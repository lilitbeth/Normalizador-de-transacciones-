from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Tuple


class TransactionNormalizer:

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.status_map = {
            k.lower(): v for k, v in config.get("status_mapping", {}).items()
        }
        self.type_map = {
            k.lower(): v for k, v in config.get("type_mapping", {}).items()
        }
        self.date_formats = config.get("date_formats", [])
        self.supported_currencies = set(config.get("supported_currencies", []))

    def detect_source(self, raw: Dict[str, Any]) -> str:
        if "charge_id" in raw or raw.get("source_system") == "stripe":
            return "STRIPE"
        if "txn_id" in raw or raw.get("source_system") == "paypal":
            return "PAYPAL"
        if "referencia" in raw or raw.get("source_system") == "core_bancario":
            return "CORE_BANCARIO"
        if "ticket_num" in raw or raw.get("source_system") == "pos_terminal":
            return "POS_TERMINAL"
        return "UNKNOWN_SOURCE"

    def parse_date(self, raw_date: Any) -> Tuple[Optional[str], Optional[str]]:
        if not raw_date:
            return None, "Fecha no proporcionada"
        raw_str = str(raw_date).strip()
        for fmt in self.date_formats:
            try:
                dt = datetime.strptime(raw_str, fmt)
                return dt.strftime("%Y-%m-%dT%H:%M:%S"), None
            except ValueError:
                continue
        return raw_str, f"Formato de fecha no reconocido: {raw_str}"

    def parse_amount(
        self, raw_val: Any, source: str
    ) -> Tuple[Optional[float], Optional[str]]:
        if raw_val is None:
            return None, "Monto ausente"
        try:
            val_dec = Decimal(str(raw_val).strip())
            if source == "STRIPE":
                val_dec = val_dec / Decimal("100")
            return float(abs(val_dec)), None
        except (InvalidOperation, ValueError):
            return None, f"Monto no convertible a número: {raw_val}"

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        source = self.detect_source(raw)

        raw_id = (
            raw.get("charge_id")
            or raw.get("txn_id")
            or raw.get("referencia")
            or raw.get("ticket_num")
            or raw.get("id")
        )
        norm_id = str(raw_id).strip() if raw_id else "NO_ID"

        raw_date = (
            raw.get("created")
            or raw.get("payment_date")
            or raw.get("fecha_operacion")
            or raw.get("timestamp")
            or raw.get("fecha")
        )
        norm_date, date_err = self.parse_date(raw_date)

        raw_amount = (
            raw.get("amount_cents")
            if source == "STRIPE"
            else (
                raw.get("total_amount")
                or raw.get("monto")
                or raw.get("val")
                or raw.get("amount")
            )
        )
        norm_amount, amount_err = self.parse_amount(raw_amount, source)

        raw_curr = (
            raw.get("currency_code")
            or raw.get("currency")
            or raw.get("moneda")
            or raw.get("curr")
        )
        norm_curr = str(raw_curr).upper().strip() if raw_curr else "UNKNOWN"

        raw_status = (
            raw.get("status")
            or raw.get("payment_status")
            or raw.get("estado_transaccion")
            or raw.get("state")
            or raw.get("estado")
        )
        norm_status = self.status_map.get(
            str(raw_status).lower().strip(), "FAILED"
        )

        raw_type = (
            raw.get("movement")
            or raw.get("intent")
            or raw.get("tipo_operacion")
            or raw.get("entry_mode")
            or raw.get("tipo")
        )
        norm_type = self.type_map.get(str(raw_type).lower().strip(), "DEBIT")

        return {
            "id": norm_id,
            "timestamp": norm_date,
            "amount": norm_amount,
            "currency": norm_curr,
            "type": norm_type,
            "status": norm_status,
            "source": source,
            "is_valid": True,
            "validation_errors": [],
            "_parse_errors": [e for e in [date_err, amount_err] if e],
            "raw_payload": raw,
        }
