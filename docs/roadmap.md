# Roadmap

BEKAL uses milestone boundaries deliberately. A useful idea is not automatically part of the current release.

## Released milestones

| Version | Status | Scope |
| --- | --- | --- |
| V0.1 | **Complete** | Receipt PDF intake, extraction/OCR, review, persistence, history/CRUD, dashboard, CSV export, testing, public-release safety |
| V0.2 | **Complete** | Tauri 2 Windows desktop shell, service lifecycle, private installed runtime, NSIS installer, owner-machine acceptance, public Windows release |

Current stable release: **v0.2.0**.

## Current project mode

BEKAL is currently in **post-release maintenance**.

Maintenance work can include:

- dependency/security advisory remediation;
- bug fixes;
- documentation improvements;
- installer/release quality improvements;
- test/CI reliability improvements;
- small accessibility/usability corrections that do not redefine product scope.

A new product milestone should be named and scoped before feature work begins.

## Near-term maintenance candidates

These are reasonable maintenance targets, not promises or fixed release dates:

1. Review and resolve dependency advisories using the smallest safe updates.
2. Improve installer signing/publisher reputation when practical.
3. Improve first-run diagnostics when Docker Desktop is unavailable or unhealthy.
4. Define and test a user-friendly backup/restore workflow for local receipt data.
5. Improve release automation while keeping owner-machine acceptance for runtime-sensitive changes.
6. Add additional synthetic parser/OCR regression fixtures where real-world receipt formats expose weaknesses.

## Future milestone candidates

These ideas require explicit scope/architecture decisions before implementation.

### Mobile / multi-device access

A smartphone cannot install the current Windows `.exe`.

The preferred future direction is likely a **client/server boundary** rather than attempting to run the full Windows Docker/PostgreSQL runtime on a phone:

```text
BEKAL local/home server
        │
        ├── Windows desktop client
        ├── mobile-friendly web/PWA client
        └── later native mobile client if justified
```

Before remote/mobile access becomes supported, BEKAL would need an accepted design for authentication, authorization, secure transport, network exposure, data ownership, and synchronization/conflict behavior.

### Multi-PC synchronization

V0.2 installations are independent. Shared household data or automatic synchronization would require a defined source of truth and conflict policy.

### Camera/photo receipt intake

Photo capture would require a new intake and image-processing path rather than being treated as the same feature as PDF upload.

### Embedded/no-Docker desktop runtime

Removing Docker Desktop would be a major architecture milestone because PostgreSQL and FastAPI lifecycle/persistence assumptions would change.

### Household accounts / authentication

Accounts, family profiles, and role permissions become relevant only if BEKAL moves beyond the supported local single-user model.

## Explicit backlog

The following remain outside the released V0.2 scope unless a future milestone explicitly adopts them:

- recipes and recipe recommendations;
- pantry inventory/depletion;
- grocery budget planning;
- meal/nutrition planning;
- live supermarket price crawling;
- store-price prediction;
- shopping-route optimization;
- barcode scanning;
- camera/photo capture;
- cloud accounts/sync;
- multi-user household profiles;
- notifications;
- HANA integration;
- multi-currency analytics;
- public hosted BEKAL service;
- required paid AI or cloud OCR.

## Scope-control rule

Before adding a feature, ask:

1. Is it required by the accepted milestone?
2. Does it satisfy an existing acceptance criterion?
3. Does it fix a blocker in the accepted milestone?

If all three answers are **no**, record/defer it instead of moving the finish line.

The historical V0.1 and V0.2 planning documents are preserved in [`archive/`](archive/README.md).
