# Skill: transaction_normalizer

## Descripción
Estandariza cargas crudas de transacciones financieras heterogéneas (Stripe, PayPal, Core Bancario, POS) al modelo canónico ISO 8601 y tipos monetarios estandarizados.

## Entradas
- `raw_payload` (dict): Objeto JSON crudo de la transacción.

## Salidas
- `canonical_tx` (dict): Registro con `id`, `timestamp`, `amount`, `currency`, `type`, `status` y `source`.
- `parse_errors` (list[str]): Lista de inconsistencias iniciales detectadas en tipos y formatos.

## Restricciones
- Las transacciones de Stripe deben convertirse de centavos a unidades mayores (`/ 100`).
- Si una fecha no coincide con los formatos declarados, no se descarta; se traslada con advertencia.