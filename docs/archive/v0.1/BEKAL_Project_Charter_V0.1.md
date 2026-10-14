# Project BEKAL — Project Charter V0.1

## 1. Project Identity

**Project name:** BEKAL  
**Creator:** Wan Mohamad Haziq Mirza  
**Current repository status:** Private during development  
**Long-term intent:** Public/open-source release after security, privacy, documentation, and licensing review  
**Primary user for V0.1:** Haziq only  

## 2. Project Purpose

BEKAL is a local-first grocery receipt intelligence platform. Its first purpose is to convert grocery and retail receipt PDFs into clean, structured, editable data that can be stored, reviewed, analyzed, and exported.

BEKAL V0.1 is intentionally narrow. It is not yet a recipe engine, meal planner, pantry manager, budgeting assistant, or price-prediction platform.

## 3. Core V0.1 Goal

> Upload a receipt PDF → extract structured receipt and item data → review and correct the extracted table → save the original receipt and structured data → view simple spending/price analytics → export data to CSV.

## 4. Success Criteria

BEKAL V0.1 is considered successful when it can:

1. Accept text-based and scanned/image-based receipt PDFs.
2. Prefer direct PDF text extraction where available and fall back to OCR/computer vision when required.
3. Extract store name, receipt date, receipt/invoice number, payment method, subtotal, discounts, tax, total, and item-level data.
4. Clean/normalize product names and assign editable categories.
5. Infer quantity and unit where reasonably possible.
6. Flag uncertain fields/rows with simple review indicators.
7. Display the original receipt PDF beside the extracted table.
8. Allow row-level editing using a dedicated edit/pen action.
9. Validate extracted item totals against the receipt total.
10. Require user confirmation before permanent save.
11. Store the original PDF using a human-readable date + store filename and an internal unique receipt ID.
12. Allow saved receipts to be reopened, edited, and deleted.
13. Warn when a likely duplicate receipt is uploaded.
14. Remember corrected product aliases for future normalization.
15. Show a simple monthly dashboard and receipt history.
16. Export receipts and items as separate CSV files.
17. Run locally and be Docker-ready for future home-lab deployment.

## 5. V0.1 Non-Goals

The following are explicitly deferred:

- Recipe generation
- Pantry inventory management
- Grocery budgeting
- Meal planning
- Price prediction
- External store price crawling
- Mobile application
- Multi-user/family accounts
- Login/authentication
- Cloud sync
- Notifications
- Required external AI services
- Barcode scanning
- Advanced AI confidence scoring
- Multi-currency support
- Advanced filtering/search

Any new feature idea not required for the V0.1 success criteria goes to the backlog rather than changing the V0.1 finish line.

## 6. Guiding Principles

### 6.1 Local-first
The core system should work without requiring paid cloud APIs.

### 6.2 Private data, public-capable code
The repository may become public later, but real receipts, databases, credentials, exports, and personal data must remain private.

### 6.3 Simple UI
The interface should be calm, functional, easy to understand, and visually simple, following the same general simplicity philosophy as HANA.

### 6.4 Human-correctable extraction
BEKAL should never pretend extraction is perfect. The user must be able to review and fix results before saving.

### 6.5 Portfolio + learning project
BEKAL should remain technically credible and professionally documented while still being approachable and understandable. The creator should be clearly credited when the project is eventually released publicly.

## 7. Initial Technology Direction

- **Frontend:** React + TypeScript
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **Deployment:** Docker-ready local development
- **Currency:** MYR only for V0.1
- **Receipt input:** PDF only for V0.1
- **Export:** CSV only for V0.1

## 8. Release Sequence

After V0.1 functionality is complete:

1. Clean repository and documentation.
2. Perform security/privacy review.
3. Prepare screenshots/demo material.
4. Decide software license.
5. Make repository public only when ready.
6. Use the public project as a technical portfolio and LinkedIn showcase.

## 9. Scope Control Rule

**If a proposed feature does not directly help upload, extract, review, store, analyze, or export receipt data in V0.1, it belongs in the backlog.**
