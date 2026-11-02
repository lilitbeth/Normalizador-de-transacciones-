from typing import Any, Dict, List


class TransactionValidator:

    def __init__(self, config: Dict[str, Any]):
        self.supported_currencies = set(config.get("supported_currencies", []))

    def validate(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = list(tx.pop("_parse_errors", []))

        if tx["id"] in ("NO_ID", "", "None"):
            errors.append("Identificador único de transacción no encontrado")

        if tx["amount"] is None:
            errors.append("Monto indefinido o corrupto")
        elif tx["amount"] <= 0:
            errors.append("El monto debe ser estrictamente positivo")

        if tx["currency"] not in self.supported_currencies:
            errors.append(f"Moneda no soportada: {tx['currency']}")

        if not tx["timestamp"] or "T" not in str(tx["timestamp"]):
            errors.append("Formato de fecha inválido (requiere ISO 8601)")

        if tx["status"] not in ("COMPLETED", "PENDING", "FAILED"):
            errors.append(f"Estado desconocido: {tx['status']}")

        if tx["type"] not in ("CREDIT", "DEBIT"):
            errors.append(f"Tipo desconocido: {tx['type']}")

        tx["is_valid"] = len(errors) == 0
        tx["validation_errors"] = errors
        return tx

    def process_all(
        self, transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return [self.validate(tx) for tx in transactions]
