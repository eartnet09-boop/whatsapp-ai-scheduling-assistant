# Credentials

The exported workflow contains **no credentials** — n8n stores them outside
the export. After importing, create each credential below and select it on
the nodes listed. Keep the values in a password manager (and, as a reminder
only, in the git-ignored `.env`).

| # | Credential (n8n type) | Nodes that use it | What you need | Placeholder in export |
| --- | --- | --- | --- | --- |
| 1 | **Groq API** (`lmChatGroq`) | Modelo de Linguagem (Groq) | API key from the Groq console | none (credential only) |
| 2 | **Redis** | Memória de Conversa (Redis), Verifica Cartão Enviado, Marca Cartão Enviado | host, port, password, DB | none (credential only) |
| 3 | **Postgres** | Buscar Cartão de Visita | host, port, database, user, password, schema | none (credential only) |
| 4 | **Google Calendar OAuth2** | Criar Evento, Buscar Todos os Eventos, Buscar Evento Específico, Atualizar Evento, Cancelar Evento | OAuth2 client id + secret, Google sign-in | calendar id = `YOUR_CALENDAR_ID` |
| 5 | **Header Auth** (`httpHeaderAuth`) | Enviar Cartão via WAHA, Enviar Resposta via WAHA | header name + token expected by WAHA | URL host = `https://YOUR-WAHA-HOST` |

Use **one Redis credential** for nodes 2 (the workflow notes say the memory
node and the card nodes share it) and **one Header Auth credential** for both
WAHA nodes.

## 1. Groq API

1. Create an API key in the Groq console (never paste it into the repo).
2. In n8n: **Credentials → New → Groq API** (name in your UI may vary).
3. Select it on `Modelo de Linguagem (Groq)`.

The workflow calls the model `openai/gpt-oss-120b`. Groq retires models
periodically — if the model is no longer available, pick any **general chat
model** from the current Groq catalogue (do not use safeguard/moderation
variants; they produce evasive answers). See
[troubleshooting.md](troubleshooting.md).

## 2. Redis

Host/port/credentials of the Redis instance reachable from n8n. Two features
depend on it:

- conversation memory (session = `senderAlt`, TTL 1 h, 15-message window);
- the `cartao_enviado:<senderAlt>` key that guarantees the card is sent once.

If Redis fails, the card nodes continue without stopping the flow
(`continueRegularOutput`) — the card may be sent again. Details in
[troubleshooting.md](troubleshooting.md).

## 3. Postgres

Any database where you ran
[`sql/001_create_cartao_visita.sql`](../sql/001_create_cartao_visita.sql).
The node runs a single `SELECT … ORDER BY id DESC LIMIT 1`.

## 4. Google Calendar OAuth2

Create an OAuth2 client (Google Cloud console), paste id/secret in n8n and
complete the Google sign-in flow offered by the credential. Full walkthrough:
[google-calendar-setup.md](google-calendar-setup.md).

The export keeps only the placeholder calendar id `YOUR_CALENDAR_ID` inside
the 5 tool nodes — replace it after importing.

## 5. Header Auth (WAHA)

| Field | Value |
| --- | --- |
| Name | e.g. `WAHA API` |
| Header name | The header your WAHA instance expects (commonly `X-Api-Key`) |
| Header value | The matching WAHA API key/token |

Both WAHA HTTP nodes must use this credential. Details:
[waha-configuration.md](waha-configuration.md).

## Placeholders recap

These strings are intentional and documented in
[setup-guide.md](setup-guide.md):

- `https://YOUR-WAHA-HOST` — WAHA base URL;
- `YOUR_CALENDAR_ID` — Google Calendar id;
- `replace-with-a-long-random-path` — webhook path (acts as a URL secret).

> Never paste real keys into the workflow JSON before exporting it. If you
> do, run `python scripts/sanitize_workflow.py raw.json` before committing —
> and double-check with `python scripts/validate_workflow.py`.
