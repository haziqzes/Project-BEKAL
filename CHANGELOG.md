# Changelog

All notable public BEKAL releases are documented here.

BEKAL uses milestone-oriented versioning during early development. Release tags are immutable snapshots; documentation on `master` may continue to improve after a release.

## [Unreleased]

### Documentation

- reorganized current documentation under `docs/`;
- moved historical V0.1/V0.2 planning records into `docs/archive/`;
- replaced the old draft/document-index presentation with a single current documentation index;
- added current installation, user, privacy/security, contribution, security-policy, and roadmap guidance;
- refreshed `AGENTS.md` for post-V0.2 maintenance.

No product/runtime behavior is changed by this documentation cleanup.

## [v0.2.0] — 2026-10-15

### Added

- Tauri 2 native Windows desktop shell around the existing React UI;
- packaged desktop API bridge to loopback FastAPI;
- conservative local PostgreSQL/FastAPI lifecycle ownership;
- private per-user installed runtime;
- generated private runtime `.env`;
- branded Windows executable and NSIS installer;
- Start Menu integration;
- Windows desktop CI build and installer verification;
- Rust formatting/check/dependency-audit release gates.

### Preserved

- FastAPI receipt-processing backend;
- PostgreSQL data model and migrations;
- local Tesseract OCR fallback;
- browser/Docker development mode;
- V0.1 receipt semantics and local-first privacy model.

### Corrected before release

Owner-machine acceptance found that an installed release launched from a shell whose current directory was the Project-BEKAL checkout could attach to the development Compose stack.

The release runtime resolver was corrected so release builds use the packaged per-user runtime unless `BEKAL_REPO_ROOT` is explicitly provided. Debug builds retain repository discovery for developer convenience.

### Owner acceptance

The corrected installer passed:

- native install/launch;
- repository-working-directory isolation;
- loopback-only FastAPI;
- non-host-exposed PostgreSQL;
- Dashboard and Receipt History;
- synthetic PDF upload/review/save/reopen;
- owned-service shutdown;
- relaunch persistence;
- uninstall data preservation;
- reinstall data restoration;
- ProductVersion `0.2.0`;
- Start Menu shortcut verification.

### Release artifact

```text
BEKAL_0.2.0_x64-setup.exe
SHA-256: E110665D77686000D872E9FD391C41AC40D21ECEC682CEB7381CD1C9A4895722
```

Release: <https://github.com/haziqzes/Project-BEKAL/releases/tag/v0.2.0>

## [v0.1] — 2026-10-14

V0.1 established the publicly released receipt-intelligence core.

### Added

- PDF-only receipt intake and original-PDF preview;
- selectable-text extraction with local OCR fallback;
- receipt metadata and line-item parsing;
- conservative normalization/category/quantity-unit preparation;
- editable review beside the original PDF;
- manual-entry fallback;
- explicit Confirm & Save;
- duplicate warning;
- PostgreSQL receipt/item/product/alias/category persistence;
- private original-PDF storage;
- Receipt History with view/edit/delete;
- monthly Dashboard;
- UTF-8 `receipts.csv` and `items.csv` exports;
- startup reconciliation for interrupted private-file operations;
- synthetic end-to-end regression coverage;
- public-repository privacy/history scanning and CI gates.

### Scope characteristics

- local-first;
- MYR-only;
- single-user;
- no authentication;
- no cloud synchronization;
- no mobile application;
- no required paid AI/cloud OCR.

Historical V0.1 planning and acceptance material is preserved under `docs/archive/v0.1/`.

[v0.2.0]: https://github.com/haziqzes/Project-BEKAL/releases/tag/v0.2.0
[v0.1]: https://github.com/haziqzes/Project-BEKAL/tree/b8de9173aa98e069015ef0d2769106e24bd1f748
