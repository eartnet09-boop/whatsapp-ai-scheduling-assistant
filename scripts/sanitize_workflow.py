#!/usr/bin/env python3
"""Turn a raw n8n workflow export into a version that is safe to commit.

Usage:
    python scripts/sanitize_workflow.py RAW_EXPORT.json [OUTPUT.json]

If OUTPUT is omitted, the sanitized workflow is written next to the input as
``<input>.sanitized.json`` (unless the input already ends with that suffix).

What the sanitizer does:
    * removes every ``credentials`` block (n8n credential references) at any
      depth, plus the top-level ``webhookId`` and the workflow ``id``;
    * forces ``active`` to ``false``;
    * rewrites HTTP(S) hosts to ``https://YOUR-WAHA-HOST`` (WAHA calls);
    * rewrites ``calendarId`` values to ``YOUR_CALENDAR_ID``;
    * rewrites the Webhook node ``path`` to ``replace-with-a-long-random-path``;
    * masks e-mail addresses and Brazilian phone numbers
      (``\\b55\\d{10,11}\\b``) with obvious placeholders.

After writing, the result is checked with ``scripts/validate_workflow.py``.
If validation fails the output file is removed and the script exits 1, so a
leaking export never survives on disk.

Never commit the raw export: it is covered by ``*.raw.json`` / ``*-export.json``
in ``.gitignore``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_workflow import validate_workflow  # noqa: E402

WEBHOOK_PATH_PLACEHOLDER = "replace-with-a-long-random-path"
CALENDAR_PLACEHOLDER = "YOUR_CALENDAR_ID"
WAHA_URL_PLACEHOLDER = "https://YOUR-WAHA-HOST"
EMAIL_PLACEHOLDER = "redacted-email@example.com"
PHONE_PLACEHOLDER = "5500000000000"

DROP_TOP_LEVEL_KEYS = ("id", "webhookId", "credentials")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\b55\d{10,11}\b")


def _rewrite_host(url: str) -> str:
    parts = re.match(r"(https?://)([^/]+)(.*)", url)
    if not parts:
        return url
    return WAHA_URL_PLACEHOLDER + parts.group(3)


def sanitize_value(key: str | None, value, in_webhook_node: bool = False):
    if isinstance(value, dict):
        return {k: sanitize_value(k, v, in_webhook_node) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_value(key, v, in_webhook_node) for v in value]
    if isinstance(value, str):
        if key == "calendarId" and value != CALENDAR_PLACEHOLDER:
            return CALENDAR_PLACEHOLDER
        if in_webhook_node and key == "path":
            return WEBHOOK_PATH_PLACEHOLDER
        if value.startswith("http://") or value.startswith("https://"):
            value = _rewrite_host(value)
        value = EMAIL_RE.sub(EMAIL_PLACEHOLDER, value)
        value = PHONE_RE.sub(PHONE_PLACEHOLDER, value)
        return value
    return value


def sanitize_workflow(data: dict) -> dict:
    result = {k: v for k, v in data.items() if k not in DROP_TOP_LEVEL_KEYS}
    result["active"] = False

    nodes = []
    for node in result.get("nodes", []):
        if not isinstance(node, dict):
            nodes.append(node)
            continue
        node = dict(node)
        node.pop("credentials", None)
        node.pop("webhookId", None)
        is_webhook = str(node.get("type", "")).endswith(".webhook")
        node["parameters"] = sanitize_value("parameters", node.get("parameters"), is_webhook)
        nodes.append(node)
    result["nodes"] = nodes
    result["connections"] = sanitize_value("connections", result.get("connections", {}))
    if isinstance(result.get("settings"), dict):
        result["settings"] = sanitize_value("settings", result["settings"])
    result["name"] = sanitize_value("name", result.get("name", ""))
    return result


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1

    source = Path(argv[0])
    if len(argv) > 1:
        target = Path(argv[1])
    else:
        name = source.name
        target = source.with_name(name[: -len(".json")] + ".sanitized.json") if name.endswith(".json") else source.with_name(name + ".sanitized.json")

    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {source}: {exc}", file=sys.stderr)
        return 1

    clean = sanitize_workflow(data)
    target.write_text(json.dumps(clean, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    errors = validate_workflow(target)
    if errors:
        target.unlink(missing_ok=True)
        print("sanitization failed validation; output removed", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"sanitized: {source} -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
