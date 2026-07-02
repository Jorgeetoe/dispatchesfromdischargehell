#!/usr/bin/env python3
"""Sync published articles from Notion into Jekyll posts."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import textwrap
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, unquote

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
IMAGES_DIR = ROOT / "assets" / "img" / "posts"
LAST_SYNC_FILE = ROOT / ".last_sync"
STATE_FILE = ROOT / ".notion_sync_state.json"
ENV_FILE = ROOT / ".env"

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"
REQUEST_TIMEOUT = 30
PAGE_SIZE = 100

CATEGORY_PRIORITY = [
    ("Satirical", "dispatches"),
    ("Educational", "field-notes"),
    ("Caregiver Resource", "field-notes"),
    ("Policy Analysis", "the-machine"),
    ("Clinical Insight", "the-machine"),
    ("Personal Reflection", "persona"),
]

PUBLIC_SITE_CATEGORIES = {
    "dispatches",
    "field-notes",
    "the-machine",
    "when-it-breaks",
    "persona",
}

CORPUS_FIELD_PROPERTY_MAP = {
    "intended_reader": "Intended Reader",
    "content_tier": "Content Tier",
    "extraction_mechanism": "Extraction Mechanism",
}

SAFETY_GATE_PROPERTY_MAP = {
    "public_safety_reviewed": "Public Safety Reviewed",
    "deidentified": "Deidentified",
}

TRUTHY_PROPERTY_VALUES = {
    "approved",
    "checked",
    "complete",
    "completed",
    "done",
    "pass",
    "passed",
    "reviewed",
    "true",
    "yes",
    "y",
}

FALSY_PROPERTY_VALUES = {
    "false",
    "incomplete",
    "n",
    "no",
    "not yet",
    "pending",
    "unchecked",
}


class NotionSyncError(RuntimeError):
    """Raised for fatal sync issues."""


@dataclass
class SyncResult:
    page_id: str
    title: str
    output_path: Path
    changed: bool
    front_matter: str
    warnings: list[str]


def load_env() -> None:
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    else:
        load_dotenv()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


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

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{NOTION_API_BASE}{path}"
        response = self.session.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            raise NotionSyncError(f"Notion API error {response.status_code} on {path}: {payload}")
        return response

    def get_json(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self.request("GET", path, **kwargs).json()

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", path, data=json.dumps(payload)).json()

    def resolve_data_source_id(self, database_id: str) -> str:
        try:
            response = self.get_json(f"/data_sources/{database_id}")
            return response["id"]
        except NotionSyncError:
            database = self.get_json(f"/databases/{database_id}")
            data_sources = database.get("data_sources", [])
            if not data_sources:
                raise NotionSyncError(f"No data sources found under database {database_id}")
            return data_sources[0]["id"]

    def query_data_source(self, data_source_id: str, last_sync: str | None) -> list[dict[str, Any]]:
        filters: list[dict[str, Any]] = [
            {"property": "Content Status", "status": {"equals": "Published"}},
            {"property": "Content Type", "select": {"equals": "Article"}},
        ]

        if last_sync:
            filters.append({"timestamp": "last_edited_time", "last_edited_time": {"after": last_sync}})

        payload: dict[str, Any] = {
            "page_size": PAGE_SIZE,
            "sorts": [{"timestamp": "last_edited_time", "direction": "ascending"}],
            "filter": {"and": filters},
        }

        results: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            if cursor:
                payload["start_cursor"] = cursor
            response = self.post_json(f"/data_sources/{data_source_id}/query", payload)
            results.extend(response.get("results", []))
            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return results

    def list_block_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            params = {"page_size": PAGE_SIZE}
            if cursor:
                params["start_cursor"] = cursor
            response = self.get_json(f"/blocks/{block_id}/children", params=params)
            results.extend(response.get("results", []))
            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return results


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    value = re.sub(r"[-\s]+", "-", value).strip("-")
    return value or "untitled"


def rich_text_plain(items: list[dict[str, Any]]) -> str:
    return "".join(part.get("plain_text", "") for part in items)


def render_rich_text(items: list[dict[str, Any]]) -> str:
    pieces: list[str] = []

    for item in items:
        text = item.get("plain_text", "")
        if not text:
            continue

        if item.get("href"):
            href = item["href"]
            # Notion URL-encodes Liquid braces in link hrefs ({% ... %} and {{ ... }}).
            # Decode them so Jekyll can process the Liquid before markdown rendering.
            if "%7B" in href or "%7D" in href:
                href = unquote(href)
            text = f"[{text}]({href})"

        annotations = item.get("annotations", {})

        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"

        pieces.append(text)

    return "".join(pieces)


def markdown_quote(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def wrap_description(value: str, width: int = 72) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    wrapped = textwrap.wrap(cleaned, width=width) or [cleaned]
    return "\n".join(f"  {line}" for line in wrapped)


def truncate_description(value: str, max_length: int = 160) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) <= max_length:
        return cleaned
    truncated = cleaned[: max_length - 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return f"{truncated}…"


def extract_property(properties: dict[str, Any], name: str) -> dict[str, Any]:
    if name not in properties:
        raise NotionSyncError(f"Missing Notion property: {name}")
    return properties[name]


def extract_optional_property(properties: dict[str, Any], name: str) -> dict[str, Any] | None:
    return properties.get(name)


def get_title(properties: dict[str, Any]) -> str:
    prop = extract_property(properties, "Content Title")
    return rich_text_plain(prop.get("title", [])).strip()


def get_summary(properties: dict[str, Any]) -> str:
    prop = extract_property(properties, "Content Summary")
    if prop["type"] == "rich_text":
        return rich_text_plain(prop.get("rich_text", [])).strip()
    return ""


def get_keywords(properties: dict[str, Any]) -> str:
    prop = extract_property(properties, "SEO Keywords")
    if prop["type"] == "rich_text":
        return rich_text_plain(prop.get("rich_text", [])).strip()
    return ""


def get_repo_slug(properties: dict[str, Any]) -> str:
    prop = extract_property(properties, "Repo Slug")
    if prop["type"] == "rich_text":
        return rich_text_plain(prop.get("rich_text", [])).strip()
    return ""


def get_publication_date(properties: dict[str, Any]) -> str:
    prop = extract_property(properties, "Publication Date")
    date_value = prop.get("date") or {}
    start = date_value.get("start")
    if not start:
        raise NotionSyncError("Publication Date is required for published articles")
    return start[:10]


def ordered_multi_select_names(prop: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for option in prop.get("multi_select", []):
        name = (option.get("name") or "").strip()
        if name and name not in names:
            names.append(name)
    return names


def multi_select_names(prop: dict[str, Any]) -> set[str]:
    return {option.get("name") for option in prop.get("multi_select", []) if option.get("name")}


def optional_text_property_value(prop: dict[str, Any], property_name: str) -> tuple[str | list[str] | None, str | None]:
    prop_type = prop.get("type")

    if prop_type == "title":
        value = rich_text_plain(prop.get("title", [])).strip()
        return value or None, None

    if prop_type == "rich_text":
        value = rich_text_plain(prop.get("rich_text", [])).strip()
        return value or None, None

    if prop_type == "select":
        value = ((prop.get("select") or {}).get("name") or "").strip()
        return value or None, None

    if prop_type == "status":
        value = ((prop.get("status") or {}).get("name") or "").strip()
        return value or None, None

    if prop_type == "multi_select":
        values = ordered_multi_select_names(prop)
        return values or None, None

    if prop_type == "number":
        value = prop.get("number")
        if value is None:
            return None, None
        if isinstance(value, float) and value.is_integer():
            return str(int(value)), None
        return str(value), None

    return None, f"Unsupported Notion property type for {property_name}: {prop_type or 'unknown'}"


def parse_boolish_value(raw: str) -> bool | None:
    normalized = raw.strip().lower()
    if not normalized:
        return None
    if normalized in TRUTHY_PROPERTY_VALUES:
        return True
    if normalized in FALSY_PROPERTY_VALUES:
        return False
    return None


def optional_boolean_property_value(prop: dict[str, Any], property_name: str) -> tuple[bool | None, str | None]:
    prop_type = prop.get("type")

    if prop_type == "checkbox":
        return bool(prop.get("checkbox")), None

    if prop_type == "formula":
        formula = prop.get("formula") or {}
        formula_type = formula.get("type")
        if formula_type == "boolean":
            value = formula.get("boolean")
            return (bool(value), None) if value is not None else (None, None)
        if formula_type == "string":
            parsed = parse_boolish_value(formula.get("string") or "")
            if parsed is None:
                return None, f"Formula string for {property_name} must resolve to true/false"
            return parsed, None
        return None, f"Unsupported Notion formula result type for {property_name}: {formula_type or 'unknown'}"

    text_value, issue = optional_text_property_value(prop, property_name)
    if issue:
        return None, issue
    if isinstance(text_value, list):
        return None, f"{property_name} must be a single true/false value, not a multi-select list"
    if text_value is None:
        return None, None

    parsed = parse_boolish_value(text_value)
    if parsed is None:
        return None, f"{property_name} must resolve to true/false, got {text_value!r}"
    return parsed, None


def read_corpus_fields(
    properties: dict[str, Any],
    page_id: str,
    warnings: list[str],
    website_post: bool,
) -> dict[str, str | list[str]]:
    front_matter_fields: dict[str, str | list[str]] = {}

    for front_matter_key, property_name in CORPUS_FIELD_PROPERTY_MAP.items():
        prop = extract_optional_property(properties, property_name)
        if prop is None:
            if website_post:
                warnings.append(
                    f"{page_id}: missing Notion property {property_name}; leaving {front_matter_key} blank"
                )
            continue

        value, issue = optional_text_property_value(prop, property_name)
        if issue:
            warnings.append(f"{page_id}: {issue}; leaving {front_matter_key} blank")
            continue

        if value is None:
            continue

        front_matter_fields[front_matter_key] = value

    return front_matter_fields


def read_safety_gates(properties: dict[str, Any], website_post: bool) -> dict[str, bool]:
    front_matter_fields: dict[str, bool] = {}
    failures: list[str] = []

    for front_matter_key, property_name in SAFETY_GATE_PROPERTY_MAP.items():
        prop = extract_optional_property(properties, property_name)
        if prop is None:
            if website_post:
                failures.append(f"Missing Notion property: {property_name}")
            continue

        value, issue = optional_boolean_property_value(prop, property_name)
        if issue:
            if website_post:
                failures.append(issue)
            continue

        if value is None:
            if website_post:
                failures.append(f"{property_name} is empty")
            continue

        front_matter_fields[front_matter_key] = value

        if website_post and value is not True:
            failures.append(f"{property_name} must be true for website sync")

    if website_post and failures:
        expected = ", ".join(SAFETY_GATE_PROPERTY_MAP.values())
        details = "; ".join(failures)
        raise NotionSyncError(
            "Website sync blocked by public-safety gate. "
            f"Expected Notion properties: {expected}. {details}"
        )

    return front_matter_fields


def get_public_site_category(properties: dict[str, Any]) -> str:
    prop = extract_property(properties, "Public Site Category")
    select_value = prop.get("select") or {}
    name = (select_value.get("name") or "").strip()
    if not name:
        return ""
    if name not in PUBLIC_SITE_CATEGORIES:
        raise NotionSyncError(f"Invalid Public Site Category: {name}")
    return name


def target_platform_names(properties: dict[str, Any]) -> list[str]:
    prop = properties.get("Target Platform")
    if not prop or prop.get("type") != "multi_select":
        return []
    return ordered_multi_select_names(prop)


def is_website_post(properties: dict[str, Any]) -> bool:
    return "Website" in target_platform_names(properties)


def skip_reason_for_non_website(properties: dict[str, Any]) -> str:
    platforms = target_platform_names(properties)
    if platforms:
        return f"Target Platform does not include Website ({', '.join(platforms)})"
    return "Target Platform does not include Website"


def map_category(properties: dict[str, Any], page_id: str, warnings: list[str]) -> str:
    public_site_category = get_public_site_category(properties)
    if public_site_category:
        return public_site_category

    prop = extract_property(properties, "Content Category")
    names = multi_select_names(prop)
    for notion_name, site_name in CATEGORY_PRIORITY:
        if notion_name in names:
            inferred_category = site_name
            break
    else:
        inferred_category = "dispatches"

    if is_website_post(properties):
        warnings.append(
            f"{page_id}: published website post missing Public Site Category; "
            f"falling back to inferred category {inferred_category}"
        )

    return inferred_category


MANAGED_FRONT_MATTER_KEYS = {
    "layout",
    "title",
    "date",
    "categories",
    "description",
    "intended_reader",
    "content_tier",
    "extraction_mechanism",
    "public_safety_reviewed",
    "deidentified",
    "keywords",
    "toc",
    "redirect_from",
}


def split_front_matter(document: str) -> tuple[str | None, str]:
    if not document.startswith("---\n"):
        return None, document

    end = document.find("\n---\n", 4)
    if end == -1:
        return None, document

    front_matter = document[4:end]
    body = document[end + 5 :]
    return front_matter, body


def extract_top_level_key(line: str) -> str | None:
    if not line or line[0].isspace() or ":" not in line:
        return None
    key, _sep, _rest = line.partition(":")
    if not key or any(ch.isspace() for ch in key):
        return None
    return key


def parse_front_matter_blocks(front_matter: str | None) -> list[tuple[str, list[str]]]:
    if not front_matter:
        return []

    blocks: list[tuple[str, list[str]]] = []
    current_key: str | None = None
    current_lines: list[str] = []

    for line in front_matter.splitlines():
        key = extract_top_level_key(line)
        if key is not None:
            if current_key is not None:
                blocks.append((current_key, current_lines))
            current_key = key
            current_lines = [line]
        elif current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        blocks.append((current_key, current_lines))

    return blocks


def preserved_front_matter_blocks(path: Path | None) -> list[str]:
    if not path or not path.exists():
        return []

    front_matter, _body = split_front_matter(path.read_text())
    preserved: list[str] = []

    for key, lines in parse_front_matter_blocks(front_matter):
        if key in MANAGED_FRONT_MATTER_KEYS:
            continue
        preserved.append("\n".join(lines))

    return preserved


def existing_body(path: Path | None) -> str:
    if not path or not path.exists():
        return ""

    _front_matter, body = split_front_matter(path.read_text())
    return body.strip()


def detect_extension(url: str, content_type: str | None) -> str:
    suffix = Path(urlparse(url).path).suffix
    if suffix:
        return suffix
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if guessed:
            return guessed
    return ".bin"


def safe_filename(value: str) -> str:
    value = value.strip().replace(" ", "-")
    value = re.sub(r"[^A-Za-z0-9._-]", "", value)
    return value or "file"


def download_asset(url: str, slug: str, block_id: str, preferred_name: str | None, dry_run: bool) -> str | None:
    target_dir = IMAGES_DIR / slug
    if dry_run:
        suffix = Path(urlparse(url).path).suffix or ".bin"
        filename = safe_filename(preferred_name or f"{block_id}{suffix}")
        return f"/assets/img/posts/{slug}/{filename}"

    target_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=REQUEST_TIMEOUT, stream=True)
    response.raise_for_status()

    suffix = detect_extension(url, response.headers.get("content-type"))
    filename = preferred_name or f"{block_id}{suffix}"
    if not Path(filename).suffix:
        filename = f"{filename}{suffix}"
    filename = safe_filename(filename)

    destination = target_dir / filename
    with destination.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)

    return f"/assets/img/posts/{slug}/{filename}"


def render_block(
    block: dict[str, Any],
    client: NotionClient,
    slug: str,
    dry_run: bool,
    warnings: list[str],
    indent: int = 0,
) -> str:
    block_type = block["type"]
    data = block.get(block_type, {})
    pad = "  " * indent

    def render_children() -> str:
        if not block.get("has_children"):
            return ""
        children = client.list_block_children(block["id"])
        child_md = render_blocks(children, client, slug, dry_run, warnings, indent=indent + 1)
        return child_md.strip("\n")

    if block_type == "paragraph":
        text = render_rich_text(data.get("rich_text", []))
        return f"{pad}{text}\n\n" if text else "\n"

    if block_type == "heading_1":
        return f"{pad}## {render_rich_text(data.get('rich_text', []))}\n\n"

    if block_type == "heading_2":
        return f"{pad}### {render_rich_text(data.get('rich_text', []))}\n\n"

    if block_type == "heading_3":
        return f"{pad}#### {render_rich_text(data.get('rich_text', []))}\n\n"

    if block_type == "bulleted_list_item":
        line = f"{pad}- {render_rich_text(data.get('rich_text', []))}\n"
        children = render_children()
        if children:
            return f"{line}{children}\n"
        return f"{line}"

    if block_type == "numbered_list_item":
        line = f"{pad}1. {render_rich_text(data.get('rich_text', []))}\n"
        children = render_children()
        if children:
            return f"{line}{children}\n"
        return f"{line}"

    if block_type == "quote":
        text = render_rich_text(data.get("rich_text", []))
        return f"{markdown_quote(text)}\n\n" if text else "\n"

    if block_type == "code":
        language = data.get("language") or ""
        code_text = rich_text_plain(data.get("rich_text", []))
        return f"```{language}\n{code_text}\n```\n\n"

    if block_type == "callout":
        icon = block.get("callout", {}).get("icon", {})
        icon_text = ""
        if icon.get("type") == "emoji":
            icon_text = f"{icon['emoji']} "
        text = render_rich_text(data.get("rich_text", []))
        body = markdown_quote(f"{icon_text}{text}".strip())
        children = render_children()
        if children:
            body = f"{body}\n{markdown_quote(children)}"
        return f"{body}\n\n"

    if block_type == "divider":
        return "---\n\n"

    if block_type == "toggle":
        summary = render_rich_text(data.get("rich_text", []))
        children = render_children()
        details = [f"<details><summary>{summary}</summary>", ""]
        if children:
            details.append(children.strip())
            details.append("")
        details.append("</details>")
        return "\n".join(details) + "\n\n"

    if block_type == "image":
        image_data = data
        caption = render_rich_text(image_data.get("caption", []))
        url = None
        if image_data.get("type") == "file":
            url = image_data.get("file", {}).get("url")
        elif image_data.get("type") == "external":
            url = image_data.get("external", {}).get("url")
        if not url:
            warnings.append(f"{block['id']}: image block has no usable URL")
            return "<!-- Unsupported Notion image block with no URL -->\n\n"
        preferred_name = None
        parsed = urlparse(url)
        if parsed.path:
            preferred_name = Path(parsed.path).name
        try:
            local_path = download_asset(url, slug, block["id"], preferred_name, dry_run)
        except requests.RequestException as exc:
            warnings.append(f"{block['id']}: image download failed for {url} ({exc})")
            return f"<!-- Notion image download failed: {url} ({exc}) -->\n\n"
        alt = caption or slug.replace("-", " ")
        return f"![{alt}]({local_path})\n\n"

    if block_type in {"file", "pdf", "video", "audio"}:
        file_data = data
        url = None
        if file_data.get("type") == "file":
            url = file_data.get("file", {}).get("url")
        elif file_data.get("type") == "external":
            url = file_data.get("external", {}).get("url")
        caption = render_rich_text(file_data.get("caption", []))
        label = caption or block_type.capitalize()
        return f"[{label}]({url})\n\n" if url else f"<!-- Unsupported Notion {block_type} block -->\n\n"

    if block_type == "bookmark":
        url = data.get("url")
        return f"{url}\n\n" if url else ""

    if block_type == "embed":
        url = data.get("url")
        return f"{url}\n\n" if url else ""

    warnings.append(f"{block['id']}: unsupported block type {block_type}")
    return f"<!-- Unsupported Notion block type: {block_type} -->\n\n"


def render_blocks(
    blocks: list[dict[str, Any]],
    client: NotionClient,
    slug: str,
    dry_run: bool,
    warnings: list[str],
    indent: int = 0,
) -> str:
    rendered = [render_block(block, client, slug, dry_run, warnings, indent=indent) for block in blocks]
    text = "".join(rendered)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def build_front_matter(
    *,
    title: str,
    date: str,
    category: str,
    description: str,
    corpus_fields: dict[str, str | list[str]],
    safety_gates: dict[str, bool],
    keywords: str,
    redirect_from: str,
    preserved_blocks: list[str],
) -> str:
    lines = [
        "---",
        "layout: post",
        f"title: {yaml_quote(title)}",
        f"date: {date}",
        f"categories: [{category}]",
        "description: >-",
        wrap_description(description),
    ]

    for key in ("intended_reader", "content_tier", "extraction_mechanism"):
        value = corpus_fields.get(key)
        if not value:
            continue
        if isinstance(value, list):
            rendered = ", ".join(yaml_quote(item) for item in value)
            lines.append(f"{key}: [{rendered}]")
        else:
            lines.append(f"{key}: {yaml_quote(value)}")

    for key in ("public_safety_reviewed", "deidentified"):
        value = safety_gates.get(key)
        if value is None:
            continue
        lines.append(f"{key}: {'true' if value else 'false'}")

    if preserved_blocks:
        lines.extend(preserved_blocks)
    if keywords:
        lines.append(f"keywords: {yaml_quote(keywords)}")
    lines.extend(
        [
            "toc: true",
            "redirect_from:",
            f"  - {redirect_from}",
            "---",
        ]
    )
    return "\n".join(lines) + "\n"


def build_markdown(front_matter: str, body: str) -> str:
    body = body.strip() + "\n"
    return f"{front_matter}\n{body}"


def sync_page(
    page: dict[str, Any],
    client: NotionClient,
    state: dict[str, str],
    dry_run: bool,
) -> SyncResult:
    properties = page["properties"]
    page_id = page["id"]
    title = get_title(properties)
    publication_date = get_publication_date(properties)
    summary = get_summary(properties)
    description = truncate_description(summary or title)
    keywords = get_keywords(properties)
    repo_slug = get_repo_slug(properties)
    slug = slugify(title)

    # Use repo_slug if provided (user control), otherwise generate from title.
    # repo_slug already includes publication date (YYYY-MM-DD-slug format).
    # Only prepend date to auto-generated slugs.
    if repo_slug:
        filename_stem = repo_slug
        # Extract slug-only part from repo_slug for orphan cleanup pattern
        slug_part = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", repo_slug)
    else:
        filename_stem = f"{publication_date}-{slug}"
        slug_part = slug
    filename = f"{filename_stem}.md"
    output_path = POSTS_DIR / filename
    redirect_from = f"/blog/posts/{filename_stem}.html"
    warnings: list[str] = []

    # ===== VALIDATION GUARD: Repo Slug + Publication Date consistency =====
    # For existing files: check if front-matter date would change (URL move)
    # For new files: verify repo_slug prefix matches publication_date
    if repo_slug:
        # Extract date prefix from repo_slug (should be YYYY-MM-DD)
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})-", repo_slug)
        if not date_match:
            # Repo slug has no valid date prefix
            raise NotionSyncError(
                f"Invalid Repo Slug format (missing YYYY-MM-DD prefix): {repo_slug}"
            )
        repo_slug_date = date_match.group(1)

        # Check if file already exists
        if output_path.exists():
            # Existing file: check if front-matter date would change (URL move warning)
            existing_front_matter, _ = split_front_matter(output_path.read_text())
            if existing_front_matter:
                existing_blocks = parse_front_matter_blocks(existing_front_matter)
                for key, lines in existing_blocks:
                    if key == "date":
                        existing_date_line = "\n".join(lines)
                        existing_date = existing_date_line.split("date:")[1].strip() if "date:" in existing_date_line else None
                        if existing_date and existing_date != publication_date:
                            warnings.append(
                                f"{page_id}: URL move detected for {title} — "
                                f"front-matter date changing from {existing_date} to {publication_date}"
                            )
        else:
            # New file: repo_slug prefix must match publication_date
            if repo_slug_date != publication_date:
                raise NotionSyncError(
                    f"Repo Slug date prefix {repo_slug_date} does not match Publication Date {publication_date}"
                )
    else:
        # No repo_slug provided
        try:
            publication_date  # Will raise if not available
        except NotionSyncError:
            raise NotionSyncError(
                f"Cannot generate filename: no Repo Slug and no Publication Date"
            )
    # ===== END VALIDATION GUARD =====

    # Clean up stale files: same slug but different (or missing) date prefix.
    # Prevents duplicates when publication_date changes, or when files from
    # before this fix (which lacked date prefixes) are re-synced.
    # Only clean up during actual sync, not dry-run.

    # Strict pattern: match only YYYY-MM-DD-{slug}.md to avoid greedy glob.
    date_slug_pattern = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(slug_part)}\.md$")
    for candidate in POSTS_DIR.iterdir():
        if (candidate.is_file()
            and date_slug_pattern.match(candidate.name)
            and candidate != output_path):
            if not dry_run:
                candidate.unlink()
                warnings.append(f"{page_id}: removed stale duplicate {candidate.name}")
            else:
                warnings.append(f"{page_id}: would remove stale duplicate {candidate.name}")

    # Also check for bare slug (no date prefix) — legacy files from before this fix.
    bare_slug_file = POSTS_DIR / f"{slug_part}.md"
    if bare_slug_file.exists() and bare_slug_file != output_path:
        if not dry_run:
            bare_slug_file.unlink()
            warnings.append(f"{page_id}: removed Jekyll-invalid file {bare_slug_file.name} (missing date prefix)")
        else:
            warnings.append(f"{page_id}: would remove Jekyll-invalid file {bare_slug_file.name} (missing date prefix)")
    website_post = is_website_post(properties)
    # Check safety gates BEFORE orphan cleanup to avoid deleting files for gated pages
    safety_gates = read_safety_gates(properties, website_post)
    category = map_category(properties, page_id, warnings)
    corpus_fields = read_corpus_fields(properties, page_id, warnings, website_post)

    previous_path = Path(state[page_id]) if page_id in state else None
    source_path_for_preserve = output_path if output_path.exists() else previous_path
    preserved_blocks = preserved_front_matter_blocks(source_path_for_preserve)

    blocks = client.list_block_children(page_id)
    body = render_blocks(blocks, client, slug, dry_run=dry_run, warnings=warnings)
    if not body.strip():
        fallback_body = existing_body(source_path_for_preserve)
        if fallback_body:
            body = fallback_body + "\n"
            warnings.append(f"{page_id}: preserved existing body because Notion page content is empty")
    front_matter = build_front_matter(
        title=title,
        date=publication_date,
        category=category,
        description=description,
        corpus_fields=corpus_fields,
        safety_gates=safety_gates,
        keywords=keywords,
        redirect_from=redirect_from,
        preserved_blocks=preserved_blocks,
    )
    document = build_markdown(
        front_matter,
        body,
    )
    if previous_path and previous_path != output_path and previous_path.exists() and not dry_run:
        previous_path.unlink()

    changed = True
    if output_path.exists():
        changed = output_path.read_text() != document

    if not dry_run:
        POSTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_text(document)
        state[page_id] = str(output_path.relative_to(ROOT))

    return SyncResult(
        page_id=page_id,
        title=title,
        output_path=output_path,
        changed=changed,
        front_matter=front_matter,
        warnings=warnings,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync published articles from Notion into Jekyll posts.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing files.")
    parser.add_argument("--full-sync", action="store_true", help="Ignore .last_sync and sync all published posts.")
    parser.add_argument("--verbose", action="store_true", help="Print extra sync details.")
    parser.add_argument(
        "--title",
        action="append",
        default=[],
        help="Only sync published articles whose Content Title exactly matches this value. Repeat for multiple titles.",
    )
    parser.add_argument(
        "--page-id",
        action="append",
        default=[],
        help="Only sync the published article with this Notion page ID. Repeat for multiple page IDs.",
    )
    parser.add_argument(
        "--no-state-update",
        action="store_true",
        help="Write posts without updating .last_sync or .notion_sync_state.json.",
    )
    return parser.parse_args()


def filter_pages(
    pages: list[dict[str, Any]],
    selected_titles: list[str],
    selected_page_ids: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    if not selected_titles and not selected_page_ids:
        return pages, []

    wanted_titles = set(selected_titles)
    wanted_ids = set(selected_page_ids)
    matched_titles: set[str] = set()
    matched_ids: set[str] = set()
    filtered: list[dict[str, Any]] = []

    for page in pages:
        page_id = page["id"]
        title = get_title(page["properties"])
        if page_id in wanted_ids or title in wanted_titles:
            filtered.append(page)
            if page_id in wanted_ids:
                matched_ids.add(page_id)
            if title in wanted_titles:
                matched_titles.add(title)

    missing = [f"title:{title}" for title in selected_titles if title not in matched_titles]
    missing.extend(f"page_id:{page_id}" for page_id in selected_page_ids if page_id not in matched_ids)
    return filtered, missing


def main() -> int:
    args = parse_args()
    load_env()

    notion_token = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")

    if not notion_token or not notion_database_id:
        print("NOTION_API_KEY and NOTION_DATABASE_ID are required.", file=sys.stderr)
        return 1

    client = NotionClient(notion_token)
    state = read_json(STATE_FILE, {})
    targeted_sync = bool(args.title or args.page_id)
    last_sync = None if (args.full_sync or targeted_sync) else (LAST_SYNC_FILE.read_text().strip() if LAST_SYNC_FILE.exists() else None)

    data_source_id = client.resolve_data_source_id(notion_database_id)
    pages = client.query_data_source(data_source_id, last_sync)
    pages, missing_targets = filter_pages(pages, args.title, args.page_id)

    if not pages:
        print("No published Notion articles to sync.")
        if not args.dry_run:
            if not args.no_state_update:
                LAST_SYNC_FILE.write_text(now_iso() + "\n")
        return 0

    for missing in missing_targets:
        print(f"[warn] Requested target not found in published articles: {missing}", file=sys.stderr)

    results: list[SyncResult] = []
    failures: list[str] = []
    skipped_non_website = 0

    for page in pages:
        properties = page["properties"]
        try:
            title = get_title(properties) or page["id"]
        except NotionSyncError:
            title = page["id"]

        if not is_website_post(properties):
            skipped_non_website += 1
            print(f"[skip] {title}: {skip_reason_for_non_website(properties)}")
            continue

        try:
            result = sync_page(page, client, state, dry_run=args.dry_run)
        except NotionSyncError as exc:
            message = f"[error] {title}: {exc}"
            print(message, file=sys.stderr)
            failures.append(message)
            continue
        results.append(result)
        status = "update" if result.changed else "unchanged"
        print(f"[{status}] {result.title} -> {result.output_path.relative_to(ROOT)}")
        if args.dry_run:
            print(result.front_matter.rstrip())
        if args.verbose:
            print(f"  page_id: {result.page_id}")
        for warning in result.warnings:
            print(f"  warning: {warning}")

    if args.dry_run:
        print(f"Dry run complete. {len(results)} posts would be processed.")
        if skipped_non_website:
            print(f"Skipped {skipped_non_website} non-website page(s).")
        if failures:
            print(f"Skipped {len(failures)} invalid page(s).", file=sys.stderr)
        return 1 if failures else 0

    if not args.no_state_update:
        write_json(STATE_FILE, state)
        LAST_SYNC_FILE.write_text(now_iso() + "\n")
    print(f"Sync complete. Processed {len(results)} posts.")
    if skipped_non_website:
        print(f"Skipped {skipped_non_website} non-website page(s).")
    if failures:
        print(f"Skipped {len(failures)} invalid page(s).", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
