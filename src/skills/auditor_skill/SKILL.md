# Skill: transaction_auditor

## Descripción
Evalúa registros canónicos contra las reglas de cumplimiento financiero (monedas soportadas, estados válidos, positividad de importes y consistencia de fecha).

## Entradas
- `canonical_tx` (dict): Transacción estandarizada por `transaction_normalizer`.

## Salidas
- `is_valid` (bool): Bandera de conformidad.
- `validation_errors` (list[str]): Errores normativos encontrados.
- `risk_level` (str): 'LOW', 'MEDIUM', 'HIGH' según la severidad del error.