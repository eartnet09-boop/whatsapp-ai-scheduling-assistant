# Roadmap

Ideas for future work. **Nothing on this page is implemented** — the current
behaviour is exactly what the workflow JSON does (see
[architecture.md](architecture.md)).

## Voice notes and other media

- **Status: planned, not implemented.**
- `Filtro de Dados` already extracts `hasMedia` and `type`, but voice
  messages arrive with an empty `body`, so the agent cannot answer them.
- Proposal: add an `IF` by media type → download the file through the WAHA
  media API → transcribe it (e.g. Whisper-compatible API on Groq) → replace
  `body` with the transcript → continue the normal flow.
- Prerequisite: media storage enabled in WAHA
  ([waha-configuration.md](waha-configuration.md)).

## Webhook authentication

- **Status: planned, not implemented.**
- The `Webhook` node currently relies only on the long random path.
- Proposal: enable n8n's webhook header authentication and configure WAHA to
  send the same header; optionally restrict `/webhook/*` at the reverse
  proxy. Discussed in [security.md](../SECURITY.md) and
  [troubleshooting.md](troubleshooting.md).

## Voice replies (text-to-speech)

- **Status: idea only.**
- Answer with an audio message instead of text for customers who prefer
  listening. Would require a TTS step and a WAHA audio-send call.

## Automated tests of the flow

- **Status: planned, not implemented.**
- Run the workflow against the example payloads
  ([`examples/webhook-payload.json`](../examples/webhook-payload.json)) in
  CI or in an n8n test runner and assert: filters drop group/echo messages,
  the card is sent exactly once, and the agent produces non-empty output.

## Other backlog items

- Rotate the webhook path periodically and document the procedure.
- Optional message queue/rate limiting on top of the Groq free tier.
- Metrics: count conversations, card deliveries and calendar events per day.
