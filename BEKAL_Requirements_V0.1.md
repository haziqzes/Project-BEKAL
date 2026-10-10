# Project BEKAL — Requirements Specification V0.1

## 1. Functional Requirements

### FR-001 Receipt Upload
The system shall allow the user to select and upload a PDF receipt using a standard file picker.

### FR-002 PDF Type Support
The system shall support both:
- text-based PDFs, and
- scanned/image-based PDFs.

### FR-003 Extraction Strategy
The system shall attempt direct text extraction first when text is available. OCR/computer vision shall be used when direct extraction is unavailable or insufficient.

### FR-004 Receipt Metadata Extraction
The system shall attempt to extract:
- store name
- receipt date
- receipt/invoice number
- payment method
- subtotal
- discounts
- tax
- final total

Branch, street address, and geographic location are not required in V0.1.

### FR-005 Item Extraction
The system shall attempt to extract for each item:
- cleaned product name
- quantity
- unit
- unit price
- line total
- category

### FR-006 Product Normalization
The system shall attempt to convert abbreviated or messy receipt item names into cleaner human-readable names.

### FR-007 Category Assignment
The system shall assign an initial category to each product and allow the category to be edited.

Initial categories may include:
- Meat & Poultry
- Seafood
- Vegetables
- Fruit
- Dairy
- Eggs
- Rice & Grains
- Bread & Bakery
- Drinks
- Snacks
- Frozen Food
- Canned / Packaged Food
- Condiments
- Household
- Personal Care
- Other

### FR-008 Quantity / Unit Inference
The system shall infer quantity and unit where reasonably possible. Failure to infer these values shall not block receipt review.

### FR-009 Review Warning
The system shall flag uncertain rows/fields using a simple warning indicator such as `⚠` and confident fields using a simple positive indicator such as `✓` where useful.

### FR-010 Receipt Review Layout
The receipt review screen shall display:
- the original PDF, and
- the extracted structured table

side-by-side where practical.

### FR-011 Row Editing
Each item row shall include a dedicated edit/pen action. Activating it shall allow editing of that row.

### FR-012 Row Management
The user shall be able to:
- edit an existing row
- add a missing row
- delete an incorrect row
- change product name
- change quantity/unit
- change price values
- change category

### FR-013 Receipt Metadata Editing
The user shall be able to edit extracted receipt-level fields before saving.

### FR-014 Total Validation
The system shall compare calculated item totals against the extracted receipt total and warn when there is a mismatch.

### FR-015 Confirmation Before Save
The system shall require explicit user confirmation before permanently saving extracted data.

### FR-016 Manual Entry Fallback
If extraction fails, the system shall still display the original PDF and provide a manual-entry path.

### FR-017 Receipt Storage
The original receipt PDF shall be retained after confirmation.

The human-readable filename shall use:

`YYYY-MM-DD_<store>.<ext>`

The system shall also assign a unique internal receipt ID.

### FR-018 Duplicate Warning
The system shall warn the user when an uploaded receipt appears to be a duplicate. The user may decide whether to continue.

### FR-019 Saved Receipt Editing
The user shall be able to reopen and edit a previously saved receipt.

### FR-020 Receipt Deletion
Deleting a receipt shall remove both:
- the database record and associated item records, and
- the original saved PDF

after explicit confirmation.

### FR-021 Product Alias Memory
When the user corrects a normalized product name, BEKAL shall be able to remember the relationship between the source representation and the corrected product name for future receipts.

### FR-022 Dashboard
The V0.1 dashboard shall provide at minimum:
- total grocery/retail spending for the selected month
- receipt count
- top spending categories
- most frequently purchased items
- recent price history
- recent receipts

### FR-023 Month Selection
The dashboard shall default to the current month and allow simple month selection.

### FR-024 Receipt History
Receipt history shall display at minimum:
- date
- store
- item count
- total
- actions to view/edit/delete

Advanced filtering is not required in V0.1.

### FR-025 CSV Export
The system shall support two separate CSV exports:

1. `receipts.csv`
2. `items.csv`

### FR-026 Currency
V0.1 shall support MYR only.

### FR-027 Single User
V0.1 shall be designed for a single user. No login, registration, or multi-user permissions are required.

## 2. Non-Functional Requirements

### NFR-001 Local-first operation
Core functionality shall operate locally without requiring paid third-party services.

### NFR-002 Usability
The interface shall prioritize clarity, low visual clutter, and readable tables.

### NFR-003 Portability
The application shall be Docker-ready so it can move from a development PC to a future home-lab environment.

### NFR-004 Data Privacy
Real receipts, databases, credentials, exports, and user data shall never be committed to source control.

### NFR-005 Maintainability
Frontend, backend, storage, and extraction responsibilities should remain modular enough to be replaced or improved independently.

### NFR-006 Testability
Core receipt parsing, normalization, persistence, and export logic shall have automated tests.

### NFR-007 Portfolio readability
Project structure and documentation should be understandable by another developer reviewing the repository.

## 3. V0.1 Acceptance Test

A release candidate passes V0.1 when a user can complete this workflow successfully:

1. Start BEKAL locally.
2. Select a receipt PDF.
3. BEKAL extracts receipt and item data.
4. Uncertain rows are visibly flagged.
5. The original PDF and extracted data are visible together.
6. The user edits at least one item row.
7. BEKAL detects whether item totals match the receipt total.
8. The user confirms and saves the receipt.
9. The receipt appears in history.
10. The receipt contributes to monthly dashboard analytics.
11. The saved receipt can be reopened and edited.
12. The data can be exported to `receipts.csv` and `items.csv`.
13. The receipt can be deleted together with its stored file.
