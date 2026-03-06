#!/usr/bin/env python3

import os
import re
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime

# Simple HTML to Markdown converter
class HTMLToMarkdownParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.output = []
        self.tag_stack = []
        self.is_code = False
        self.is_list = False
        self.list_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'h2':
            self.output.append('\n## ')
        elif tag == 'h3':
            self.output.append('\n### ')
        elif tag == 'p':
            if self.output and self.output[-1] != '\n':
                self.output.append('\n')
        elif tag == 'strong' or tag == 'b':
            self.output.append('**')
        elif tag == 'em' or tag == 'i':
            self.output.append('*')
        elif tag == 'a':
            self.output.append('[')
        elif tag == 'ul':
            self.is_list = True
            self.list_depth += 1
            self.output.append('\n')
        elif tag == 'li':
            indent = '  ' * (self.list_depth - 1)
            self.output.append(f'{indent}* ')
        elif tag == 'blockquote':
            self.output.append('\n> ')
        elif tag == 'code':
            self.is_code = True
            self.output.append('`')
        elif tag == 'pre':
            self.output.append('\n```\n')
        elif tag == 'br':
            self.output.append('\n')

        self.tag_stack.append((tag, attrs_dict))

    def handle_endtag(self, tag):
        if tag == 'h2' or tag == 'h3':
            self.output.append('\n')
        elif tag == 'p':
            self.output.append('\n')
        elif tag == 'strong' or tag == 'b':
            self.output.append('**')
        elif tag == 'em' or tag == 'i':
            self.output.append('*')
        elif tag == 'a':
            if self.tag_stack and self.tag_stack[-1][0] == 'a':
                href = self.tag_stack[-1][1].get('href', '')
                self.output.append(f']({href})')
        elif tag == 'ul':
            self.list_depth -= 1
            if self.list_depth == 0:
                self.is_list = False
            self.output.append('\n')
        elif tag == 'li':
            self.output.append('\n')
        elif tag == 'blockquote':
            self.output.append('\n')
        elif tag == 'code':
            self.is_code = False
            self.output.append('`')
        elif tag == 'pre':
            self.output.append('\n```\n')

        if self.tag_stack and self.tag_stack[-1][0] == tag:
            self.tag_stack.pop()

    def handle_data(self, data):
        if data.strip():
            self.output.append(data)

    def get_markdown(self):
        text = ''.join(self.output)
        # Clean up multiple newlines
        text = re.sub(r'\n\n+', '\n\n', text)
        # Clean up whitespace
        text = text.strip()
        return text


def extract_meta_content(html):
    """Extract content from meta tags and other HTML elements"""

    # Extract title
    title_match = re.search(r'<title>([^|]+)\|', html)
    title = title_match.group(1).strip() if title_match else "Untitled"

    # Extract meta description
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
    description = desc_match.group(1) if desc_match else ""

    # Extract publish date
    date_match = re.search(r'<time datetime="([^"]+)"', html)
    publish_date = date_match.group(1) if date_match else datetime.now().isoformat()

    # Extract article body
    content_match = re.search(r'<div class="article-content">(.*?)</div>', html, re.DOTALL)
    article_html = content_match.group(1) if content_match else ""

    # Extract category from schema markup
    category_match = re.search(r'"keywords":\s*"([^"]+)"', html)
    category = category_match.group(1) if category_match else "Field Notes"

    # Try to extract category from category tag
    cat_match = re.search(r'<span class="category-tag"[^>]*>([^<]+)</span>', html)
    if cat_match:
        category = cat_match.group(1).strip()

    # Extract related posts
    related = []
    related_matches = re.findall(r'/blog/posts/([^"]+)\.html', html)
    for match in related_matches[:3]:  # Limit to 3 related posts
        related.append(f"/blog/posts/{match}/")

    # Extract series info
    series = ""
    series_order = 0
    series_match = re.search(r'data-series-part="(\d+)"', html)
    if series_match:
        series = "Dispatches from Discharge Hell"
        series_order = int(series_match.group(1))

    return {
        'title': title,
        'description': description,
        'date': publish_date,
        'content': article_html,
        'category': category,
        'related': related,
        'series': series,
        'series_order': series_order
    }


def html_to_markdown(html_content):
    """Convert HTML to Markdown"""
    parser = HTMLToMarkdownParser()
    try:
        parser.feed(html_content)
        return parser.get_markdown()
    except:
        return html_content


def convert_posts():
    """Convert all HTML posts to Markdown"""

    posts_dir = Path('/Users/jorgearenivar/DispatchesFromDischargeHell/site/blog/posts')
    output_dir = Path('/Users/jorgearenivar/DispatchesFromDischargeHell/hugo/content/blog/posts')
    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = sorted(posts_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML post files")

    converted = 0
    errors = []

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Extract metadata
            meta = extract_meta_content(html_content)

            # Convert HTML to Markdown
            markdown_content = html_to_markdown(meta['content'])

            # Generate front matter
            date_obj = datetime.fromisoformat(meta['date'].replace('Z', '+00:00'))
            date_str = date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')

            # Create filename from original
            base_name = html_file.stem
            markdown_filename = f"{base_name}.md"

            # Build YAML front matter
            front_matter = f"""---
title: "{meta['title'].replace('"', '\\"')}"
date: {date_str}
categories: ["{meta['category']}"]
"""
            if meta['series']:
                front_matter += f"""series: "{meta['series']}"
series_order: {meta['series_order']}
"""
            if meta['description']:
                front_matter += f"""description: "{meta['description'].replace('"', '\\"')}"
"""
            if meta['related']:
                related_str = ', '.join(f'"{r}"' for r in meta['related'])
                front_matter += f"""related: [{related_str}]
"""
            front_matter += "---\n\n"

            # Write markdown file
            markdown_path = output_dir / markdown_filename
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(front_matter)
                f.write(markdown_content)

            print(f"✓ Converted: {base_name}")
            converted += 1

        except Exception as e:
            error_msg = f"✗ Error converting {html_file.name}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)

    print(f"\n--- Summary ---")
    print(f"Successfully converted: {converted}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  {error}")


if __name__ == '__main__':
    convert_posts()
