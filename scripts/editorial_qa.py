#!/usr/bin/env python3
"""Run basic editorial QA checks against Dispatches markdown posts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
VALID_CATEGORIES = {
    "dispatches",
    "field-notes",
    "the-machine",
    "when-it-breaks",
    "persona",
}
RESEARCH_HINTS = (
    "study",
    "research",
    "medicare",
    "cms",
    "kaiser",
    "jama",
    "harvard",
    "report",
    "appeal",
    "denial rate",
)
CORNERSTONE_LINK_HINTS = (
    "/start-here/",
    "/telos/",
    "/categories/",
    "post_url 2024-01-01-dispatches-from-discharge-hell-25-part-series",
    "post_url 2026-02-15-what-doc-rehab-actually-does",
    "post_url 2026-02-15-rehabilitation-vs-catastrophic-care",
)
FAMILY_UTILITY_HINTS = (
    "what to ask",
    "what to watch for",
    "what this means",
    "next step",
    "next steps",
    "red flag",
    "red flags",
    "what to do",
    "what to document",
    "what families should",
    "if you're reading this",
)
MECHANISM_HINTS = (
    "the system",
    "insurance",
    "payer",
    "authorization",
    "prior auth",
    "medical necessity",
    "throughput",
    "benefit",
    "coverage",
    "discharge",
    "staffing",
    "home health",
    "snf",
    "ltac",
    "incentive",
    "utilization",
)
DEBUGGER_HINTS = (
    "where you are",
    "what's happening",
    "what is happening",
    "what to ask next",
    "what to do today",
    "what to document",
    "red flags",
    "red flag",
)
FAMILY_CONFUSION_HINTS = (
    "family",
    "caregiver",
    "wife",
    "husband",
    "daughter",
    "son",
    "mom",
    "dad",
    "home health",
    "snf",
    "ltac",
    "denial",
    "discharge",
)


@dataclass
class Finding:
    severity: str
    code: str
    message: str


@dataclass
class QaResult:
    path: str
    findings: list[Finding]
    word_count: int
    internal_link_count: int
    heading_count: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run editorial QA checks on Dispatches posts.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", type=Path, help="Single markdown file to check.")
    group.add_argument("--all", action="store_true", help="Check all posts in _posts/.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


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
    if value in {"true", "false"}:
        return value == "true"
    return value


def parse_front_matter(front_matter: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    lines = front_matter.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
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


def count_words(body: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", body))


def count_internal_links(body: str) -> int:
    patterns = (
        r"\{%\s*post_url\s+[^%]+%\}",
        r"\{\{\s*'/.+?'\s*\|\s*relative_url\s*\}\}",
        r"\[[^\]]+\]\((/[^)]+)\)",
    )
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, body))
    return total


def count_headings(body: str) -> int:
    return len(re.findall(r"^#{1,6}\s+.+$", body, flags=re.M))


def has_research_hints(body: str) -> bool:
    lowered = body.lower()
    return any(hint in lowered for hint in RESEARCH_HINTS)


def has_any_hint(text: str, hints: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(hint in lowered for hint in hints)


def count_hint_hits(text: str, hints: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(1 for hint in hints if hint in lowered)


def check_post(path: Path) -> QaResult:
    text = read_text(path)
    front_matter_text, body = split_front_matter(text)
    meta = parse_front_matter(front_matter_text)
    findings: list[Finding] = []

    def error(code: str, message: str) -> None:
        findings.append(Finding("error", code, message))

    def warn(code: str, message: str) -> None:
        findings.append(Finding("warning", code, message))

    required_fields = ("layout", "title", "date", "categories", "description", "toc")
    for field in required_fields:
        value = meta.get(field)
        if field not in meta or value is None or value == "" or value == []:
            error("missing_field", f"Missing required front matter field: {field}")

    categories = meta.get("categories", [])
    if isinstance(categories, str):
        categories = [categories]

    if categories:
        invalid = [category for category in categories if category not in VALID_CATEGORIES]
        if invalid:
            error("invalid_category", f"Invalid categories: {', '.join(invalid)}")
        if len(categories) > 2:
            warn("multi_category", "Post uses more than two categories; site guidance favors a single effective public category.")

    description = str(meta.get("description", "")).strip()
    if description:
        if len(description) < 40:
            warn("short_description", "Description is very short; consider a more informative summary.")
        if len(description) > 220:
            warn("long_description", "Description is long; consider tightening for excerpt/meta usage.")

    redirects = meta.get("redirect_from", [])
    if isinstance(redirects, str):
        redirects = [redirects]
    if not redirects:
        warn("missing_redirect", "No redirect_from field present.")

    word_count = count_words(body)
    if word_count < 250:
        warn("short_body", f"Post is short at {word_count} words.")

    heading_count = count_headings(body)
    if heading_count == 0:
        warn("no_headings", "Post has no headings.")

    internal_link_count = count_internal_links(body)
    if internal_link_count == 0:
        warn("no_internal_links", "Post has no obvious internal links to site canon or hubs.")

    if has_research_hints(body) and "notes" not in meta:
        warn("missing_notes", "Body looks research-heavy but has no notes front matter.")

    is_substantial = word_count >= 600
    combined_text = f"{meta.get('title', '')}\n{description}\n{body}"
    category_set = set(categories)

    if is_substantial and not has_any_hint(body, CORNERSTONE_LINK_HINTS):
        warn(
            "missing_canon_link",
            "Substantial post does not appear to link to Start Here, Telos, a category hub, or a cornerstone post.",
        )

    family_facing = bool(category_set & {"field-notes", "when-it-breaks"}) or has_any_hint(
        combined_text, ("family", "caregiver", "what families", "if someone you love")
    )
    if family_facing and not has_any_hint(body, FAMILY_UTILITY_HINTS):
        warn(
            "weak_family_utility",
            "Family-facing post lacks obvious practical guidance cues such as what to ask, what to watch for, next steps, or red flags.",
        )

    analytical = is_substantial and bool(category_set & {"the-machine", "field-notes", "when-it-breaks"})
    if analytical and count_hint_hits(body, MECHANISM_HINTS) < 3:
        warn(
            "weak_mechanism_framing",
            "Analytical post may not clearly name the system mechanism or incentive structure driving the situation.",
        )

    family_confusion = family_facing and has_any_hint(combined_text, FAMILY_CONFUSION_HINTS)
    if family_confusion and not has_any_hint(body, DEBUGGER_HINTS):
        warn(
            "missing_debugger_block",
            "Family-confusion post may benefit from a debugger-style block: where you are, what's happening, what to ask next, what to document, and red flags.",
        )

    return QaResult(
        path=str(path.relative_to(ROOT)),
        findings=findings,
        word_count=word_count,
        internal_link_count=internal_link_count,
        heading_count=heading_count,
    )


def resolve_targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return sorted(POSTS_DIR.glob("*.md"))
    path = args.path
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return [path]


def render_text(results: list[QaResult]) -> str:
    lines: list[str] = []
    for result in results:
        error_count = sum(1 for finding in result.findings if finding.severity == "error")
        warning_count = sum(1 for finding in result.findings if finding.severity == "warning")
        lines.append(f"{result.path}: {error_count} error(s), {warning_count} warning(s)")
        lines.append(
            f"  words={result.word_count} headings={result.heading_count} internal_links={result.internal_link_count}"
        )
        for finding in result.findings:
            lines.append(f"  [{finding.severity}] {finding.code}: {finding.message}")
    return "\n".join(lines) + ("\n" if lines else "")


def main() -> int:
    args = parse_args()
    results = [check_post(path) for path in resolve_targets(args)]

    if args.json:
        payload = [
            {
                **asdict(result),
                "findings": [asdict(finding) for finding in result.findings],
            }
            for result in results
        ]
        print(json.dumps(payload, indent=2))
    else:
        sys.stdout.write(render_text(results))

    return 1 if any(any(f.severity == "error" for f in result.findings) for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
