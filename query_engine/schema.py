SCHEMA_DESCRIPTION = """
Table: customers
- customer_id (INTEGER, primary key)
- name (TEXT) — customer's individual contact name
- company_name (TEXT)
- segment (TEXT) — one of: 'SMB', 'Enterprise'
- city (TEXT)
- credit_limit (REAL) — in INR
- onboarded_date (TEXT) — format YYYY-MM-DD

Table: invoices
- invoice_id (INTEGER, primary key)
- customer_id (INTEGER) — references customers.customer_id
- invoice_date (TEXT) — format YYYY-MM-DD
- due_date (TEXT) — format YYYY-MM-DD
- amount (REAL)
- status (TEXT) — one of: 'paid', 'unpaid', 'overdue'
- currency (TEXT)

Table: payments
- payment_id (INTEGER, primary key)
- invoice_id (INTEGER) — references invoices.invoice_id
- payment_date (TEXT) — format YYYY-MM-DD
- amount_paid (REAL)
- payment_method (TEXT) — one of: 'bank_transfer', 'card', 'cheque', 'upi'

Table: accounts
- account_id (INTEGER, primary key)
- account_name (TEXT)
- account_type (TEXT) — one of: 'bank', 'cash', 'credit'
- balance (REAL)

Table: transactions
- transaction_id (INTEGER, primary key)
- account_id (INTEGER) — references accounts.account_id
- date (TEXT) — format YYYY-MM-DD
- type (TEXT) — one of: 'inflow', 'outflow'
- category (TEXT)
- amount (REAL)
- linked_invoice_id (INTEGER) — references invoices.invoice_id
"""
