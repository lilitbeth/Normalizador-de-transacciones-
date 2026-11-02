# 💳 Sistema de Normalización de Transacciones Heterogéneas

Sistema interactivo desarrollado en Python para procesar, normalizar y auditar transacciones financieras provenientes de diversas plataformas externas (Stripe, PayPal, Core Bancario, POS). Incluye validación estricta bajo un modelo de datos bancario, configuración desacoplada dual (técnica y funcional) y exploración mediante un panel interactivo con Streamlit.

---

## 📋 Resumen de Decisiones del Estudiante

En cumplimiento con los requerimientos de la actividad, las decisiones de diseño arquitectónico y de negocio fueron establecidas del siguiente modo:

1. **Modelo de Datos Normalizado (Estándar Bancario):**
   * `id` (`str`): Identificador único homologado.
   * `timestamp` (`str` en formato ISO 8601: `YYYY-MM-DDTHH:MM:SS`): Estándar temporal universal.
   * `amount` (`float`): Valor numérico estrictamente positivo (los centavos de fuentes como Stripe se convierten automáticamente a unidades).
   * `currency` (`str`): Código alfabético ISO 4217 en mayúsculas (`USD`, `EUR`, `GBP`, etc.).
   * `type` (`str`): Clasificación del flujo contable (`CREDIT` o `DEBIT`).
   * `status` (`str`): Estado canónico homologado (`COMPLETED`, `PENDING`, `FAILED`).
   * `source` (`str`): Plataforma emisora (`STRIPE`, `PAYPAL`, `CORE_BANCARIO`, `POS_TERMINAL`, `UNKNOWN_SOURCE`).
   * `is_valid` (`bool`): Indicador de consistencia operativa.
   * `validation_errors` (`list`): Listado de causales de fallo si no cumple las reglas.

2. **Criterio de Inconsistencias (Auditoría Completa):**
   * Ningún registro se descarta silenciosamente.
   * Los registros incompletos o con errores (fechas inválidas, monedas no soportadas, fallos de parseo de monto) preservan sus campos recuperables, se marcan como `is_valid: false` y se conservan junto a sus motivos de error para trazabilidad e inspección regulatoria.

3. **Configuración Desacoplada Dual:**
   * `config/rules.json`: Orientado a integración técnica automatizada y desarrolladores.
   * `config/rules.yaml`: Orientado a analistas de negocio y operadores no técnicos.
   * El sistema detecta y carga transparentemente cualquiera de los dos formatos.

4. **Interfaz Interactiva:**
   * Dashboard web con **Streamlit** que permite aplicar filtros dinámicos, examinar anomalías, calcular métricas en tiempo real y exportar los resultados normalizados.

---

## 📁 Estructura del Proyecto

```text
transacciones-normalizador/
│
├── config/
│   ├── rules.json              # Configuración técnica (JSON)
│   └── rules.yaml              # Configuración funcional/declarativa (YAML)
│
├── data/
│   └── raw_transactions.json   # Dataset heterogéneo con casos válidos e inconsistencias
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py        # Cargador unificado de reglas (JSON y YAML)
│   ├── normalizer.py           # Detección de origen y normalización de campos
│   ├── validator.py            # Validación de integridad y registro de auditoría
│   └── metrics.py              # Cálculo de métricas y acumulados
│
├── app.py                      # Interfaz interactiva en Streamlit
├── requirements.txt            # Dependencias del proyecto
├── NOTA_TECNICA.md             # Memoria técnica sobre diseño y uso de IA
└── README.md                   # Este archivo
```

---

## ⚙️ Requisitos Previos e Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/<tu-usuario>/<tu-repositorio>.git
cd <tu-repositorio>
```

### 2. Configurar entorno virtual (recomendado)

En **Linux / macOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

En **Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución del Sistema

Para iniciar el panel interactivo en tu navegador:

```bash
streamlit run app.py
```

Una vez ejecutado, la aplicación se abrirá en tu navegador predeterminado (usualmente en `http://localhost:8501`).

---

## 🖥️ Funcionalidades del Dashboard

* **Selector de Motor de Reglas:** Permite alternar en caliente entre `rules.json` y `rules.yaml`.
* **Carga de Datos Flexible:** Carga automáticamente el dataset de prueba incluido (`data/raw_transactions.json`) o permite subir cualquier archivo JSON propio desde la barra lateral.
* **Tarjetas KPI:** Visualización de registros procesados, porcentaje de transacciones válidas vs. inválidas y monedas activas.
* **Resumen Financiero:** Tablas con totales acumulados por divisa (únicamente de transacciones válidas) y recuento por estado de transacción.
* **Explorador Dinámico:** Filtro cruzado por validez (Todas, Válidas, Inválidas), divisa y estado.
* **Exportador de Auditoría:** Botón de descarga para obtener el resultado completo procesado en formato JSON.

---

## 📊 Reglas de Normalización Aplicadas

| Variable | Regla Implementada |
| :--- | :--- |
| **Montos (Stripe)** | División automática entre 100 si el origen suministra centavos enteros (`amount_cents`). |
| **Montos (Signo)** | Se toma el valor absoluto (`abs(monto)`), trasladando el sentido financiero al campo `type` (`CREDIT` o `DEBIT`). |
| **Fechas** | Parseo secuencial contra formatos admitidos (`YYYY-MM-DD`, `DD/MM/YYYY`, ISO 8601, etc.) y conversión final a `YYYY-MM-DDTHH:MM:SS`. |
| **Monedas Soportadas** | Conversión a mayúsculas y validación contra lista oficial: `USD`, `EUR`, `GBP`, `JPY`, `CAD`. |
| **Estados Homologados** | Mapeo canónico a `COMPLETED`, `PENDING` o `FAILED`. |

---
