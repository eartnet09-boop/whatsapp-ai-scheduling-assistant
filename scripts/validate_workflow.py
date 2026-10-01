#!/usr/bin/env python3
"""Validate a sanitized n8n workflow export before committing it.

Usage:
    python scripts/validate_workflow.py [FILE ...]

If no FILE is given, every ``*.json`` file inside ``workflows/`` is checked.

For each file the script:
    1. Parses the JSON and fails if it is invalid.
    2. Confirms it looks like an n8n workflow (``nodes`` list + ``connections``
       object) and prints the number of nodes.
    3. Confirms every connection source/target points to an existing node name.
    4. Scans the raw text and fails (exit 1) on any secret or identifier that
       must never be committed:
           - the JSON key ``"credentials"`` (n8n credential references)
           - ``webhookId``
           - e-mail addresses (``example.com``/``example.org``/``example.net``
             are ignored: they are reserved documentation domains)
           - Brazilian mobile numbers matching ``\\b55\\d{10,11}\\b``
             (``5500000000000`` is ignored: it is the documented fake number)
           - any HTTP(S) host other than ``YOUR-WAHA-HOST``
           - token-like strings: ``sk-``, ``gsk_``, ``ghp_``, ``Bearer ``

Exit code is 0 when every file passes and 1 when any check fails.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ALLOWED_HOST = "YOUR-WAHA-HOST"
ALLOWED_EMAIL_DOMAINS = ("example.com", "example.org", "example.net")
ALLOWED_PHONES = ("5500000000000",)
PHONE_RE = re.compile(r"\b55\d{10,11}\b")
EMAIL_RE = re.compile(r"\b[\w.+-]+@([\w-]+\.[\w.-]+)\b")
URL_RE = re.compile(r"https?://([^/\"'\\\s]+)")
TOKEN_RE = re.compile(r"(?:sk-|gsk_|ghp_)[A-Za-z0-9_\-]{4,}|\bBearer\b")
FORBIDDEN_KEYS = ("credentials", "webhookId")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_workflow(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: cannot be read ({exc})"]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON ({exc})"]

    if not isinstance(data, dict):
        return [f"{path}: top level is not a JSON object"]

    nodes = data.get("nodes")
    connections = data.get("connections")
    if not isinstance(nodes, list) or not isinstance(connections, dict):
        fail(errors, f"{path}: missing n8n 'nodes' list or 'connections' object")
        return errors

    node_names = {n.get("name") for n in nodes if isinstance(n, dict)}
    node_names.discard(None)
    print(f"{path}: valid JSON, {len(nodes)} nodes")

    if not nodes:
        fail(errors, f"{path}: workflow has no nodes")

    for source, outputs in connections.items():
        if source not in node_names:
            fail(errors, f"{path}: connection source '{source}' does not exist")
        if not isinstance(outputs, dict):
            continue
        for output_type, groups in outputs.items():
            if not isinstance(groups, list):
                continue
            for group in groups:
                if not isinstance(group, list):
                    continue
                for link in group:
                    target = link.get("node") if isinstance(link, dict) else None
                    if target not in node_names:
                        fail(
                            errors,
                            f"{path}: connection {source} -> {target!r} "
                            f"({output_type}) points to a missing node",
                        )

    for key in FORBIDDEN_KEYS:
        if key in raw:
            fail(errors, f"{path}: forbidden identifier '{key}' found")

    for match in EMAIL_RE.finditer(raw):
        domain = match.group(1).lower()
        if not domain.endswith(ALLOWED_EMAIL_DOMAINS):
            fail(errors, f"{path}: e-mail address found: {match.group(0)}")

    for match in PHONE_RE.finditer(raw):
        if match.group(0) not in ALLOWED_PHONES:
            fail(errors, f"{path}: phone number found: {match.group(0)}")

    for match in URL_RE.finditer(raw):
        host = match.group(1).split(":")[0]
        if host != ALLOWED_HOST:
            fail(errors, f"{path}: unexpected host '{host}' (only {ALLOWED_HOST} allowed)")

    for match in TOKEN_RE.finditer(raw):
        fail(errors, f"{path}: token-like string found: {match.group(0)[:12]}...")

    return errors


def main(argv: list[str]) -> int:
    if argv:
        files = [Path(a) for a in argv]
    else:
        files = sorted(Path("workflows").glob("*.json"))
        if not files:
            print("no workflow files found in workflows/", file=sys.stderr)
            return 1

    errors: list[str] = []
    for path in files:
        errors.extend(validate_workflow(path))

    if errors:
        print("\nVALIDATION FAILED", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"\nOK: {len(files)} file(s) validated, no secrets detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
