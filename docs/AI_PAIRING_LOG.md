# Bitácora de Supervisión Técnica y Trabajo con IA (AI Pairing Log)

## Objetivo
Documentar las interacciones de desarrollo con IA como herramienta de apoyo, justificando la intervención humana crítica y las decisiones de diseño arquitectónico.

---

### Interacción 1: Modularización de Normalizer y Validator
- **Sugerencia inicial de la IA:** Dejar las clases `TransactionNormalizer` y `TransactionValidator` como estaban y envolverlas en una sola función lambda dentro de Streamlit.
- **Criterio propio / Intervención humana:** Rechazado. Se optó por diseñar el patrón estándar de Skills heredando de `BaseSkill`, separando cada capacidad en su propio módulo con contratos `execute()` definidos y especificación formal `SKILL.md`.
- **Razón técnica:** Garantizar desacoplamiento, trazabilidad y extensibilidad hacia agentes más complejos.

---

### Interacción 2: Gestión de Transacciones Inválidas
- **Sugerencia inicial de la IA:** Descartar silenciosamente las transacciones con errores de fecha o moneda mediante un filtro `[tx for tx in data if is_valid]`.
- **Criterio propio / Intervención humana:** Modificado sustancialmente. En sistemas bancarios descartar registros vulnera las normas de auditoría. Se diseñó la `RemediationSkill` para sugerir correcciones conservando el registro crudo en `_parse_errors`.
- **Razón técnica:** Cumplimiento de la política institucional de no repudio y trazabilidad completa.

---

### Interacción 3: Parametrización del Agente
- **Sugerencia inicial de la IA:** Dejar los system prompts incrustados en cadenas constantes dentro de `src/agents/transaction_agent.py`.
- **Criterio propio / Intervención humana:** Extraído a `config/agent_config.yaml`.
- **Razón técnica:** Desacoplar la identidad y parámetros del agente del código de ejecución en Python.