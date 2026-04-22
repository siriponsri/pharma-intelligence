# Copilot Agent Prompts

This directory contains **machine-executable prompts** for GitHub Copilot Agent mode.
Humans should read `../next_steps.md` instead for a narrative overview.

## How to use these prompts

1. Ensure you're on a clean git state (`git status` shows no uncommitted changes)
2. Open VS Code → Copilot Chat panel (Ctrl+Alt+I or ⌘+Alt+I)
3. Select **"Agent"** mode from the top dropdown (not "Ask" or "Edit")
4. Open the prompt file for the current step
5. Copy the ENTIRE file contents into the Agent chat
6. Paste and send

## Workflow between steps

```
Step A (mock data fix)
    ↓ you review: git diff, pytest, experiment_02 doc
    ↓ you approve and merge
Step B (Prophet baseline)
    ↓ you review
    ↓ you approve and merge
Step C (XGBoost — currently placeholder)
```

## Current status

| Step | Status | Prompt file |
|---|---|---|
| A — Improve mock data realism | 📝 Ready to execute | `step_A_fix_mock_data.md` |
| B — Prophet baseline | 📝 Ready to execute (after A) | `step_B_prophet_baseline.md` |
| C — XGBoost | 🔒 Placeholder — do not execute | `step_C_xgboost.md` |
| D — TFT on Vast AI | 🔒 Not yet planned | — |

## Principles behind these prompts

Each prompt includes:

- **Required reading** — Copilot reads context files first, so it doesn't guess
- **Task 0 — Planning** — Copilot writes a plan and STOPS for your approval before acting
- **Explicit task list** — numbered, with code snippets and expected outputs
- **Acceptance criteria** — objective pass/fail checks
- **Decision trees** — what to do if criteria fail (bounded retries)
- **Anti-patterns** — specific "do NOT do X" rules
- **Scientific honesty clause** — "a failed experiment honestly documented beats a tuned success"

## If Copilot goes off the rails

If Copilot starts doing something unexpected (editing files you didn't ask about, running unrelated commands, trying to "fix" experiments by changing methodology):

1. **Stop the Agent immediately** (there's a stop button in the chat panel)
2. **Check `git status`** — if files changed unexpectedly, `git checkout -- <file>` to revert
3. **Review the prompt** — did you include an updated version of `copilot-instructions.md`? Were the anti-patterns clear?
4. **Restart fresh** — Agent conversations can accumulate confusion; starting over is often faster than correcting

## Feedback loop

After each step:

1. Update `../next_steps.md` with actual results
2. Update `.github/copilot-instructions.md` section "Current Project State" with new milestones
3. If you found an anti-pattern not covered, add it to the instructions file

This keeps the prompt system self-improving.
