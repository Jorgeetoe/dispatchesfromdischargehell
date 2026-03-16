#!/usr/bin/env python3
"""Export the canonical Build Spec page from Notion into docs/build-spec.md."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
OUTPUT_PATH = ROOT / "docs" / "build-spec.md"

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"
REQUEST_TIMEOUT = 30
PAGE_SIZE = 100
DEFAULT_BUILD_SPEC_PAGE_ID = "9faed86b-0e4b-45f3-a045-46b7428fdca1"


class NotionExportError(RuntimeError):
    """Raised for export failures."""


def load_env() -> None:
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    else:
        load_dotenv()


class NotionClient:
    def __init__(self, token: str) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            }
        )

    def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.session.request(method, f"{NOTION_API_BASE}{path}", timeout=REQUEST_TIMEOUT, **kwargs)
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            raise NotionExportError(f"Notion API error {response.status_code} on {path}: {payload}")
        return response.json()

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{page_id}")

    def list_block_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            params: dict[str, Any] = {"page_size": PAGE_SIZE}
            if cursor:
                params["start_cursor"] = cursor
            response = self.request("GET", f"/blocks/{block_id}/children", params=params)
            results.extend(response.get("results", []))
            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return results


def rich_text_plain(items: list[dict[str, Any]]) -> str:
    return "".join(part.get("plain_text", "") for part in items)


def render_rich_text(items: list[dict[str, Any]]) -> str:
    pieces: list[str] = []

    for item in items:
        text = item.get("plain_text", "")
        if not text:
            continue

        href = item.get("href")
        annotations = item.get("annotations", {})

        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"

        if href:
            text = f"[{text}]({href})"

        pieces.append(text)

    return "".join(pieces)


def indent_block(text: str, spaces: int) -> str:
    prefix = " " * spaces
    lines = text.splitlines()
    return "\n".join(f"{prefix}{line}" if line else "" for line in lines)


def markdown_quote(text: str) -> str:
    return "\n".join("> " + line if line else ">" for line in text.splitlines())


def get_block_title(page: dict[str, Any]) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            return rich_text_plain(prop.get("title", []))
    return "Build Spec"


def render_table(block: dict[str, Any], client: NotionClient) -> str:
    rows = client.list_block_children(block["id"])
    table_rows: list[list[str]] = []

    for row in rows:
        if row.get("type") != "table_row":
            continue
        cells = row["table_row"].get("cells", [])
        table_rows.append([render_rich_text(cell) for cell in cells])

    if not table_rows:
        return ""

    width = max(len(row) for row in table_rows)
    normalized = [row + [""] * (width - len(row)) for row in table_rows]
    has_header = block.get("table", {}).get("has_column_header", False)

    if has_header:
        header = normalized[0]
        body_rows = normalized[1:]
    else:
        header = normalized[0]
        body_rows = normalized[1:]

    separator = ["---"] * width
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]

    for row in body_rows:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines) + "\n\n"


def render_children(block: dict[str, Any], client: NotionClient, indent: int = 0) -> str:
    if not block.get("has_children"):
        return ""
    children = client.list_block_children(block["id"])
    return render_blocks(children, client, indent=indent)


def render_block(block: dict[str, Any], client: NotionClient, indent: int = 0) -> str:
    block_type = block["type"]
    data = block.get(block_type, {})
    pad = " " * indent

    if block_type == "paragraph":
        text = render_rich_text(data.get("rich_text", []))
        return f"{pad}{text}\n\n" if text else "\n"

    if block_type == "heading_1":
        return f"{pad}# {render_rich_text(data.get('rich_text', []))}\n\n"

    if block_type == "heading_2":
        return f"{pad}## {render_rich_text(data.get('rich_text', []))}\n\n"

    if block_type == "heading_3":
        return f"{pad}### {render_rich_text(data.get('rich_text', []))}\n\n"

    if block_type == "bulleted_list_item":
        line = f"{pad}- {render_rich_text(data.get('rich_text', []))}\n"
        children = render_children(block, client, indent=indent + 2)
        return f"{line}{children}" + ("\n" if children else "")

    if block_type == "numbered_list_item":
        line = f"{pad}1. {render_rich_text(data.get('rich_text', []))}\n"
        children = render_children(block, client, indent=indent + 3)
        return f"{line}{children}" + ("\n" if children else "")

    if block_type == "quote":
        text = render_rich_text(data.get("rich_text", []))
        return f"{markdown_quote(text)}\n\n" if text else "\n"

    if block_type == "code":
        language = data.get("language") or ""
        code_text = rich_text_plain(data.get("rich_text", []))
        return f"```{language}\n{code_text}\n```\n\n"

    if block_type == "callout":
        icon = data.get("icon") or block.get("callout", {}).get("icon", {})
        icon_text = f"{icon.get('emoji')} " if icon.get("type") == "emoji" else ""
        text = render_rich_text(data.get("rich_text", []))
        lines = [f"> {icon_text}{text}".rstrip()]
        children = render_children(block, client, indent=0).strip()
        if children:
            lines.append(">")
            for child_line in children.splitlines():
                lines.append("> " + child_line if child_line else ">")
        return "\n".join(lines) + "\n\n"

    if block_type == "divider":
        return "---\n\n"

    if block_type == "toggle":
        summary = render_rich_text(data.get("rich_text", []))
        children = render_children(block, client, indent=0).strip()
        lines = [f"<details><summary>{summary}</summary>", ""]
        if children:
            lines.append(children)
            lines.append("")
        lines.append("</details>")
        return "\n".join(lines) + "\n\n"

    if block_type == "table":
        return render_table(block, client)

    if block_type == "bookmark":
        url = data.get("url", "")
        return f"{url}\n\n" if url else "\n"

    if block_type == "child_page":
        title = data.get("title", "")
        return f"## {title}\n\n" if title else "\n"

    return f"<!-- Unsupported Notion block type: {block_type} -->\n\n"


def render_blocks(blocks: list[dict[str, Any]], client: NotionClient, indent: int = 0) -> str:
    rendered = "".join(render_block(block, client, indent=indent) for block in blocks)
    rendered = re.sub(r"\n{3,}", "\n\n", rendered)
    return rendered


def clean_markdown(markdown: str) -> str:
    markdown = markdown.replace("****`", "**`").replace("`****", "`**")
    markdown = re.sub(r"\n>\n  ", "\n>\n> ", markdown)
    markdown = re.sub(r"\n> +-\s", "\n> - ", markdown)
    markdown = re.sub(r"\n> \s+- ", "\n> - ", markdown)
    markdown = re.sub(r"\n  - ", "\n> - ", markdown)
    markdown = re.sub(r"\n>\s+\*\*Immediate priority:\*\*", "\n> **Immediate priority:**", markdown)
    markdown = re.sub(r"\n-{4,}\n", "\n---\n", markdown)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip() + "\n"


def export_build_spec(page_id: str, output_path: Path) -> str:
    load_env()
    token = os.getenv("NOTION_API_KEY")
    if not token:
        raise NotionExportError("NOTION_API_KEY is required.")

    client = NotionClient(token)
    page = client.get_page(page_id)
    title = get_block_title(page).strip() or "Build Spec"
    blocks = client.list_block_children(page_id)

    markdown = f"# {title}\n\n" + render_blocks(blocks, client).strip() + "\n"
    markdown = clean_markdown(markdown)
    output_path.write_text(markdown)
    return markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the Build Spec page from Notion to docs/build-spec.md.")
    parser.add_argument("--page-id", default=DEFAULT_BUILD_SPEC_PAGE_ID, help="Notion page ID for the Build Spec page.")
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output markdown path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    export_build_spec(args.page_id, Path(args.output))
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
