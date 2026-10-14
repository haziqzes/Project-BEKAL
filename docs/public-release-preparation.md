# Public-release preparation

BEKAL V0.1 has a local release candidate and has completed reversible public-release preparation. The owner approved the MIT License and approved public release after final safety/CI verification.

## Completed checks

- Reviewed every path in the reachable Git history through the Phase 9 commit. Only source, design documents, configuration templates, and synthetic examples were tracked. No runtime receipt directory, database, real `.env`, export, dump, log, or private key file was found.
- Ran `python scripts/check_repository_safety.py --history` over all committed blobs. The check rejects private paths and recognizable private-key, GitHub, OpenAI, and AWS credential formats. It passed. This targeted scanner does not replace human review or a broader external secret scanner before publication.
- Reviewed `.gitignore`, Docker build contexts, Compose loopback port bindings, and `.env.example`. The template contains a clearly replaceable local password, not a user credential.
- Added a staged-file safety check, an optional local pre-commit hook, and read-only CI jobs for privacy, backend tests, and frontend build/audit.
- Added a wholly fabricated demo receipt PDF and reproducible generator under `examples/synthetic/`. Its extracted text was inspected before tracking.
- Confirmed creator credit in `README.md`. Runtime data and exported CSVs remain private and ignored.
- Owner selected the MIT License. `LICENSE` contains the approved text and creator copyright.
- Owner approved changing repository visibility to public after the final release gates pass.

## Final release gates

Before changing repository visibility:

- Re-run the full Git-history safety scan against the exact release commit.
- Re-run backend tests and dependency audit.
- Re-run frontend build and dependency audit.
- Confirm Docker Compose services remain healthy and loopback-bound.
- Inspect the final GitHub Actions/CI results for the release commit.
- Confirm no real receipt, runtime data, export, database content, `.env`, secret, credential, or private log is tracked.
- If screenshots or a demo video are prepared, inspect every frame for private data before sharing.

After all gates pass, the approved next action is to make `haziqzes/Project-BEKAL` public. Do not weaken any privacy, test, or dependency gate to reach publication.

To enable the local hook in this checkout, run `git config core.hooksPath .githooks`. The hook checks staged content. CI checks the full reachable Git history on every push and pull request. The hook and CI are defense in depth; human review is still required.
