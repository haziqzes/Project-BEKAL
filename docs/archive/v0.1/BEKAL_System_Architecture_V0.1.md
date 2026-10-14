# Project BEKAL — System Architecture V0.1

## 1. Architecture Overview

```text
┌─────────────────────────────┐
│       React + TypeScript     │
│           Frontend           │
│                             │
│ Dashboard / Upload / Review │
│ History / Edit / Export     │
└──────────────┬──────────────┘
               │ HTTP/JSON
               ▼
┌─────────────────────────────┐
│       FastAPI Backend        │
│                             │
│ API                         │
│ Receipt orchestration       │
│ Validation                  │
│ Product normalization       │
│ CSV export                  │
└───────┬──────────┬──────────┘
        │          │
        │          ▼
        │   ┌─────────────────┐
        │   │ Extraction Layer│
        │   │                 │
        │   │ PDF text parse  │
        │   │ OCR fallback    │
        │   │ CV if required  │
        │   └─────────────────┘
        │
        ▼
┌─────────────────────────────┐
│         PostgreSQL           │
│                             │
│ receipts                    │
│ receipt_items               │
│ products                    │
│ product_aliases             │
│ categories                  │
└─────────────────────────────┘

               +

┌─────────────────────────────┐
│      Local File Storage      │
│                             │
│ Original receipt PDFs       │
└─────────────────────────────┘
```

## 2. Major Components

### 2.1 Frontend
Responsibilities:
- PDF file selection
- upload progress / processing state
- receipt preview
- editable item table
- review warnings
- confirm/save workflow
- receipt history
- dashboard
- CSV export trigger

### 2.2 Backend API
Responsibilities:
- receive uploads
- coordinate extraction
- normalize extracted data
- validate totals
- persist confirmed records
- retrieve history/dashboard data
- update/delete saved receipts
- export CSV

### 2.3 Extraction Layer
Processing order:

```text
PDF received
   ↓
Can usable embedded text be extracted?
   ├── Yes → direct text parsing
   └── No  → OCR / image extraction
                ↓
          structured candidate data
```

The extraction layer should return candidate data rather than directly writing to the permanent database.

### 2.4 Review Layer
Candidate extraction results remain temporary until the user confirms them.

```text
Extracted Candidate
      ↓
Review / Edit
      ↓
Confirm & Save
      ↓
Permanent Database + Receipt Storage
```

### 2.5 Database
Recommended core entities:

#### receipts
- id
- store_name
- receipt_date
- receipt_number
- payment_method
- subtotal
- discount_total
- tax_total
- final_total
- currency
- original_file_path
- created_at
- updated_at

#### receipt_items
- id
- receipt_id
- product_id
- display_name
- quantity
- unit
- unit_price
- line_total
- category_id
- review_flag

#### products
- id
- canonical_name
- default_category_id
- created_at

#### product_aliases
- id
- source_alias
- product_id
- created_at

#### categories
- id
- name

## 3. Receipt File Naming

Human-readable stored filename:

`YYYY-MM-DD_<store>.pdf`

An internal UUID or equivalent database identifier shall remain the authoritative unique identity.

If filename collisions occur, the system may append a short unique suffix without changing the visible receipt date/store convention.

## 4. Data Flow

```text
[Select PDF]
      ↓
[Temporary Upload]
      ↓
[Extract text / OCR]
      ↓
[Parse receipt]
      ↓
[Normalize product names]
      ↓
[Assign categories]
      ↓
[Infer qty/unit where possible]
      ↓
[Validate totals]
      ↓
[User review + row edits]
      ↓
[Confirm & Save]
      ↓
[PostgreSQL + Stored PDF]
      ↓
[Dashboard / History / CSV]
```

## 5. Deployment Model

### V0.1 Development

```text
Windows PC
│
├── Frontend
├── Backend
├── PostgreSQL
└── Local receipt storage
```

### Docker-ready Target

```text
Docker Compose
├── frontend
├── backend
└── postgres

Host-mounted private volume
└── receipt storage
```

Future home-lab migration should require configuration changes rather than architectural redesign.

## 6. Authentication Boundary

Authentication is intentionally outside V0.1 scope.

The API architecture should avoid tightly coupling business logic to user identity so authentication can be added later at the request/middleware boundary if required.

## 7. Architectural Boundary with HANA

BEKAL remains a standalone system.

Future HANA integration, if added, should happen through a defined API rather than by embedding BEKAL database logic directly into HANA.

## 8. Architecture Principle

**BEKAL V0.1 optimizes for one reliable receipt-processing loop, not maximum feature coverage.**
