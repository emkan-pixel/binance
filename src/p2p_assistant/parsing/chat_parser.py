from __future__ import annotations

import re
from typing import Iterable

from p2p_assistant.core.models import ChatMessage, ParsedPaymentInfo


ARABIC_NAME_RE = re.compile(r"[\u0600-\u06FF]{2,}(?:\s+[\u0600-\u06FF]{2,})+")
LATIN_NAME_RE = re.compile(r"\b[A-Z][A-Z\s]{3,}\b")
ACCOUNT_RE = re.compile(r"\b\d{8,20}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3})?0?\d{8,12}\b")


class ChatPaymentParser:
    def parse(self, messages: Iterable[ChatMessage]) -> ParsedPaymentInfo:
        info = ParsedPaymentInfo()
        mine = [m for m in messages if m.sender == "mine"]
        if not mine:
            info.notes = "No outbound payment details found."
            return info

        tail = mine[-15:]
        blob = "\n".join(m.text for m in tail if m.text)

        account_match = ACCOUNT_RE.search(blob)
        if account_match:
            info.account_number = account_match.group(0)

        phone_match = PHONE_RE.search(blob)
        if phone_match:
            info.phone_number = phone_match.group(0)

        name_match = ARABIC_NAME_RE.search(blob) or LATIN_NAME_RE.search(blob)
        if name_match:
            info.beneficiary_name = name_match.group(0).strip()

        info.has_barcode_or_qr = any(
            (m.image_url and ("qr" in (m.text or "").lower() or "barcode" in (m.text or "").lower()))
            or ("qr" in (m.text or "").lower() or "barcode" in (m.text or "").lower())
            for m in tail
        )
        info.has_proof_image = any(m.image_url for m in messages if m.sender == "counterparty")

        instruction_candidates = [
            m.text for m in tail
            if "receipt" in m.text.lower() or "proof" in m.text.lower() or "transfer" in m.text.lower()
        ]
        if instruction_candidates:
            info.transfer_instruction_text = instruction_candidates[-1]

        score = 0.0
        score += 0.4 if info.account_number else 0.0
        score += 0.25 if info.beneficiary_name else 0.0
        score += 0.15 if info.phone_number else 0.0
        score += 0.1 if info.has_barcode_or_qr else 0.0
        score += 0.1 if info.transfer_instruction_text else 0.0
        info.confidence = round(score, 2)

        if score < 0.5:
            info.notes = "Partial extraction; manual review recommended."
        return info
