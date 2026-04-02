from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exchange_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    exchange_account TEXT,
    profile_path TEXT NOT NULL,
    login_valid INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS receiving_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    beneficiary_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    phone_number TEXT,
    barcode_path TEXT,
    currency TEXT NOT NULL,
    daily_cap TEXT NOT NULL,
    assigned_total TEXT NOT NULL DEFAULT '0',
    is_active INTEGER NOT NULL DEFAULT 1,
    priority INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    exchange_account TEXT,
    order_id TEXT NOT NULL,
    status TEXT,
    order_type TEXT,
    fiat_amount_raw TEXT,
    fiat_amount_normalized TEXT,
    fiat_currency TEXT,
    unit_price_raw TEXT,
    quantity_raw TEXT,
    fee_raw TEXT,
    payment_method TEXT,
    created_at TEXT,
    counterparty_nickname TEXT,
    counterparty_real_name TEXT,
    detail_url TEXT,
    parsed_account_number TEXT,
    parsed_beneficiary_name TEXT,
    parsed_phone_number TEXT,
    has_barcode_qr INTEGER NOT NULL DEFAULT 0,
    has_proof_image INTEGER NOT NULL DEFAULT 0,
    parsing_confidence REAL,
    parsing_notes TEXT,
    reviewed INTEGER NOT NULL DEFAULT 0,
    scraped_at TEXT NOT NULL,
    UNIQUE(platform, order_id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    order_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    ts TEXT,
    text_body TEXT,
    image_url TEXT,
    message_type TEXT,
    scraped_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    order_id TEXT NOT NULL,
    account_id INTEGER,
    assigned_amount TEXT,
    currency TEXT,
    status TEXT,
    assigned_at TEXT NOT NULL,
    FOREIGN KEY(account_id) REFERENCES receiving_accounts(id)
);

CREATE TABLE IF NOT EXISTS proof_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    order_id TEXT NOT NULL,
    account_id INTEGER,
    local_path TEXT NOT NULL,
    source_url TEXT,
    saved_at TEXT NOT NULL,
    FOREIGN KEY(account_id) REFERENCES receiving_accounts(id)
);

CREATE TABLE IF NOT EXISTS exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    export_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn
