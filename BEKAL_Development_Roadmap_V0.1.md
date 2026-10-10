# Project BEKAL — Development Roadmap V0.1

## Phase 0 — Foundation

- Create private repository
- Add README draft
- Add `.gitignore`
- Add `.env.example`
- Establish React + TypeScript frontend
- Establish FastAPI backend
- Establish PostgreSQL
- Establish Docker Compose development environment
- Create synthetic demo receipt set

**Exit condition:** All core services start locally and repository safety rules are in place.

---

## Phase 1 — Receipt Intake

- PDF file picker
- Temporary upload handling
- PDF preview
- Basic file metadata
- Human-readable file naming strategy
- Internal receipt UUID generation

**Exit condition:** User can select and preview a PDF without saving it permanently.

---

## Phase 2 — Extraction Pipeline

- Detect embedded PDF text
- Direct text extraction path
- OCR fallback path
- Receipt metadata parsing
- Line-item parsing
- Candidate structured result

**Exit condition:** A synthetic receipt can become a structured candidate receipt.

---

## Phase 3 — Normalization & Review

- Product name cleaning
- Initial category assignment
- Quantity/unit inference
- Simple confidence/review indicator
- Total validation
- Side-by-side PDF/table layout
- Row edit button using pen icon
- Add/delete row
- Receipt metadata editing
- Manual-entry fallback

**Exit condition:** User can correct an imperfect extraction before saving.

---

## Phase 4 — Persistence

- PostgreSQL schema/migrations
- Save confirmed receipt
- Save receipt items
- Save original PDF
- Product alias table
- Learn aliases from corrections
- Duplicate warning

**Exit condition:** Confirmed receipts persist correctly and can be retrieved later.

---

## Phase 5 — History & CRUD

- Receipt history table
- View saved receipt
- Edit saved receipt
- Delete receipt + item records + PDF with confirmation

**Exit condition:** Saved receipts can be maintained safely.

---

## Phase 6 — Dashboard

- Current-month spending total
- Month selector
- Receipt count
- Top categories
- Most purchased items
- Recent price history
- Recent receipts

**Exit condition:** Receipt history produces useful basic analytics.

---

## Phase 7 — CSV Export

- `receipts.csv`
- `items.csv`
- UTF-8 safe output
- MYR numeric fields exported cleanly for Excel

**Exit condition:** Data opens cleanly in spreadsheet software.

---

## Phase 8 — Testing

Required automated test areas:
- parser unit tests
- normalization unit tests
- database tests
- duplicate-detection tests
- CSV export tests
- one end-to-end flow:
  upload → extract → edit → save → view → export

Coverage percentage is not the goal. Core workflow reliability is.

---

## Phase 9 — V0.1 Release Candidate

A V0.1 candidate is ready when all acceptance criteria in `BEKAL_Requirements_V0.1.md` pass.

No new feature may be added to the V0.1 scope after this point unless it fixes a blocker or directly satisfies an existing acceptance criterion.

---

## Phase 10 — Public Release Preparation

Only after V0.1 works:

1. Clean repository/documentation
2. Review `.gitignore`
3. Scan commit history for secrets/private data
4. Run security/privacy review
5. Prepare safe demo dataset
6. Choose license
7. Prepare screenshots/demo video
8. Add clear creator credit
9. Make repository public
10. Share as a portfolio/LinkedIn project

---

# Backlog — Explicitly Not V0.1

- Recipes
- Pantry inventory
- Grocery budget planning
- Meal planning
- Price forecasting
- External supermarket price data
- Barcode scanning
- Photo receipt capture
- Mobile application
- Authentication
- Multi-user household profiles
- Cloud sync
- Notifications
- HANA integration
- Multi-currency support

The backlog is allowed to grow. **V0.1 scope is not.**
