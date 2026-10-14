# BEKAL V0.1 release candidate verification

Phase 9 checks the frozen acceptance workflow in `BEKAL_Requirements_V0.1.md` using synthetic receipt data. The project remains private and local-first.

| Acceptance step | Verification |
| --- | --- |
| Start locally; select a PDF | Compose health checks; intake API and PDF validation tests |
| Extract metadata and items | Embedded-text and scanned/local-OCR tests |
| Flag uncertain rows | Review normalization and warning tests; review UI indicators |
| Compare original PDF with candidate | Candidate preview API tests and side-by-side review UI |
| Edit a row; reconcile totals | Review tests and interactive row controls; reconciliation warnings |
| Confirm and save | Synthetic end-to-end test and persistence tests |
| See history; contribute to dashboard | End-to-end history and dashboard assertions; browser history/dashboard check |
| Reopen and edit a saved receipt | History update tests and end-to-end saved edit |
| Export both CSVs | End-to-end CSV assertions and dedicated export tests |
| Delete receipt and original PDF | End-to-end delete assertions and deletion failure tests |

Run the release candidate checks from the repository root:

```powershell
docker compose up --build -d
docker compose exec -T backend alembic upgrade head
docker compose exec -T backend pytest -q
docker compose ps
```

From `frontend/`, run `npm ci`, `npm run build`, and `npm audit --audit-level=low`. The backend dependency audit uses `pip-audit` in the backend container; its local `bekal-backend` package is not on PyPI and is skipped. Use only synthetic PDFs for manual review. Check `git status`, tracked paths, and `.gitignore` before any push.

Known limits within the accepted V0.1 scope: OCR quality varies with scan quality; uncertain data needs human review. The backend performs private-file reconciliation at startup after migrations. Interrupted saves can leave a PDF in ignored `.recovery/` for manual review. Files staged for deletion before Phase 8 lack a receipt identifier and need manual inspection if their PDF is missing. No authentication is provided in V0.1, so the local app ports remain bound to loopback only. No license or public repository status has been chosen.
