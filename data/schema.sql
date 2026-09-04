-- FinSight database schema
-- Designed independently for the FinSight resume project (no relation to any prior/internship schema)

CREATE TABLE IF NOT EXISTS customers (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    company_name    TEXT NOT NULL,
    segment         TEXT NOT NULL CHECK (segment IN ('SMB', 'Enterprise')),
    city            TEXT NOT NULL,
    credit_limit    REAL NOT NULL,
    onboarded_date  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id      INTEGER PRIMARY KEY,
    account_name    TEXT NOT NULL,
    account_type    TEXT NOT NULL CHECK (account_type IN ('bank', 'cash', 'credit')),
    balance         REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id      INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL,
    invoice_date    TEXT NOT NULL,
    due_date        TEXT NOT NULL,
    amount          REAL NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('paid', 'unpaid', 'overdue')),
    currency        TEXT NOT NULL DEFAULT 'INR',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id      INTEGER PRIMARY KEY,
    invoice_id      INTEGER NOT NULL,
    payment_date    TEXT NOT NULL,
    amount_paid     REAL NOT NULL,
    payment_method  TEXT NOT NULL CHECK (payment_method IN ('bank_transfer', 'card', 'cheque', 'upi')),
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id      INTEGER PRIMARY KEY,
    account_id          INTEGER NOT NULL,
    date                TEXT NOT NULL,
    type                TEXT NOT NULL CHECK (type IN ('inflow', 'outflow')),
    category            TEXT NOT NULL,
    amount              REAL NOT NULL,
    linked_invoice_id   INTEGER,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (linked_invoice_id) REFERENCES invoices(invoice_id)
);
