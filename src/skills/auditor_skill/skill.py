from typing import Any, Dict
from src.validator import TransactionValidator
from src.skills.base_skill import BaseSkill


class AuditorSkill(BaseSkill):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="transaction_auditor",
            description="Audita reglas financieras de negocio y clasifica severidad.",
            version="1.0.0",
        )
        self.validator = TransactionValidator(config)

    def execute(self, canonical_tx: Dict[str, Any]) -> Dict[str, Any]:
        audited = self.validator.validate(canonical_tx)
        errors = audited.get("validation_errors", [])

        # Clasificación del nivel de riesgo técnico
        risk = "LOW"
        if not audited.get("is_valid", False):
            if any("Monto" in e or "Moneda" in e for e in errors):
                risk = "HIGH"
            else:
                risk = "MEDIUM"

        audited["risk_level"] = risk
        return {
            "audited_tx": audited,
            "is_valid": audited.get("is_valid", False),
            "risk_level": risk,
            "errors": errors,
        }