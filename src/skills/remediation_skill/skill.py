from typing import Any, Dict
from src.skills.base_skill import BaseSkill


class RemediationSkill(BaseSkill):

    def __init__(self):
        super().__init__(
            name="transaction_remediator",
            description="Genera diagnósticos de remediación para transacciones inconsistentes.",
            version="1.0.0",
        )

    def execute(self, audited_tx: Dict[str, Any]) -> Dict[str, Any]:
        errors = audited_tx.get("validation_errors", [])
        raw = audited_tx.get("raw_payload", {})
        proposal: Dict[str, Any] = {}
        can_auto_recover = False

        for err in errors:
            if "Moneda no soportada" in err:
                curr = audited_tx.get("currency")
                if curr in ("US$", "$"):
                    proposal["currency"] = "USD"
                    can_auto_recover = True
                elif curr in ("€", "EURO"):
                    proposal["currency"] = "EUR"
                    can_auto_recover = True
            elif "Formato de fecha" in err:
                raw_date = raw.get("created") or raw.get("timestamp") or raw.get("fecha")
                proposal["suggested_fix_date"] = f"Re-parsear timestamp crudo: '{raw_date}'"
            elif "Identificador" in err:
                proposal["suggested_id"] = f"AUTOGEN_{hash(str(raw)) % 1000000}"

        return {
            "tx_id": audited_tx.get("id"),
            "can_auto_recover": can_auto_recover,
            "remediation_proposal": proposal,
            "original_errors": errors,
        }