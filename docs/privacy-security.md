# Privacy & Security

## Core rule

> **Source code may be public. User data must remain private.**

BEKAL is designed as a local-first receipt system. The current Windows release does not require a cloud account, paid AI provider, or cloud OCR service for its core workflow.

## Sensitive data

The following must not be committed to Git or posted in public issues/PRs:

- real receipt PDFs or images;
- receipt-derived OCR caches containing real data;
- PostgreSQL data directories or dumps;
- real CSV exports;
- logs containing private receipt contents;
- generated local `.env` files;
- passwords, access tokens, API keys, credentials, or private keys;
- private backups or user-specific runtime configuration.

## Public-safe data

The repository may contain:

- synthetic receipt fixtures;
- fake/demo datasets;
- anonymized screenshots with no private transaction data;
- schemas and migrations;
- parser/normalization code;
- tests that use synthetic data;
- documentation.

## Repository defenses

Repository safety uses defense in depth:

```text
.gitignore
   ↓
pre-commit safety hook
   ↓
repository safety/history scan
   ↓
dependency/security checks
   ↓
GitHub Actions CI
   ↓
human review
```

The history scanner is run with:

```powershell
python scripts/check_repository_safety.py --history
```

`.env.example` is an intentionally tracked, non-secret template and is allowed. Real `.env` and secret environment variants are not.

`.gitignore` and the repository safety script are security-relevant project files; do not weaken them just to make a build pass.

## Installed private runtime

The V0.2 installed runtime is under:

```text
%LOCALAPPDATA%\com.haziqzes.bekal\runtime
```

It includes the generated private `.env`, managed runtime files, and private receipt storage.

Confirmed PostgreSQL data is stored in the stable Docker named volume used by the packaged `bekal-desktop` Compose project.

Normal application uninstall preserves private data by design.

## Network boundary

The packaged backend binds only to:

```text
127.0.0.1:8000
```

Packaged PostgreSQL is not exposed to a host TCP port.

The desktop UI talks to the backend over loopback. The backend CORS policy allows expected Tauri application origins rather than allowing arbitrary origins.

## Authentication position

V0.2 is local and single-user, so it does not implement login/accounts/authentication.

That choice is valid only for the supported local topology.

If BEKAL is later exposed to a LAN, VPN-accessible household server, the public internet, or a multi-user environment, authentication, authorization, transport security, session handling, and remote-threat assumptions must be reviewed before that topology is considered supported.

## Receipt processing privacy

The original PDF is the source of truth.

Receipt extraction happens locally. BEKAL prefers embedded PDF text and uses local Tesseract OCR when necessary.

Extraction/review creates a temporary candidate first. Permanent PostgreSQL/PDF storage happens only after explicit confirmation.

Missing data remains unknown rather than being fabricated by a remote model or silently inferred.

## CSV exports

Exports are generated on demand and not retained by the backend after generation.

Downloaded CSV files contain private receipt data. Store them as private user files and do not add them to the repository.

## Multi-device and mobile security

V0.2 has no multi-device synchronization and no smartphone client.

A future mobile or remote client must not be implemented by simply exposing the current unauthenticated FastAPI service to a network. Remote access requires a new security architecture.

## Installer integrity

The current V0.2 Windows installer is unsigned. Verify its published SHA-256 before running it:

```text
E110665D77686000D872E9FD391C41AC40D21ECEC682CEB7381CD1C9A4895722
```

Official release:

<https://github.com/haziqzes/Project-BEKAL/releases/tag/v0.2.0>

## Dependency security

CI runs Python, npm, Rust, and repository-safety checks appropriate to the project. Dependency advisories should be reviewed and remediated as maintenance work without weakening release gates.

An advisory does not automatically justify a risky major dependency/architecture change; assess whether the affected code path is reachable, whether a safe update exists, and whether the fix preserves BEKAL's runtime behavior.

## Reporting a security problem

Do not include real receipts, credentials, private exports, or other sensitive household data in a public GitHub issue.

See the repository [Security Policy](../SECURITY.md) for responsible reporting guidance.
