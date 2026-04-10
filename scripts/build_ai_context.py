#!/usr/bin/env python3
"""Build a deterministic AI context packet for this repository."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
TABS_DIR = ROOT / "_tabs"
DOCS_DIR = ROOT / "docs"

DEFAULT_DOCS = [
    "build-spec.md",
    "editorial-audit.md",
    "notion-integration-prep.md",
]

DEFAULT_TABS = [
    "about.md",
    "telos.md",
    "start-here.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a compact repo context packet for AI-assisted workflows."
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--posts-limit",
        type=int,
        default=12,
        help="Maximum number of posts to include in the rendered output.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file to write. Defaults to stdout.",
    )
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text

    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text

    return text[4:end], text[end + 5 :]


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("'\"") for part in inner.split(",")]
    return value


def parse_front_matter(front_matter: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    lines = front_matter.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue

        if ":" not in line:
            i += 1
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value in {">", ">-", "|", "|-"}:
            i += 1
            block: list[str] = []
            while i < len(lines):
                next_line = lines[i]
                if next_line.startswith("  ") or not next_line.strip():
                    block.append(next_line[2:] if next_line.startswith("  ") else "")
                    i += 1
                    continue
                break
            result[key] = "\n".join(block).strip()
            continue

        if not value:
            i += 1
            items: list[str] = []
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                if stripped.startswith("- "):
                    items.append(stripped[2:].strip().strip("'\""))
                    i += 1
                    continue
                if next_line.startswith("  ") and stripped:
                    items.append(stripped.strip("'\""))
                    i += 1
                    continue
                if not stripped:
                    i += 1
                    continue
                break
            result[key] = items if items else ""
            continue

        result[key] = parse_scalar(value)
        i += 1

    return result


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^>\s?", "", text, flags=re.M)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"[*_~]", "", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


def first_paragraph(body: str) -> str:
    plain = strip_markdown(body)
    for chunk in plain.split("\n\n"):
        chunk = chunk.strip()
        if chunk:
            return re.sub(r"\s+", " ", chunk)
    return ""


def extract_headings(body: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"^#{1,6}\s+(.+)$", body, flags=re.M)]


def summarize_file(path: Path) -> dict[str, Any]:
    text = read_text(path)
    front_matter_text, body = split_front_matter(text)
    front_matter = parse_front_matter(front_matter_text)
    headings = extract_headings(body)
    title = str(front_matter.get("title") or (headings[0] if headings else path.stem))
    description = str(front_matter.get("description") or front_matter.get("excerpt") or "").strip()
    if not description:
        description = first_paragraph(body)

    categories = front_matter.get("categories", [])
    if isinstance(categories, str):
        categories = [categories] if categories else []

    keywords = front_matter.get("keywords", "")
    if isinstance(keywords, str):
        keywords = [part.strip() for part in keywords.split(",") if part.strip()]

    return {
        "path": str(path.relative_to(ROOT)),
        "title": title,
        "description": description,
        "date": front_matter.get("date", ""),
        "layout": front_matter.get("layout", ""),
        "categories": categories,
        "keywords": keywords,
        "headings": headings[:8],
        "first_paragraph": first_paragraph(body),
    }


def build_packet(posts_limit: int) -> dict[str, Any]:
    tabs = [summarize_file(TABS_DIR / name) for name in DEFAULT_TABS if (TABS_DIR / name).exists()]
    docs = [summarize_file(DOCS_DIR / name) for name in DEFAULT_DOCS if (DOCS_DIR / name).exists()]

    posts = [summarize_file(path) for path in sorted(POSTS_DIR.glob("*.md"))]
    posts.sort(key=lambda item: (item.get("date", ""), item["path"]), reverse=True)

    category_counter: Counter[str] = Counter()
    for post in posts:
        category_counter.update(post.get("categories", []))

    return {
        "generated_at": now_iso(),
        "project": {
            "name": "Dispatches from Discharge Hell",
            "repo_root": str(ROOT),
            "site_type": "content-first Jekyll publication on Chirpy",
            "primary_use_case": "Research-backed editorial publishing on catastrophic care, discharge mechanics, and payer behavior",
        },
        "core_context": {
            "tabs": tabs,
            "docs": docs,
        },
        "inventory": {
            "post_count": len(posts),
            "tab_count": len(list(TABS_DIR.glob("*.md"))),
            "doc_count": len(list(DOCS_DIR.glob("*.md"))),
            "categories": dict(category_counter.most_common()),
        },
        "posts": posts[: max(posts_limit, 0)],
    }


def render_markdown(packet: dict[str, Any]) -> str:
    lines: list[str] = []
    project = packet["project"]
    inventory = packet["inventory"]

    lines.append("# AI Context Packet")
    lines.append("")
    lines.append(f"- Generated: `{packet['generated_at']}`")
    lines.append(f"- Project: `{project['name']}`")
    lines.append(f"- Site type: {project['site_type']}")
    lines.append(f"- Primary use case: {project['primary_use_case']}")
    lines.append("")
    lines.append("## Core Context")
    lines.append("")

    for section_name in ("tabs", "docs"):
        items = packet["core_context"][section_name]
        label = "Tabs" if section_name == "tabs" else "Docs"
        lines.append(f"### {label}")
        lines.append("")
        for item in items:
            lines.append(f"- `{item['path']}`")
            lines.append(f"  - Title: {item['title']}")
            if item["description"]:
                lines.append(f"  - Summary: {item['description']}")
        lines.append("")

    lines.append("## Inventory")
    lines.append("")
    lines.append(f"- Posts: {inventory['post_count']}")
    lines.append(f"- Tabs: {inventory['tab_count']}")
    lines.append(f"- Docs: {inventory['doc_count']}")
    lines.append("- Categories:")
    for category, count in inventory["categories"].items():
        lines.append(f"  - `{category}`: {count}")
    lines.append("")
    lines.append("## Recent / Included Posts")
    lines.append("")

    for post in packet["posts"]:
        category_text = ", ".join(post["categories"]) if post["categories"] else "uncategorized"
        lines.append(f"- `{post['path']}`")
        lines.append(f"  - Title: {post['title']}")
        if post["date"]:
            lines.append(f"  - Date: {post['date']}")
        lines.append(f"  - Categories: {category_text}")
        if post["description"]:
            lines.append(f"  - Summary: {post['description']}")
        if post["headings"]:
            lines.append(f"  - Headings: {', '.join(post['headings'][:5])}")
    lines.append("")

    return "\n".join(lines)


def emit(text: str, output: Path | None) -> None:
    if output:
        output.write_text(text, encoding="utf-8")
        return
    print(text)


def main() -> int:
    args = parse_args()
    packet = build_packet(args.posts_limit)

    if args.format == "json":
        rendered = json.dumps(packet, indent=2, ensure_ascii=False)
    else:
        rendered = render_markdown(packet)

    emit(rendered + ("\n" if not rendered.endswith("\n") else ""), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
