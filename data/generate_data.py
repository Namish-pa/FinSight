"""
FinSight synthetic data generator.

Populates finsight.db with realistic, internally-consistent finance data:
customers, invoices, payments, accounts, transactions.

Run with:  python generate_data.py
"""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker("en_IN")  # India-localized names/cities for realism
random.seed(42)        # reproducible dataset

DB_PATH = Path(__file__).parent / "finsight.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

N_CUSTOMERS = 120
N_ACCOUNTS = 10
N_INVOICES = 900
N_TRANSACTION_EXTRA = 1200  # transactions beyond the ones linked to invoices

TODAY = datetime(2026, 9, 4)  # anchor date so results are reproducible/explainable in a demo


def reset_db(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def gen_customers(conn):
    segments = ["SMB", "Enterprise"]
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        segment = random.choices(segments, weights=[0.7, 0.3])[0]
        onboarded = random_date(datetime(2023, 1, 1), TODAY)
        rows.append((
            i,
            fake.name(),
            fake.company(),
            segment,
            fake.city(),
            round(random.uniform(50_000, 2_000_000), 2),
            onboarded.strftime("%Y-%m-%d"),
        ))
    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)", rows
    )
    return rows


def gen_accounts(conn):
    types = ["bank", "bank", "cash", "credit"]
    rows = []
    for i in range(1, N_ACCOUNTS + 1):
        acc_type = random.choice(types)
        starting_balance = round(random.uniform(200_000, 5_000_000), 2)
        rows.append((i, f"{fake.company()} - {acc_type.title()} A/C", acc_type, starting_balance))
    conn.executemany(
        "INSERT INTO accounts VALUES (?, ?, ?, ?)", rows
    )
    return rows


def gen_invoices(conn, customers):
    rows = []
    for i in range(1, N_INVOICES + 1):
        customer_id = random.choice(customers)[0]
        invoice_date = random_date(datetime(2025, 1, 1), TODAY - timedelta(days=1))
        due_date = invoice_date + timedelta(days=random.choice([15, 30, 45, 60]))
        amount = round(random.uniform(5_000, 400_000), 2)

        # Status logic: consistent with due_date vs TODAY
        if due_date > TODAY:
            status = random.choices(["unpaid", "paid"], weights=[0.6, 0.4])[0]
        elif (TODAY - due_date).days <= 5:
            status = random.choices(["paid", "unpaid", "overdue"], weights=[0.5, 0.3, 0.2])[0]
        else:
            status = random.choices(["paid", "overdue"], weights=[0.55, 0.45])[0]

        rows.append((i, customer_id, invoice_date.strftime("%Y-%m-%d"),
                     due_date.strftime("%Y-%m-%d"), amount, status, "INR"))
    conn.executemany(
        "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?)", rows
    )
    return rows


def gen_payments(conn, invoices):
    """Every 'paid' invoice gets exactly one full payment (keeps demo queries clean)."""
    methods = ["bank_transfer", "card", "cheque", "upi"]
    rows = []
    payment_id = 1
    for inv in invoices:
        invoice_id, _, invoice_date, due_date, amount, status, _ = inv
        if status == "paid":
            due_dt = datetime.strptime(due_date, "%Y-%m-%d")
            inv_dt = datetime.strptime(invoice_date, "%Y-%m-%d")
            pay_upper_bound = min(due_dt, TODAY)
            if pay_upper_bound <= inv_dt:
                pay_upper_bound = inv_dt + timedelta(days=1)
            payment_date = random_date(inv_dt, pay_upper_bound)
            rows.append((payment_id, invoice_id, payment_date.strftime("%Y-%m-%d"),
                         amount, random.choice(methods)))
            payment_id += 1
    conn.executemany(
        "INSERT INTO payments VALUES (?, ?, ?, ?, ?)", rows
    )
    return rows


def gen_transactions(conn, accounts, invoices, payments):
    categories_out = ["payroll", "rent", "utilities", "vendor_payment", "software_subscription", "travel"]
    categories_in = ["customer_payment", "interest_income", "other_income"]
    rows = []
    tx_id = 1

    # 1) A transaction for every payment (inflow, linked to the invoice)
    invoice_map = {inv[0]: inv for inv in invoices}
    for pay in payments:
        payment_id, invoice_id, payment_date, amount_paid, _ = pay
        account_id = random.choice(accounts)[0]
        rows.append((tx_id, account_id, payment_date, "inflow",
                     "customer_payment", amount_paid, invoice_id))
        tx_id += 1

    # 2) Extra unrelated transactions (operating expenses, misc income) for realism
    for _ in range(N_TRANSACTION_EXTRA):
        account_id = random.choice(accounts)[0]
        date = random_date(datetime(2025, 1, 1), TODAY)
        tx_type = random.choices(["inflow", "outflow"], weights=[0.3, 0.7])[0]
        category = random.choice(categories_in) if tx_type == "inflow" else random.choice(categories_out)
        amount = round(random.uniform(2_000, 300_000), 2)
        rows.append((tx_id, account_id, date.strftime("%Y-%m-%d"), tx_type, category, amount, None))
        tx_id += 1

    conn.executemany(
        "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)", rows
    )
    return rows


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    reset_db(conn)

    customers = gen_customers(conn)
    accounts = gen_accounts(conn)
    invoices = gen_invoices(conn, customers)
    payments = gen_payments(conn, invoices)
    transactions = gen_transactions(conn, accounts, invoices, payments)

    conn.commit()

    print(f"Inserted: {len(customers)} customers, {len(accounts)} accounts, "
          f"{len(invoices)} invoices, {len(payments)} payments, {len(transactions)} transactions")

    # quick sanity checks
    cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) FROM invoices GROUP BY status")
    print("Invoice status breakdown:", cur.fetchall())

    cur.execute("""
        SELECT COUNT(*) FROM invoices i
        LEFT JOIN payments p ON i.invoice_id = p.invoice_id
        WHERE i.status = 'paid' AND p.payment_id IS NULL
    """)
    orphaned_paid = cur.fetchone()[0]
    print(f"Paid invoices missing a payment record (should be 0): {orphaned_paid}")

    conn.close()


if __name__ == "__main__":
    main()
