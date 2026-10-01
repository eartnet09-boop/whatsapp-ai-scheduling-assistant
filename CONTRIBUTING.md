# Contributing

Thanks for helping improve the WhatsApp AI Scheduling Assistant.

## Workflow

1. **Fork** the repository and create a branch from `main`:
   `git checkout -b feat/short-description`
2. Make your changes, keeping commits small and atomic.
3. Run the checks (see below).
4. Open a **pull request** against `main` with a clear description of the
   problem and the solution.

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add transcription step for voice notes
fix: reference source node in agent prompt
docs: explain webhook path rotation
chore: bump workflow typeVersion
ci: run validator on pull requests
```

## Exporting a workflow from n8n

The workflow JSON is the core of this repository and must stay **sanitized**:

1. In n8n, export the workflow to a file.
2. Save the raw export outside the repo or with a name matched by
   `.gitignore` (`*.raw.json`, `*-export.json`).
3. Sanitize it:

   ```bash
   python scripts/sanitize_workflow.py raw-export.json workflows/whatsapp-ai-scheduling-assistant.json
   ```

   The script drops `credentials`, `webhookId` and the workflow `id`, forces
   `active = false`, rewrites hosts/calendar ids/webhook path to placeholders
   and masks e-mails and phone numbers.
4. Validate:

   ```bash
   python scripts/validate_workflow.py
   ```

5. **Never** commit a raw export, a credential, a real webhook path, a real
   phone number or a real e-mail. CI runs the same validator.

## Checks before pushing

```bash
python scripts/validate_workflow.py
python3 -m json.tool workflows/whatsapp-ai-scheduling-assistant.json > /dev/null
```

## Pull request checklist

- [ ] `python scripts/validate_workflow.py` passes
- [ ] No credentials, webhook ids, real URLs, e-mails or phone numbers added
- [ ] Workflow logic changes are explained (nodes, connections, expressions)
- [ ] Docs updated when behaviour changes (`docs/`, `README.md`,
      `README.pt-BR.md`, `prompts/nero-system-prompt.md`)
- [ ] New features that are not implemented yet are documented as roadmap
      items, never as current behaviour
- [ ] Commit messages follow Conventional Commits

## Reporting bugs and requesting features

Use the issue templates (bug report / feature request). For anything that
looks like a security problem, follow [SECURITY.md](SECURITY.md) instead —
do not open a public issue.
