# Synthia Professor Cockpit

Professor-facing teaching cockpit for Synthia and FNP-QNN learning summaries.

## Purpose

Students primarily interact with FNP-QNN. Synthia gives professors a governed,
human-reviewed view of minimized learning summaries, evidence links, support
priorities, intervention drafts, student transparency, and Law 25 privacy
controls.

Synthia does not create grades, sanctions, discipline, or automated-only
educational decisions.

## Run

```powershell
pnpm install
pnpm dev -- --port 5178
```

Production build:

```powershell
pnpm build
```

## Contract Routes

- `/classes/:id/learning-map`
- `/students/:id/synthesis`
- `/students/:id/evidence`
- `/interventions`
- `/teacher-notes`
- `/privacy/consents`
- `/privacy/efvp-status`
- `/audit-events`
- `/exports/student/:id`

The current UI uses local mock route handlers in `src/mockApi.ts`. The matching
Python contract and tests live in `synthia_core/professor_platform.py` and
`tests/test_professor_platform.py`.

## Governance Defaults

- FNP-QNN summaries are minimized by default.
- Evidence can be opened, but raw FNP-QNN messages are not exported.
- Interventions must be professor-validated before saving.
- Every sensitive route is expected to create an audit event.
- Cloud mode remains gated by EFVP, highest privacy defaults, written agreement
  checks, and legal review before production deployment.

