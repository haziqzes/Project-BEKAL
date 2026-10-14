# Public-release preparation (repository remains private)

BEKAL V0.1 has a local release candidate. This checklist records reversible preparation only; publication and licensing require the owner's decision.

## Completed checks

- Reviewed every path in the reachable Git history through the Phase 9 commit. Only source, design documents, configuration templates, and synthetic examples were tracked. No runtime receipt directory, database, real `.env`, export, dump, log, or private key file was found.
- Ran `python scripts/check_repository_safety.py --history` over all committed blobs. The check rejects private paths and recognizable private-key, GitHub, OpenAI, and AWS credential formats. It passed. This targeted scanner does not replace human review or a broader external secret scanner before publication.
- Reviewed `.gitignore`, Docker build contexts, Compose loopback port bindings, and `.env.example`. The template contains a clearly replaceable local password, not a user credential.
- Added a staged-file safety check, an optional local pre-commit hook, and read-only CI jobs for privacy, backend tests, and frontend build/audit.
- Added a wholly fabricated demo receipt PDF and reproducible generator under `examples/synthetic/`. Its extracted text was inspected before tracking.
- Confirmed creator credit in `README.md`. Runtime data and exported CSVs remain private and ignored.

## Remaining owner decisions and release gates

- Owner chooses the software license and approves the exact license text before it is added.
- Owner explicitly approves any repository visibility change. The repository stays private until then.
- If screenshots or a demo video are prepared later, inspect every frame for private data before sharing.
- Re-run the history and dependency scans immediately before any public visibility change, and inspect CI results for the final commit.

To enable the local hook in this checkout, run `git config core.hooksPath .githooks`. The hook checks staged content. CI checks the full reachable Git history on every push and pull request. The hook and CI are defense in depth; human review is still required.
