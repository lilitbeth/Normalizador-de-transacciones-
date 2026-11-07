from typing import Any, Dict
from src.normalizer import TransactionNormalizer
from src.skills.base_skill import BaseSkill


class NormalizerSkill(BaseSkill):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name="transaction_normalizer",
            description="Convierte cargas heterogéneas al esquema bancario canónico.",
            version="1.1.0",
        )
        self.engine = TransactionNormalizer(config)

    def execute(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw_payload, dict):
            raise ValueError("El payload crudo debe ser un diccionario.")
        canonical = self.engine.normalize(raw_payload)
        return {
            "canonical_tx": canonical,
            "parse_errors": canonical.get("_parse_errors", []),
        }