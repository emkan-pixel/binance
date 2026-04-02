from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook

from p2p_assistant.core.models import OrderRecord


class ExcelExporter:
    def export(self, orders: Iterable[OrderRecord], output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        wb = Workbook()
        ws1 = wb.active
        ws1.title = "Detailed Orders"

        ws1.append([
            "Platform", "Exchange Account", "Order ID", "Status", "Fiat Amount", "Currency",
            "Price", "Quantity", "Fee", "Payment Method", "Created Date", "Created Time",
            "Counterparty Nickname", "Counterparty Real Name", "Assigned Bank Account",
            "Assigned Beneficiary", "Assigned Phone", "Barcode/QR", "Proof Image",
            "Detail URL", "Parsing Confidence", "Notes", "Reviewed",
        ])

        orders_list = list(orders)
        for o in orders_list:
            dt = o.created_at
            ws1.append([
                o.platform, o.exchange_account, o.order_id, o.status, str(o.fiat_amount_raw), o.fiat_currency,
                o.unit_price_raw, o.quantity_raw, o.fee_raw, o.payment_method,
                dt.date().isoformat() if dt else None,
                dt.time().isoformat(timespec="seconds") if dt else None,
                o.counterparty_nickname, o.counterparty_real_name,
                o.parsed_payment.account_number, o.parsed_payment.beneficiary_name, o.parsed_payment.phone_number,
                "Yes" if o.parsed_payment.has_barcode_or_qr else "No",
                "Yes" if o.parsed_payment.has_proof_image else "No",
                o.detail_url, o.parsed_payment.confidence, o.parsed_payment.notes,
                "Yes" if o.reviewed else "No",
            ])

        ws2 = wb.create_sheet("Account Summary")
        ws2.append([
            "Bank Account Number", "Beneficiary Name", "Phone", "Currency", "Total Transferred",
            "Order Count", "Related Order IDs", "Notes",
        ])

        groups = defaultdict(lambda: {"total": 0, "orders": []})
        for o in orders_list:
            key = (
                o.parsed_payment.account_number or "UNKNOWN",
                o.parsed_payment.beneficiary_name or "UNKNOWN",
                o.parsed_payment.phone_number or "",
                o.fiat_currency,
            )
            groups[key]["total"] += float(o.fiat_amount_normalized)
            groups[key]["orders"].append(o.order_id)

        for key, value in groups.items():
            acc, name, phone, currency = key
            ws2.append([
                acc,
                name,
                phone,
                currency,
                value["total"],
                len(value["orders"]),
                ", ".join(value["orders"]),
                "",
            ])

        wb.save(output_path)
        return output_path
