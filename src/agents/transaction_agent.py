from typing import Any, Dict, List
from src.agents.base_agent import BaseAgent


class TransactionAgent(BaseAgent):

    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)

    def process(self, raw_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        processed_list: List[Dict[str, Any]] = []
        audit_trail: List[Dict[str, Any]] = []

        for raw in raw_transactions:
            # 1. Ejecutar skill de normalización
            norm_res = self.execute_skill("transaction_normalizer", raw_payload=raw)
            canonical = norm_res["canonical_tx"]

            # 2. Ejecutar skill de auditoría
            audit_res = self.execute_skill("transaction_auditor", canonical_tx=canonical)
            validated_tx = audit_res["audited_tx"]

            # 3. Si no es válida, invocar skill de remediación
            if not audit_res["is_valid"]:
                remediation = self.execute_skill("transaction_remediator", audited_tx=validated_tx)
                audit_trail.append(remediation)

            processed_list.append(validated_tx)

        return {
            "processed_transactions": processed_list,
            "remediation_trail": audit_trail,
            "agent_summary": {
                "agent_name": self.name,
                "role": self.role,
                "total_handled": len(raw_transactions),
                "skills_applied": list(self.skills.keys()),
            },
        }