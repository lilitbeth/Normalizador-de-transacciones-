# Skill: transaction_remediator

## Descripción
Analiza transacciones declaradas como no válidas por la auditoría y genera una propuesta de recuperación asistida inspeccionando el payload crudo (`raw_payload`) antes de marcar la transacción como insalvable.

## Entradas
- `audited_tx` (dict): Transacción con fallas de validación.

## Salidas
- `remediation_proposal` (dict): Sugerencias concretas de corrección de campos.
- `can_auto_recover` (bool): Indica si la falla tiene solución unívoca.