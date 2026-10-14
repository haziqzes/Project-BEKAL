# Synthetic examples

Only wholly fabricated receipt fixtures belong here. No real household receipt or transaction data should be committed.

`demo_receipt.pdf` is wholly fabricated. Select it in the local UI to try intake, extraction, review, saving, the dashboard, history, and CSV export. No real merchant, account, or transaction data is included. To recreate it, install the backend development dependencies (`python -m pip install -e '.[dev]'` from `backend/`) and run `python examples/synthetic/create_demo.py` from the repository root.
