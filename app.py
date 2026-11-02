import json
from pathlib import Path
import pandas as pd
import streamlit as st

from src.config_loader import ConfigLoader
from src.metrics import TransactionMetrics
from src.normalizer import TransactionNormalizer
from src.validator import TransactionValidator

st.set_page_config(
    page_title="Sistema de Normalización Financiera",
    page_icon="💳",
    layout="wide",
)

st.title("💳 Sistema de Normalización de Transacciones Heterogéneas")
st.caption(
    "Modelo Estándar Bancario | Auditoría Completa de Registros | Soporte Dual JSON/YAML"
)

# Barra lateral: Configuración y carga
st.sidebar.header("⚙️ Configuración del Motor")
config_source = st.sidebar.radio(
    "Origen de Reglas:",
    options=[
        "config/rules.json (Perfil Técnico)",
        "config/rules.yaml (Perfil Negocio)",
    ],
)
config_path = (
    "config/rules.json"
    if "rules.json" in config_source
    else "config/rules.yaml"
)

try:
    config = ConfigLoader.load(config_path)
    st.sidebar.success(f"Reglas cargadas desde `{config_path}`")
except Exception as e:
    st.sidebar.error(f"Error cargando reglas: {e}")
    st.stop()

uploaded_file = st.sidebar.file_uploader(
    "Subir archivo JSON de transacciones", type=["json"]
)

# Cargar dataset
if uploaded_file is not None:
    raw_data = json.load(uploaded_file)
else:
    default_data_path = Path("data/raw_transactions.json")
    if default_data_path.exists():
        with open(default_data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    else:
        st.warning("Carga un archivo JSON para procesar.")
        st.stop()

# Pipeline de Normalización y Validación
normalizer = TransactionNormalizer(config)
validator = TransactionValidator(config)

normalized_raw = [normalizer.normalize(tx) for tx in raw_data]
processed_data = validator.process_all(normalized_raw)
metrics = TransactionMetrics.calculate(processed_data)

# Métricas Principales (KPI Cards)
st.subheader("📊 Métricas de Procesamiento")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Procesadas", metrics["total_processed"])
valid_pct = (
    (metrics["valid_count"] / metrics["total_processed"]) * 100
    if metrics["total_processed"] > 0
    else 0.0
)
kpi2.metric("Válidas", metrics["valid_count"], f"{valid_pct:.1f}%")
kpi3.metric(
    "Inválidas (Auditadas)",
    metrics["invalid_count"],
    delta=f"-{metrics['invalid_count']}",
    delta_color="inverse",
)
kpi4.metric(
    "Monedas Activas",
    ", ".join(metrics["currency_totals"].keys()) or "Ninguna",
)

st.divider()

# Tablas de Resumen
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("##### 💵 Montos Totales Válidos por Moneda")
    if metrics["currency_totals"]:
        curr_df = pd.DataFrame(
            list(metrics["currency_totals"].items()),
            columns=["Moneda", "Total Acumulado"],
        )
        st.dataframe(curr_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay montos válidos acumulados.")

with col_right:
    st.markdown("##### 📌 Distribución por Estado")
    status_df = pd.DataFrame(
        list(metrics["status_breakdown"].items()),
        columns=["Estado", "Cantidad"],
    )
    st.dataframe(status_df, use_container_width=True, hide_index=True)

st.divider()

# Filtros Interactivos
st.subheader("🔍 Explorador de Auditoría y Transacciones")

f1, f2, f3 = st.columns(3)
with f1:
    filter_validity = st.selectbox(
        "Filtro de Auditoría:",
        options=["Todas", "Solo Válidas", "Solo Inválidas (Inconsistencias)"],
    )
with f2:
    all_currencies = sorted(
        list({tx["currency"] for tx in processed_data if tx["currency"]})
    )
    filter_currency = st.multiselect(
        "Filtrar por Moneda:", options=all_currencies, default=[]
    )
with f3:
    all_statuses = sorted(list({tx["status"] for tx in processed_data}))
    filter_status = st.multiselect(
        "Filtrar por Estado:", options=all_statuses, default=[]
    )

# Filtrado dinámico
filtered = processed_data
if filter_validity == "Solo Válidas":
    filtered = [tx for tx in filtered if tx["is_valid"]]
elif filter_validity == "Solo Inválidas (Inconsistencias)":
    filtered = [tx for tx in filtered if not tx["is_valid"]]

if filter_currency:
    filtered = [tx for tx in filtered if tx["currency"] in filter_currency]

if filter_status:
    filtered = [tx for tx in filtered if tx["status"] in filter_status]

display_rows = []
for tx in filtered:
    display_rows.append(
        {
            "ID": tx["id"],
            "Timestamp": tx["timestamp"],
            "Monto": tx["amount"],
            "Moneda": tx["currency"],
            "Tipo": tx["type"],
            "Estado": tx["status"],
            "Origen": tx["source"],
            "Válida": "✅ Sí" if tx["is_valid"] else "❌ No",
            "Errores Detectados": (
                " | ".join(tx["validation_errors"])
                if tx["validation_errors"]
                else "Ninguno"
            ),
        }
    )

df_display = pd.DataFrame(display_rows)
st.dataframe(df_display, use_container_width=True)

# Descarga de salida normalizada
st.subheader("💾 Exportación de Datos Normalizados")
json_output = json.dumps(processed_data, indent=2, ensure_ascii=False)
st.download_button(
    label="Descargar JSON Normalizado con Auditoría Completa",
    data=json_output,
    file_name="normalized_transactions_audit.json",
    mime="application/json",
)
