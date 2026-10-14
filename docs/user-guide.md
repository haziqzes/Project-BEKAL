# User Guide

This guide describes the current BEKAL V0.2 receipt workflow.

## 1. Start BEKAL

Start Docker Desktop, then launch BEKAL from the Windows Start Menu. The native window appears after BEKAL's local backend and database are healthy.

## 2. Add a receipt PDF

BEKAL currently accepts receipt PDFs only.

The intake layer checks the file type, basic PDF validity, encryption/readability, and the 10 MiB upload limit before creating a temporary candidate.

The original PDF is kept visible during review because it remains the source of truth.

## 3. Extraction

BEKAL prefers selectable text already embedded in the PDF.

If the embedded text is not useful enough, BEKAL renders the pages locally and uses Tesseract OCR. No cloud OCR provider is required.

The candidate may contain:

- store name;
- receipt date;
- receipt/invoice number;
- payment method;
- subtotal;
- discount;
- tax;
- final total;
- item names;
- category suggestions;
- quantity and unit when supported;
- unit price and line total when available.

Missing information remains blank rather than being invented.

## 4. Review and correct

Before saving, compare the structured candidate with the original PDF.

You can:

- edit receipt metadata;
- edit individual rows;
- add rows;
- remove rows;
- correct product names;
- correct categories;
- correct quantities, units, prices, and totals;
- use manual entry when extraction is not useful.

BEKAL recalculates validation/review warnings as the candidate changes.

Extraction confidence is intentionally simple. The goal is to direct attention to uncertain information, not pretend that OCR/parser output is certain.

## 5. Confirm and save

Permanent storage happens only after explicit review and confirmation.

When you choose **Confirm & Save**, BEKAL validates the reviewed candidate and checks for likely duplicates. If a possible duplicate is found, you can compare the receipt and decide whether to continue.

A successful save writes structured data to PostgreSQL and copies the original receipt PDF into private local receipt storage.

The temporary candidate is removed after a successful save.

## 6. Receipt History

Open **Receipt History** to view saved receipts.

The history page provides the saved date, store, item count, and known total. From there you can reopen the structured record beside its private original PDF.

### Edit a saved receipt

Editing a saved receipt updates the structured database record. The original PDF is not replaced.

Row changes remain in the edit form until **Save changes** is used.

### Delete a saved receipt

Deletion requires explicit confirmation. BEKAL removes the saved receipt record, its item rows, and the associated private receipt PDF while using recovery safeguards for interrupted file/database operations.

## 7. Dashboard

The Dashboard is read-only and works by calendar month.

It can show:

- known receipt spending;
- receipts whose total is missing;
- receipt count;
- category spending from known item line totals;
- most-purchased products based on saved item rows;
- conservative comparable unit-price history;
- recent receipts.

BEKAL does not invent missing totals. Category totals can differ from receipt totals when item-level data is incomplete.

## 8. CSV export

Receipt History provides two on-demand exports:

- `receipts.csv`
- `items.csv`

Exports are generated from the currently saved PostgreSQL data and are not stored by the backend after generation.

The files use UTF-8 and keep unknown values blank. MYR monetary values are exported as decimal values without currency symbols. Potential spreadsheet formula triggers in text are escaped.

Downloaded exports contain private household data. Keep them outside the source repository.

## 9. Local data behavior

BEKAL V0.2 is single-user and local-first.

The installed runtime is under:

```text
%LOCALAPPDATA%\com.haziqzes.bekal\runtime
```

The packaged PostgreSQL database uses a Docker named volume. The Windows application and its private data are intentionally separated so normal application uninstall/reinstall does not erase receipt history.

Each computer currently has its own data. There is no automatic synchronization between two BEKAL installations.

## 10. Temporary candidates and recovery

Before confirmation, candidate PDFs are temporary. They expire and are cleaned up according to the backend candidate lifecycle.

Confirmed receipts are stored separately.

BEKAL also contains startup reconciliation for interrupted private-PDF save/delete operations. When a file is left in an uncertain state, the recovery path prefers preserving evidence for manual review rather than silently discarding private receipt data.

## Current limitations

V0.2 does not currently provide:

- Android or iOS applications;
- camera/photo receipt capture;
- barcode scanning;
- cloud sync;
- multi-PC synchronization;
- user accounts or authentication;
- multi-user household profiles;
- recipe generation;
- pantry inventory;
- grocery budgeting;
- live supermarket price crawling;
- multi-currency analytics;
- automated backup/restore UI;
- automatic application updates.

These are not hidden features; they are outside the released V0.2 scope.

## Need installation help?

See [Windows Installation](installation.md).

For privacy and network details, see [Privacy & Security](privacy-security.md).
