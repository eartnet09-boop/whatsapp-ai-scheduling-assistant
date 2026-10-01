# Google Calendar Setup

The agent manages appointments through five `Google Calendar Tool` nodes.
This guide covers the OAuth2 credential, the calendar id and the timezone.

> Google changes its consoles and consent screens often. Where a menu differs
> from what is written here, **check the current Google and n8n
> documentation**.

## 1. Create the OAuth2 client

1. In the Google Cloud console, create (or select) a project.
2. Enable the **Google Calendar API** for that project.
3. Configure the OAuth consent screen (External is fine for personal use;
   add your own Google account as a test user while the app is untested).
4. Create credentials → **OAuth client ID** → type **Web application**.
5. Add n8n's OAuth redirect URL to *Authorized redirect URIs*. n8n shows the
   exact URL in the credential form when you create a **Google Calendar OAuth2**
   credential — copy it from there.

## 2. Create the n8n credential

1. n8n → **Credentials → New → Google Calendar OAuth2 API**
   (the exact name may vary by n8n version).
2. Paste the client id and client secret.
3. Click **Sign in with Google** and accept the consent screen.
4. Select the credential on the five calendar nodes:
   `Criar Evento`, `Buscar Todos os Eventos`, `Buscar Evento Específico`,
   `Atualizar Evento`, `Cancelar Evento`.

### Scopes

n8n's Google Calendar credential requests the scopes defined by the node
version you run (read/write access to calendar events). Verify the requested
scopes in the n8n credential screen or in its official documentation before
using a workspace account with restricted calendars.

## 3. Get the calendar id

1. Open Google Calendar in the browser → **Settings → Integrate calendar**.
2. Choose the calendar → **Integrate calendar** section → **Calendar ID**.
3. Copy the value — it is either your own Google address or a shared calendar
   id whose local part ends with `@group.calendar.google.com`.

Then, in the imported workflow, replace `YOUR_CALENDAR_ID` in all five
calendar nodes (each node's `calendar` field, *ID* mode).

## 4. Timezone (−03:00)

The tool descriptions inside the workflow tell the model to return datetimes
with `TZ -03:00` (Brasília):

- `Criar Evento` → `Start` / `End`: *"Data e hora … no formato Datetime. TZ -03:00"*
- `Atualizar Evento` → `Start` / `End`: same wording.

Consequences:

- The agent assumes the customer is in Brasília time when it builds dates.
- Your Google Calendar timezone (Settings → **Time zone**) should match, or
  events will shift.

To use another timezone:

1. Edit the `$fromAI` descriptions in `Criar Evento` and `Atualizar Evento`
   (start/end fields) replacing `-03:00` with the target offset.
2. Keep the calendar's own timezone setting consistent.
3. Re-run `python scripts/validate_workflow.py` before committing.

## 5. Sanity checklist

- [ ] Credential selected on all five calendar nodes
- [ ] `YOUR_CALENDAR_ID` replaced everywhere (search the workflow for it)
- [ ] Test event created by asking the agent *"agendar uma reunião amanhã às 10h"*
- [ ] Event appears in the expected calendar with the expected timezone
- [ ] Update and delete work (ask the agent to change/cancel it)

If tool calls fail, see [troubleshooting.md](troubleshooting.md).
