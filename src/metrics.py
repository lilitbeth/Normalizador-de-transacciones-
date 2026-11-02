from collections import Counter
from typing import Any, Dict, List


class TransactionMetrics:

    @staticmethod
    def calculate(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(transactions)
        valid_count = sum(1 for tx in transactions if tx.get("is_valid", False))
        invalid_count = total - valid_count

        status_counter = Counter(
            tx.get("status", "UNKNOWN") for tx in transactions
        )

        currency_totals: Dict[str, float] = {}
        for tx in transactions:
            if tx.get("is_valid") and tx.get("amount") is not None:
                curr = tx.get("currency", "UNKNOWN")
                currency_totals[curr] = round(
                    currency_totals.get(curr, 0.0) + tx["amount"], 2
                )

        error_breakdown = Counter()
        for tx in transactions:
            for err in tx.get("validation_errors", []):
                error_breakdown[err] += 1

        return {
            "total_processed": total,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "status_breakdown": dict(status_counter),
            "currency_totals": currency_totals,
            "error_breakdown": dict(error_breakdown),
        }
