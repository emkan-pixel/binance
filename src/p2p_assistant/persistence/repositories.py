from __future__ import annotations

import sqlite3
from datetime import datetime

from p2p_assistant.core.models import OrderRecord


class LogRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, level: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO app_logs(level, message, created_at) VALUES (?, ?, ?)",
            (level, message, datetime.utcnow().isoformat()),
        )
        self.conn.commit()


class OrderRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert(self, order: OrderRecord) -> None:
        self.conn.execute(
            """
            INSERT INTO orders(
                platform, exchange_account, order_id, status, order_type,
                fiat_amount_raw, fiat_amount_normalized, fiat_currency,
                unit_price_raw, quantity_raw, fee_raw, payment_method,
                detail_url, parsed_account_number, parsed_beneficiary_name,
                parsed_phone_number, has_barcode_qr, has_proof_image,
                parsing_confidence, parsing_notes, reviewed, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(platform, order_id) DO UPDATE SET
                status=excluded.status,
                fiat_amount_raw=excluded.fiat_amount_raw,
                fiat_amount_normalized=excluded.fiat_amount_normalized,
                fiat_currency=excluded.fiat_currency,
                parsed_account_number=excluded.parsed_account_number,
                parsed_beneficiary_name=excluded.parsed_beneficiary_name,
                parsed_phone_number=excluded.parsed_phone_number,
                has_barcode_qr=excluded.has_barcode_qr,
                has_proof_image=excluded.has_proof_image,
                parsing_confidence=excluded.parsing_confidence,
                parsing_notes=excluded.parsing_notes,
                reviewed=excluded.reviewed,
                scraped_at=excluded.scraped_at
            """,
            (
                order.platform,
                order.exchange_account,
                order.order_id,
                order.status,
                order.order_type,
                order.fiat_amount_raw,
                str(order.fiat_amount_normalized),
                order.fiat_currency,
                order.unit_price_raw,
                order.quantity_raw,
                order.fee_raw,
                order.payment_method,
                order.detail_url,
                order.parsed_payment.account_number,
                order.parsed_payment.beneficiary_name,
                order.parsed_payment.phone_number,
                int(order.parsed_payment.has_barcode_or_qr),
                int(order.parsed_payment.has_proof_image),
                order.parsed_payment.confidence,
                order.parsed_payment.notes,
                int(order.reviewed),
                datetime.utcnow().isoformat(),
            ),
        )
        self.conn.commit()
