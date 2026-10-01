# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-01

### Added

- Sanitized n8n workflow export with 19 nodes: WAHA webhook intake, group and
  echo filters, one-time business-card delivery (Postgres + Redis) and the
  *Nero* AI agent (Groq `openai/gpt-oss-120b`, Redis memory, 5 Google
  Calendar tools).
- `scripts/validate_workflow.py` — JSON/structure validation plus secret scan
  (credentials, webhook ids, e-mails, phones, unexpected hosts, tokens); also
  run by CI.
- `scripts/sanitize_workflow.py` — converts a raw n8n export into a
  commit-safe version (drops credentials/webhookId, forces `active = false`,
  rewrites hosts, calendar ids and webhook path to placeholders).
- `sql/001_create_cartao_visita.sql` — inferred DDL for the `cartao_visita`
  table with a fictitious example insert.
- `examples/webhook-payload.json` — fake WAHA message payload for local
  testing.
- `.env.example` documenting every value needed before importing the
  workflow.
- `prompts/nero-system-prompt.md` — verbatim agent system prompt with a
  section-by-section guide.
- Documentation: architecture (Mermaid + node table), setup guide,
  WAHA configuration, credentials, Google Calendar setup, troubleshooting,
  testing and roadmap.
- READMEs in English and Portuguese (pt-BR).
- Community files: LICENSE (MIT), CONTRIBUTING, CODE_OF_CONDUCT, SECURITY and
  GitHub issue/PR templates.

### Security

- Export ships with placeholders only; validator and CI fail on any secret.
- Webhook authentication is documented as a known gap with mitigation steps.
