# Project BEKAL — Architecture Decision Record V0.1

## ADR-001 — Standalone Project
**Status:** Accepted

BEKAL shall be developed as a standalone system rather than as a HANA module.

**Reason:** Receipt intelligence has a distinct data model, workflow, and potential public/open-source audience. Separation prevents HANA from becoming an overloaded monolith.

---

## ADR-002 — Private Repository During Early Development
**Status:** Accepted

The repository shall remain private until BEKAL is ready for public release.

**Reason:** This allows the project structure, `.gitignore`, documentation, sample data, privacy controls, and license choice to mature before exposure.

---

## ADR-003 — Public/Open-Source Intent
**Status:** Planned, license undecided

BEKAL is intended to become a public repository later.

**Reason:** Public source can support portfolio development, learning, external review, reuse, and future contributions.

**Constraint:** No public release until security/privacy review and explicit license selection are completed.

---

## ADR-004 — React + TypeScript Frontend
**Status:** Accepted

**Reason:** Good fit for a clean table-heavy UI, strong ecosystem, and portfolio value.

---

## ADR-005 — FastAPI + Python Backend
**Status:** Accepted

**Reason:** Python is well suited for PDF parsing, OCR, data transformation, and future computer-vision experimentation. FastAPI provides a clear API layer with low overhead.

---

## ADR-006 — PostgreSQL Database
**Status:** Accepted

**Reason:** Provides a durable relational model and aligns with future Docker/home-lab deployment. The UI simplicity is independent of database choice.

---

## ADR-007 — Local-First Core
**Status:** Accepted

BEKAL core functionality shall not require paid external AI or cloud services.

**Reason:** The project should remain usable, educational, and low-cost.

---

## ADR-008 — PDF-Only Input for V0.1
**Status:** Accepted

V0.1 supports receipt PDFs only.

**Reason:** PDFs provide a more controlled starting point than low-resolution phone photos and reduce early computer-vision complexity.

---

## ADR-009 — Direct Text Extraction Before OCR
**Status:** Accepted

The system shall prefer embedded PDF text extraction and only use OCR/computer vision when required.

**Reason:** Direct extraction is generally faster, simpler, and less error-prone when text exists.

---

## ADR-010 — Original Receipt as Source of Truth
**Status:** Accepted

The original uploaded receipt PDF shall be retained. Raw OCR text does not need to be separately preserved in V0.1.

**Reason:** The original document remains available for manual verification and future reprocessing.

---

## ADR-011 — Human Confirmation Before Persistence
**Status:** Accepted

Extraction results shall not enter the permanent database until the user reviews and confirms them.

**Reason:** Early OCR/normalization errors should not silently contaminate the historical dataset.

---

## ADR-012 — Product Alias Memory
**Status:** Accepted

User corrections may be stored as product aliases for future normalization.

**Reason:** Provides useful learning behavior without requiring a complex AI training system.

---

## ADR-013 — No Authentication in V0.1
**Status:** Accepted

V0.1 is single-user and local. Login/authentication is deferred.

**Reason:** Authentication does not contribute to the core receipt-processing objective and would expand scope unnecessarily.

---

## ADR-014 — MYR Only in V0.1
**Status:** Accepted

**Reason:** Initial usage is Malaysia-focused. The schema may retain a currency field to avoid blocking later expansion.

---

## ADR-015 — CSV Export Only
**Status:** Accepted

BEKAL shall export `receipts.csv` and `items.csv` in V0.1.

**Reason:** CSV is sufficient for Excel/manual analysis without adding spreadsheet-formatting complexity.

---

## ADR-016 — V0.1 Finish-Line Protection
**Status:** Accepted

Any feature not directly required for receipt upload, extraction, review, storage, simple analysis, editing, deletion, or CSV export shall be deferred to backlog.

**Reason:** Prevent moving the finish line and uncontrolled feature expansion.
