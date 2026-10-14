# Project BEKAL — Data, Privacy & Repository Safety V0.1

## 1. Core Rule

> Source code may become public. User data must remain private.

## 2. Sensitive / Private Data

The following must never be committed to Git:

- real receipt PDFs
- receipt images
- PostgreSQL data directories
- database dumps
- CSV exports containing real user data
- local logs containing receipt contents
- OCR caches derived from real receipts
- `.env` files
- passwords
- API keys
- credentials
- secrets
- local backups

## 3. Public-Safe Data

Allowed repository content may include:

- synthetic receipts created for testing
- fake/demo datasets
- anonymized sample screenshots that contain no real personal or transaction data
- database schemas/migrations
- parser code
- normalization rules
- documentation

## 4. Source Control Strategy

`.gitignore` is considered part of the security model.

Suggested baseline:

```gitignore
# Private data
data/
private/
uploads/
receipts/
receipt_images/
ocr_output/
ocr_cache/
exports/
backups/
snapshots/
user_data/

# Databases / dumps
*.db
*.sqlite
*.sqlite3
*.sql
*.dump
*.backup

# Secrets
.env
.env.*
!.env.example
secrets/
credentials/
keys/
*.pem
*.key
*.p12
*.pfx

# Local config
config.local.*
settings.local.*
*.local.json
*.local.yaml
*.local.yml

# Generated / temp
cache/
.cache/
tmp/
temp/
logs/
*.log

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Node
node_modules/
dist/
build/

# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db
```

## 5. Defense in Depth

Before public release, BEKAL should use several layers:

```text
.gitignore
   ↓
pre-commit checks
   ↓
secret scanning
   ↓
CI validation
   ↓
human review
```

## 6. Test Data Policy

Real receipts shall not be used as committed test fixtures.

Preferred order:
1. Synthetic receipts
2. Artificially generated PDFs
3. Sanitized examples only when there is a strong reason and no identifying data remains

## 7. Receipt Storage

Confirmed receipt PDFs should live in a private runtime directory/volume that is not part of the repository.

Example:

```text
/runtime-data/
└── receipts/
    └── 2026/
        └── 10/
            └── 2026-10-10_lotus.pdf
```

## 8. Public Release Gate

The repository shall remain private until all are complete:

- repository cleanup
- `.gitignore` review
- commit-history review
- secret scan
- synthetic demo dataset ready
- privacy documentation ready
- license chosen
- screenshots/demo content verified safe

## 9. Current Authentication Position

No authentication is required in V0.1 because the intended deployment is local and single-user.

If network exposure is introduced later, authentication must be reviewed before that deployment model is considered safe.
