# Nota Técnica: Sistema de Normalización de Transacciones Heterogéneas

## 1. Esquema Normalizado Final (Estándar Bancario)
Se definió un modelo uniforme inspirado en arquitecturas transaccionales financieras:
- `id` (str): Identificador unívoco homologado del registro.
- `timestamp` (ISO 8601: `YYYY-MM-DDTHH:MM:SS`): Cronología unificada.
- `amount` (float positivo): Conversión de centavos enteros (Stripe) a unidades estándar y conversión de montos con signo a valor absoluto.
- `currency` (código ISO 4217 en mayúsculas): Divisa homologada.
- `type` (`CREDIT` o `DEBIT`): Clasificación del movimiento financiero.
- `status` (`COMPLETED`, `PENDING`, `FAILED`): Homologación canónica de estados.
- `source`: Trazabilidad del sistema emisor (`STRIPE`, `PAYPAL`, `CORE_BANCARIO`, `POS_TERMINAL`, `UNKNOWN_SOURCE`).
- `is_valid` (bool) y `validation_errors` (list): Campos de auditoría continua.

## 2. Reglas de Normalización y Auditoría Completa
- **Conversión de montos:** Ajuste específico por plataforma (división entre 100 para Stripe) y parseo seguro con `Decimal`.
- **Fechas:** Reconocimiento multidistributivo con fallback seguro a texto original con registro de inconsistencia.
- **Tratamiento de Inconsistencias:** Aplicación estricta de *Auditoría Completa*: ninguna transacción se descarta silenciosamente. Aquellas con errores estructurales quedan retenidas, señaladas con `is_valid=False` y con causales explícitas para inspección visual y regulatoria.
- **Configuración Desacoplada Dual:** Implementación paralela de `rules.json` para pipelines técnicos automatizados y `rules.yaml` para actualización ágil por personal de operaciones.

## 3. Uso Consciente de la Inteligencia Artificial
- **Propuestas de la IA adoptadas:** Separación modular en capas (`Normalizer`, `Validator`, `Metrics`, `ConfigLoader`) y maquetación reactiva en Streamlit.
- **Decisiones y ajustes propios del estudiante:**
  - Se descartó el filtrado/descarte silencioso sugerido por el modelo, implementando auditoría total con preservación de payload crudo.
  - Se diseñó el esquema canónico de tres estados y dos naturalezas contables (`CREDIT`/`DEBIT`).
  - Se implementó la coexistencia y homologación de formatos JSON y YAML en un único cargador unificado.
