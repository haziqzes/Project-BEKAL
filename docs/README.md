# BEKAL Documentation

This directory contains the current documentation for the latest `master` branch of BEKAL.

If you are installing or using the released Windows application, start with the user-facing documents. If you are changing the codebase, read the technical documents and `AGENTS.md` before making architectural or privacy-sensitive changes.

## Getting started

| Document | Purpose |
| --- | --- |
| [Installation](installation.md) | Download, verify, install, launch, upgrade, uninstall, and troubleshoot BEKAL V0.2 on Windows |
| [User guide](user-guide.md) | Receipt workflow, history, dashboard, exports, data behavior, and current limitations |
| [README](../README.md) | Public project overview and download entry point |

## Technical documentation

| Document | Purpose |
| --- | --- |
| [Architecture](architecture.md) | Current V0.2 components, runtime topology, data flow, lifecycle, and boundaries |
| [Development](development.md) | Local setup, browser mode, desktop mode, tests, audits, CI, and release workflow |
| [Privacy & Security](privacy-security.md) | Local-first privacy model, repository safety rules, network boundary, and sensitive-data policy |
| [Roadmap](roadmap.md) | Completed milestones, maintenance priorities, and explicitly uncommitted future candidates |
| [Changelog](../CHANGELOG.md) | Public release history |
| [Contributing](../CONTRIBUTING.md) | Contribution expectations and project boundaries |
| [Security policy](../SECURITY.md) | Supported version and safe vulnerability-reporting guidance |
| [AGENTS](../AGENTS.md) | Persistent operating contract for coding agents working on BEKAL |

## Current release

**BEKAL v0.2.0 — Windows Desktop**

- Release: <https://github.com/haziqzes/Project-BEKAL/releases/tag/v0.2.0>
- Installer: `BEKAL_0.2.0_x64-setup.exe`
- SHA-256: `E110665D77686000D872E9FD391C41AC40D21ECEC682CEB7381CD1C9A4895722`
- Runtime: Tauri 2 + React + FastAPI + PostgreSQL + local Tesseract OCR
- Docker Desktop: required in V0.2
- License: MIT

## Historical documents

Older planning, scope-freeze, release-candidate, and milestone documents are preserved under [`archive/`](archive/README.md).

The archive is useful when reviewing why a decision was made, but it is **not** the primary source for current installation or development instructions. Some archived documents intentionally contain language such as “private repository”, “future installer”, or “ready for merge” because they capture an earlier project state.

## Documentation rule

Current behavior belongs in the current documentation set above. Historical milestones belong in the archive. Avoid adding new root-level planning documents when an existing current document can be updated instead.
