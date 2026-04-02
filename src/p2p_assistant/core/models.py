from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ChatMessage:
    order_id: str
    timestamp: Optional[datetime]
    sender: str  # mine | counterparty | system
    text: str = ""
    image_url: Optional[str] = None
    message_type: str = "text"  # text | image | system


@dataclass
class ParsedPaymentInfo:
    beneficiary_name: Optional[str] = None
    account_number: Optional[str] = None
    phone_number: Optional[str] = None
    has_barcode_or_qr: bool = False
    has_proof_image: bool = False
    transfer_instruction_text: Optional[str] = None
    confidence: float = 0.0
    notes: str = ""


@dataclass
class OrderRecord:
    platform: str
    exchange_account: str
    order_id: str
    status: str
    order_type: Optional[str]
    fiat_amount_raw: str
    fiat_amount_normalized: Decimal
    fiat_currency: str
    unit_price_raw: Optional[str] = None
    quantity_raw: Optional[str] = None
    fee_raw: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: Optional[datetime] = None
    counterparty_nickname: Optional[str] = None
    counterparty_real_name: Optional[str] = None
    detail_url: Optional[str] = None
    parsed_payment: ParsedPaymentInfo = field(default_factory=ParsedPaymentInfo)
    reviewed: bool = False


@dataclass
class ReceivingAccount:
    id: Optional[int]
    beneficiary_name: str
    account_number: str
    phone_number: Optional[str]
    barcode_path: Optional[str]
    currency: str
    daily_cap: Decimal
    assigned_total: Decimal
    is_active: bool = True
    priority: int = 0


@dataclass
class AssignmentDecision:
    account_id: Optional[int]
    reason: str
    accepted: bool
