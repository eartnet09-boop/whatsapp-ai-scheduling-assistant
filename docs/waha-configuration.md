# WAHA Configuration

WAHA (WhatsApp HTTP API) is the bridge between WhatsApp and the workflow.
This page covers what the workflow expects from it: webhook, session,
authentication and events.

> Menu names and payload fields change between WAHA versions. **Verify against
> the official WAHA documentation** for the version you run.

## Webhook

The `Webhook` node listens for `POST` requests on:

```
https://<your-n8n-host>/webhook/<path>
```

`<path>` must be a **long, random string** — in the sanitized export the node
path is `replace-with-a-long-random-path`. Treat it like a password: anyone
who knows it can post fake events to your workflow.

Configure that URL as the webhook in WAHA. The exact option names depend on
your WAHA version (usually a webhook URL entry in `docker-compose.yml` or in
the WAHA environment — check the official docs).

### Events

The workflow only cares about incoming messages: the `Filtro de Dados` node
reads `event`, `session`, `payload.body`, `payload.timestamp`,
`payload.source`, `payload.ack`, `payload.ackName`, `payload.hasMedia` and
`payload._data.Info.*`. Subscribe at least to the message-received event of
your WAHA version; extra events are harmless (they are filtered out).

## Session

The payload carries a `session` field, and the workflow forwards it back on
both `sendImage` and `sendText` calls. Key points:

- The session name in your WAHA deployment must exist — messages sent with an
  unknown session name fail at send time.
- The example payload uses `default`
  ([`examples/webhook-payload.json`](../examples/webhook-payload.json)); if
  your WAHA runs a different session (e.g. `ear`), test with that name.
- Only one WAHA session is expected by this workflow.

## Authentication

Both HTTP nodes (`Enviar Cartão via WAHA`, `Enviar Resposta via WAHA`) use an
n8n **Header Auth** credential:

| Setting | Value |
| --- | --- |
| Header name | Whatever you configure in WAHA (commonly `X-Api-Key`) |
| Header value | The API key configured on the WAHA side |

The sanitized export contains no header name or key. Create the credential in
n8n after importing and select it on both nodes. See
[credentials.md](credentials.md).

### Incoming side (webhook)

The `Webhook` node as shipped does **not** require a credential: security
relies on the random path. If your n8n is exposed to the internet, consider
(optionally, see [roadmap.md](roadmap.md)):

1. Enabling header authentication on the n8n Webhook node (n8n supports a
   credential for that) **and** configuring WAHA to send the same header, or
2. Restricting network access to `/webhook/*` at the reverse proxy, or
3. Keeping the path long and random and rotating it if it ever leaks.

## Media / voice notes

`Filtro de Dados` already extracts `hasMedia` and `type`, but voice messages
arrive with an empty `body`, so the agent answers as if the customer said
nothing. Handling audio (download → transcription → continue) is **not
implemented**; it is described in [roadmap.md](roadmap.md). If you plan to
implement it, enable media storage in WAHA first.

## Debugging tips

- Watch n8n's **Executions** view: a message that never reaches the Webhook
  node is a WAHA-side problem (webhook URL, session, events).
- A message that reaches the workflow but is dropped usually hits the group
  filter (`@g.us`) or the echo filter (`isFromMe = true`).
- Test the webhook directly with `curl` — see [testing.md](testing.md).
