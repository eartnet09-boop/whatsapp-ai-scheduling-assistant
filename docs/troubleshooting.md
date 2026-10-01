# Troubleshooting

Format: **Symptom → Cause → Solution**. Every item below was learned in
production.

---

## Empty agent prompt on the card path

- **Symptom:** the first reply to a new customer is generic or the agent
  behaves as if the customer had sent nothing, even though the WhatsApp
  message had text.
- **Cause:** the agent prompt referenced `{{ $json.body }}`. On the
  business-card branch the current item comes from the Redis/PostgreSQL node,
  not from `Filtro de Dados`, so `$json.body` resolved to an empty string.
- **Solution:** always name the source node explicitly:
  `{{ $('Filtro de Dados').item.json.body }}`. **Already fixed** in the
  committed workflow (node `Assistente IA` → `text`).

## Broken reply when the answer has line breaks

- **Symptom:** `sendText` fails or the WhatsApp message shows raw JSON /
  truncated text whenever the model answers with multiple lines.
- **Cause:** the HTTP body was hand-written JSON with
  `{{ $json.output }}` inside quotes; unescaped newlines produced an invalid
  JSON body.
- **Solution:** build the body with `JSON.stringify({...})` — done for both
  WAHA nodes (`Enviar Resposta via WAHA`, `Enviar Cartão via WAHA`). Use the
  same pattern in any new HTTP node.

## Evasive answers from the model

- **Symptom:** the assistant refuses, deflects or answers "I can't help with
  that" to normal questions.
- **Cause:** a **safeguard/moderation variant** of the model was selected
  (e.g. `gpt-oss-safeguard`). Those variants are for moderation, not for
  conversation.
- **Solution:** use a general chat model. The workflow ships with
  `openai/gpt-oss-120b`; Groq retires models periodically (older ones such as
  *Llama 3.3 70B versatile* are gone), so **check the current Groq catalogue**
  before pinning a different model and do not trust outdated names.

## Temporary failures during message bursts

- **Symptom:** some messages get no answer during peaks; n8n executions show
  Groq rate-limit errors.
- **Cause:** the free Groq plan limits tokens per minute. Each agent turn is
  at least one model call, and every tool call (calendar) triggers a second
  call, so one busy conversation multiplies usage.
- **Solution:** retry the message later; reduce the context window if needed
  (memory node `contextWindowLength`, currently 15 messages); consider a paid
  tier or a different provider for higher volume. Also note that WhatsApp
  messages arriving in bursts may queue in n8n.

## Fake messages accepted by the webhook

- **Symptom:** anyone can POST to your webhook and make the assistant answer.
- **Cause:** the `Webhook` node ships **without** authentication; the only
  defence is the long random path (`replace-with-a-long-random-path`).
- **Solution (optional hardening):** enable header authentication on the n8n
  Webhook node and configure WAHA to send the same header, and/or restrict
  `/webhook/*` at your reverse proxy. Not implemented yet — see
  [roadmap.md](roadmap.md) and [waha-configuration.md](waha-configuration.md).

## Bot answers its own messages (loop)

- **Symptom:** the assistant keeps talking to itself; executions run back to
  back forever.
- **Cause:** WAHA re-emits messages sent by the bot with `isFromMe = true`.
  Without the echo filter, the answer triggers a new execution.
- **Solution:** keep `Verifica se é Mensagem Própria` (`isFromMe` check) and
  `Verifica se é Grupo` (`@g.us` check) connected before any I/O. Do not
  delete or bypass these nodes.

## Business card sent twice

- **Symptom:** a customer receives the card again after some time.
- **Cause:** the card nodes use `onError: continueRegularOutput`. If Redis
  fails on the read (`Verifica Cartão Enviado`) or on the write
  (`Marca Cartão Enviado`), the flow continues without the flag — the next
  message is treated as "never received".
- **Solution:** check Redis availability and logs around that execution. As a
  last resort, delete the customer's key (`cartao_enviado:<senderAlt>`) only
  if you *want* the card re-sent. This is a known edge case, by design the
  conversation must never break because of the card.

## Send fails with a session error

- **Symptom:** `sendText`/`sendImage` returns an error only for some
  environments or tests.
- **Cause:** the WAHA `session` name comes from the payload
  (`payload.session`) and is forwarded to the API. Tests that invent a
  session name that does not exist in WAHA fail at send time.
- **Solution:** use an existing session name in your test payload
  ([`examples/webhook-payload.json`](../examples/webhook-payload.json) uses
  `default`). See [waha-configuration.md](waha-configuration.md).

## Events land two/three hours off

- **Symptom:** created events are shifted in Google Calendar.
- **Cause:** the calendar tools describe datetimes with `TZ -03:00`
  (Brasília). Another timezone — or a calendar configured with a different
  time zone — shifts the result.
- **Solution:** align the calendar timezone with `-03:00`, or edit the
  `$fromAI` descriptions in `Criar Evento` / `Atualizar Evento` with your
  offset. See [google-calendar-setup.md](google-calendar-setup.md).

## Voice notes and stickers are ignored

- **Symptom:** the customer sends an audio and the agent answers something
  generic.
- **Cause:** `hasMedia` is extracted, but the message `body` of voice notes
  is empty; there is no transcription step yet.
- **Solution:** none implemented — see [roadmap.md](roadmap.md).

---

## Quick diagnostics checklist

1. n8n → **Executions**: does the run reach `Filtro de Dados`?
2. Is it discarded by `Verifica se é Grupo` or `Verifica se é Mensagem Própria`?
3. Does the `Assistente IA` input contain the customer text?
4. Do Groq/Redis/Postgres/Calendar credentials resolve (no gray nodes)?
5. Does the final `Enviar Resposta via WAHA` return a WAHA success payload?
