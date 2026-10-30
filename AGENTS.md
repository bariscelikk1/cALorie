# cALorie collaboration and continuity

## Start here

Read `PROJECT_HANDOFF.md` before continuing project work. Read the applicable
subdirectory `AGENTS.md` instructions before changing its files.

## User-requested checkpoint policy

The user explicitly requests frequent GitHub checkpoints so another assistant
or collaborator can continue after a chat failure.

- After every meaningful completed unit (notebook, fix, experiment analysis,
  or documentation update), update the handoff, commit the relevant files with
  a descriptive message, and push to the current authorized branch.
- During longer work, save coherent intermediate checkpoints when useful;
  clearly mark unfinished work and incomplete validation.
- Do not wait until the entire project is finished to push. This is a work
  checkpoint policy, not a background scheduled automation.
- Stage only intended changes. Preserve unrelated/untracked work; never force
  push or reset someone else's changes to make a checkpoint succeed.
- Keep credentials, environment files, and private raw data out of commits.
- Archive experiment evidence with provenance and checksums when appropriate.
- Confirm push success. If it fails, report the failure and retain the local
  commit; never imply GitHub is up to date when it is not.
- In `PROJECT_HANDOFF.md`, record current branch, completed work, decisions,
  important evidence, next action, and what was/was not tested. Use repository
  paths and durable links rather than relying on chat memory or local paths.

## Notebook input delivery

For inputs already archived on GitHub, download them automatically from a
pinned commit and verify integrity. Do not ask the user to upload the same
archive again. Clearly state CPU/T4 and the output archive name.

## Colab automation contract

The user runs Colab only as remote compute. Prepare data discovery, labels,
audits, manifests, notebook logic, and GitHub artifacts locally before handing
off a notebook.

- A delivered notebook must support `Runtime -> Run all` from a fresh Colab
  runtime without manual uploads, file pickers, per-row review clicks, copied
  repair cells, or editing Python.
- Download every reusable input automatically from an immutable GitHub commit,
  verify its SHA-256, reuse a valid cache, and fail with actionable diagnostics.
- Resolve interactive review and labeling locally before Colab. If a manual
  widget is useful, keep it optional and provide a deterministic automatic
  default with honest provenance.
- Colab performs only the expensive extraction, training, or evaluation and
  automatically downloads one clearly named output ZIP at the end.
- Test notebook JSON, parse every Python cell, dry-run all locally testable
  selection/manifest logic, and document anything that still requires Colab.
- After the user returns an output ZIP, verify it, archive it with checksums,
  analyze it locally, update the handoff, and push the checkpoint before making
  the next notebook.
