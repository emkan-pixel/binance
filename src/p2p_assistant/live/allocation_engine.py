from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from p2p_assistant.core.models import AssignmentDecision, ReceivingAccount


class AllocationEngine:
    """Sequential capacity-based assignment engine."""

    def choose_account(self, amount: Decimal, accounts: Iterable[ReceivingAccount]) -> AssignmentDecision:
        sorted_accounts = sorted(
            [a for a in accounts if a.is_active],
            key=lambda a: a.priority,
        )
        for account in sorted_accounts:
            remaining = account.daily_cap - account.assigned_total
            if remaining >= amount:
                return AssignmentDecision(account_id=account.id, reason=f"Assigned to priority {account.priority}", accepted=True)
        return AssignmentDecision(account_id=None, reason="No account has sufficient remaining capacity.", accepted=False)
