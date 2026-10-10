# BEKAL

**BEKAL** is a local-first receipt intelligence platform created by **Wan Mohamad Haziq Mirza**.

The first release focuses on one job: turning receipt PDFs into clean, editable, structured data that can be stored, reviewed, analyzed, and exported.

> Upload → Extract → Review → Save → Analyze → Export

## Current Status

BEKAL is currently in early private development. The repository is intended to become public later after the project passes privacy/security review, documentation cleanup, and license selection.

## V0.1 Scope

BEKAL V0.1 aims to support:

- PDF receipt upload
- direct PDF text extraction where available
- OCR fallback for scanned/image PDFs
- store/date/receipt metadata extraction
- item-level extraction
- product-name normalization
- editable categories
- quantity/unit inference where possible
- simple review/confidence warnings
- side-by-side PDF and structured table review
- row-level editing
- receipt total validation
- manual-entry fallback
- duplicate warnings
- receipt history
- basic monthly analytics
- remembered product aliases from user corrections
- CSV export

## Not V0.1

The following are intentionally deferred:

- recipes
- pantry tracking
- grocery budgeting
- meal planning
- store price crawling
- price prediction
- mobile app
- multi-user accounts
- login/authentication
- cloud sync
- HANA integration

These may become future BEKAL capabilities, but they do not move the V0.1 finish line.

## Planned Stack

- **Frontend:** React + TypeScript
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **Deployment:** Docker-ready local development
- **Currency:** MYR for V0.1
- **Input:** PDF receipts
- **Export:** CSV

## Privacy Philosophy

BEKAL follows a simple rule:

> **Code may become public. Household data remains private.**

Real receipts, databases, exports, credentials, and private runtime data must never be committed to the repository. Public examples and tests should use synthetic data.

## Creator

Created by **Wan Mohamad Haziq Mirza** as a learning, engineering, and portfolio project.

## License

Not selected yet. The repository remains private while licensing options are evaluated.
