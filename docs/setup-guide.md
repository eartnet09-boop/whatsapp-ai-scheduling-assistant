# Setup Guide

End-to-end instructions to go from a fresh machine to a working assistant.

> Commands and menu names change between releases. When something does not
> match your screen exactly, **check the official documentation** of the tool
> in question instead of guessing.

## Prerequisites

| Requirement | Purpose | Minimum version |
| --- | --- | --- |
| n8n (self-hosted or Cloud) | Runs the workflow | not verified |
| WAHA (WhatsApp HTTP API) | Sends/receives WhatsApp messages | not verified |
| Redis | Conversation memory + business-card control | not verified |
| PostgreSQL | Stores the business-card image (`cartao_visita`) | not verified |
| Groq account | LLM (`openai/gpt-oss-120b`) | not verified |
| Google account | Calendar used by the agent | not verified |

## 1. Get the code

```bash
git clone <repository-url>
cd whatsapp-ai-scheduling-assistant
```

## 2. Prepare PostgreSQL

Create a database and run the schema:

```bash
psql -U <user> -d <database> -f sql/001_create_cartao_visita.sql
```

Insert your business card (image encoded as base64) — see the example inside
[`sql/001_create_cartao_visita.sql`](../sql/001_create_cartao_visita.sql).
The workflow always reads the **most recent** row (`ORDER BY id DESC LIMIT 1`).

## 3. Prepare Redis

Run Redis anywhere reachable from n8n (local service, Docker, managed). No
special configuration is required: the workflow uses one key per customer
(`cartao_enviado:<senderAlt>`) and the chat memory keys created by n8n.

```bash
docker run --rm -p 6379:6379 redis:7
```

> Replace the image tag with the version you standardised on; tags were **not
> verified** for this project.

## 4. Configure WAHA

See [waha-configuration.md](waha-configuration.md) for the webhook, the
session name and the authentication header.

## 5. Import the workflow

1. Open n8n → **Workflows → Import from File**.
2. Select [`workflows/whatsapp-ai-scheduling-assistant.json`](../workflows/whatsapp-ai-scheduling-assistant.json).

The export is sanitized: it contains **no credentials**, `active: false`, the
placeholder host `https://YOUR-WAHA-HOST`, the calendar id
`YOUR_CALENDAR_ID` and the webhook path `replace-with-a-long-random-path`.

## 6. Create the n8n credentials

Create each credential and select it in the nodes that request it. Full
details in [credentials.md](credentials.md):

| Credential | Used by |
| --- | --- |
| Groq API | Modelo de Linguagem (Groq) |
| Redis (same one) | Memória de Conversa (Redis), Verifica Cartão Enviado, Marca Cartão Enviado |
| PostgreSQL | Buscar Cartão de Visita |
| Google Calendar OAuth2 | the 5 calendar tools |
| Header Auth (WAHA) | Enviar Cartão via WAHA, Enviar Resposta via WAHA |

## 7. Replace the placeholders

| Placeholder | Where | What to put |
| --- | --- | --- |
| `https://YOUR-WAHA-HOST` | Enviar Cartão / Enviar Resposta nodes | Your WAHA base URL |
| `replace-with-a-long-random-path` | Webhook node → **Path** | A long random string (this is your secret) |
| `YOUR_CALENDAR_ID` | the 5 Google Calendar nodes | Your calendar id ([calendar guide](google-calendar-setup.md)) |

Copy [`.env.example`](../.env.example) to `.env` to keep track of the same
values (`.env` is git-ignored). n8n itself reads credentials from its UI, not
from this file.

## 8. Activate and connect WAHA

1. Toggle the workflow to **Active** in n8n.
2. Point the WAHA webhook at
   `https://<your-n8n-host>/webhook/<your-random-path>`
   ([waha-configuration.md](waha-configuration.md)).
3. Send a WhatsApp message to the connected number and watch the execution
   log in n8n.

## 9. Test

Simulate a message without WhatsApp using the example payload — see
[testing.md](testing.md).

## Troubleshooting

Symptom-by-symptom fixes: [troubleshooting.md](troubleshooting.md).
