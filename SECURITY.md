# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for security problems.

1. Use GitHub's **private vulnerability reporting** on this repository
   (*Security → Report a vulnerability*), or
2. Contact the maintainer privately through GitHub (profile → contact) and
   mark the subject as `SECURITY`.

Include the affected file/node, steps to reproduce and the impact. You should
receive an acknowledgement within a few days; fixes for confirmed issues are
released as soon as possible and credited in the changelog unless you prefer
to remain anonymous.

## Scope and known gaps

- **The n8n Webhook node ships without authentication.** Access control
  relies on a long, random webhook path (`replace-with-a-long-random-path` in
  the sanitized export). Anyone who learns the path can post events to the
  workflow. If your n8n is internet-facing, either
  - enable header authentication on the webhook and configure WAHA to send
    the same header, or
  - restrict `/webhook/*` at your reverse proxy, or
  - rotate the path if it ever leaks.

  Hardening the webhook is tracked in [docs/roadmap.md](docs/roadmap.md).

- **No secrets belong in this repository.** The exported workflow contains
  placeholders only (`https://YOUR-WAHA-HOST`, `YOUR_CALENDAR_ID`,
  `replace-with-a-long-random-path`). CI runs
  `scripts/validate_workflow.py`, which fails on credentials, webhook ids,
  e-mails, phone numbers, unexpected hosts and token-like strings.

- **Raw n8n exports can contain credentials.** They are git-ignored
  (`*.raw.json`, `*-export.json`); always run
  `scripts/sanitize_workflow.py` before committing (see
  [CONTRIBUTING.md](CONTRIBUTING.md)).

- **`.env` must never be committed.** Copy `.env.example` and keep the real
  file local.

- **Third-party services** (WAHA, Groq, Google, Redis, PostgreSQL) are out of
  scope for this repository; follow their own security guidance.

## Supported versions

The version on the `main` branch is the supported one. Older exports should
not be used in production without re-importing the latest sanitized workflow.
