# Testing

How to exercise the workflow without a real WhatsApp conversation.

## 1. Prerequisites

- The workflow imported and **Active** in n8n.
- Credentials configured ([credentials.md](credentials.md)).
- The WAHA session name in your payload matches a real WAHA session.

## 2. Send a fake message with curl

Copy the example payload and POST it to the webhook URL:

```bash
curl -X POST "https://<your-n8n-host>/webhook/<your-random-path>" \
  -H "Content-Type: application/json" \
  -d @examples/webhook-payload.json
```

Locally, n8n's test URL (`/webhook-test/...`) can be used while the
*Listen for test event* mode is open — the production path (`/webhook/...`)
requires the workflow to be active.

The payload in
[`examples/webhook-payload.json`](../examples/webhook-payload.json) models a
first message from a new customer:

```json
{
  "event": "message",
  "session": "default",
  "payload": {
    "body": "Olá! Gostaria de agendar uma reunião para falar sobre automação.",
    "_data": {
      "Info": {
        "SenderAlt": "5500000000000@c.us",
        "IsFromMe": false,
        "Type": "chat"
      }
    }
  }
}
```

All phone numbers and names in the example are obviously fake.

## 3. What to check

| Step | Where | Expected |
| --- | --- | --- |
| Execution appears | n8n → Executions | one new execution, green |
| Data normalized | `Filtro de Dados` output | `senderAlt`, `body`, `session`, `isFromMe`, `chat` populated |
| Group filter | `Verifica se é Grupo` | `false` branch (direct chat) |
| Echo filter | `Verifica se é Mensagem Própria` | `false` branch (`isFromMe = false`) |
| Card check | `Verifica Cartão Enviado` | empty on first run |
| Card sent | `Enviar Cartão via WAHA` | WAHA 200, image visible in WhatsApp |
| Flag written | Redis | `GET cartao_enviado:5500000000000@c.us` → `1` |
| Agent ran | `Assistente IA` | `output` with a relevant Portuguese answer |
| Reply sent | `Enviar Resposta via WAHA` | WAHA 200, message visible in WhatsApp |

### Variations to test

1. **Second message:** run the same payload again → the card must **not** be
   sent (branch `Já Recebeu Cartão?` → `false` → straight to the agent).
2. **Echo:** set `"IsFromMe": true` → execution ends in `Mensagem Ignorada`.
3. **Group:** set `Chat` to `123456789-98765@g.us` → `Mensagem Ignorada`.
4. **Scheduling:** send *"quero agendar uma reunião amanhã às 10h"* → the
   agent calls `Criar Evento` and the event appears in Google Calendar
   (timezone `-03:00`).
5. **Cancellation:** ask to cancel → `Buscar Todos os Eventos` +
   `Cancelar Evento`.
6. **Memory:** send two messages in a row → the second answer must
   acknowledge the first (Redis session, 1 h TTL).

## 4. Without n8n receiving real WhatsApp traffic

Use curl as above. The workflow does not call WhatsApp on the *input* side —
it only receives HTTP — so the fake payload exercises the entire chain up to
the two outbound WAHA calls. If you do not want to hit a real phone number,
point `https://YOUR-WAHA-HOST` at a WAHA instance connected to a test number.

## 5. Automated tests

Automated tests over example payloads are **not implemented**; they are
planned in [roadmap.md](roadmap.md). Today the safety net is
`python scripts/validate_workflow.py` (structure + secret scan), run locally
and by CI.
