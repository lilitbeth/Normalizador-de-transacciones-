import json
from pathlib import Path
import pandas as pd
import streamlit as st
import yaml

from src.config_loader import ConfigLoader
from src.metrics import TransactionMetrics

# Componentes de la arquitectura agentica refactorizada
from src.agents.transaction_agent import TransactionAgent
from src.skills.normalizer_skill.skill import NormalizerSkill
from src.skills.auditor_skill.skill import AuditorSkill
from src.skills.remediation_skill.skill import RemediationSkill

st.set_page_config(
    page_title="Sistema de Normalización Financiera con Agentes",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Sistema de Auditoría y Normalización Financiera Asistido por Agentes")
st.caption(
    "Arquitectura Modular Agentica | Invocación Autónoma de Skills | Soporte Dual JSON/YAML"
)

# ---------------------------------------------------------
# 1. Barra Lateral: Configuración de Negocio y del Agente
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configuración del Motor")
config_source = st.sidebar.radio(
    "Origen de Reglas de Negocio:",
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
    st.sidebar.error(f"Error cargando reglas de negocio: {e}")
    st.stop()

# Cargar configuración de personalización del agente
agent_config_path = Path("config/agent_config.yaml")
if agent_config_path.exists():
    with open(agent_config_path, "r", encoding="utf-8") as f:
        agent_config = yaml.safe_load(f)
    st.sidebar.info(
        f"Agente Activo: **{agent_config.get('agent', {}).get('name', 'AuditBot')}**"
    )
else:
    st.sidebar.error("No se encontró `config/agent_config.yaml`.")
    st.stop()

uploaded_file = st.sidebar.file_uploader(
    "Subir archivo JSON de transacciones", type=["json"]
)

# ---------------------------------------------------------
# 2. Carga del Dataset
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 3. Inicialización del Agente y Registro de Skills Propias
# ---------------------------------------------------------
agent = TransactionAgent(agent_config)

# Inyección de dependencias y habilidades
agent.register_skill(NormalizerSkill(config))
agent.register_skill(AuditorSkill(config))
agent.register_skill(RemediationSkill())

# Procesamiento orquestado por el agente
execution_result = agent.process(raw_data)
processed_data = execution_result["processed_transactions"]
remediation_trail = execution_result["remediation_trail"]
agent_summary = execution_result["agent_summary"]

# Cálculo de métricas
metrics = TransactionMetrics.calculate(processed_data)

# ---------------------------------------------------------
# 4. Sección de Diagnóstico y Personalización del Agente
# ---------------------------------------------------------
st.subheader("🧠 Panel del Agente y Orquestación de Skills")

with st.expander("🔍 Ver Perfil, Instrucciones y Skills Activas del Agente", expanded=False):
    c_agent1, c_agent2 = st.columns([1, 2])
    with c_agent1:
        st.markdown(f"**Nombre:** `{agent_summary['agent_name']}`")
        st.markdown(f"**Rol:** {agent_summary['role']}")
        st.markdown(f"**Registros procesados:** {agent_summary['total_handled']}")
        st.markdown("**Skills Habilitadas:**")
        for sk in agent_summary["skills_applied"]:
            st.markdown(f"- 🛠️ `{sk}`")
    with c_agent2:
        st.markdown("**System Prompt / Instrucciones de Operación:**")
        st.info(agent.instructions.strip())

# Mostrar trazabilidad si se activó la skill de remediación
if remediation_trail:
    st.warning(
        f"⚠️ El agente activó de forma autónoma la skill `transaction_remediator` "
        f"para resolver inconsistencias en {len(remediation_trail)} transacciones."
    )
    with st.expander("🛠️ Ver Trazabilidad de Remediación y Propuestas Técnicas", expanded=True):
        remediation_rows = []
        for rem in remediation_trail:
            remediation_rows.append({
                "ID Transacción": rem.get("tx_id"),
                "Auto-Recuperable": "✅ Sí" if rem.get("can_auto_recover") else "❌ No",
                "Errores Originales": " | ".join(rem.get("original_errors", [])),
                "Propuesta de Remediación": json.dumps(rem.get("remediation_proposal", {}), ensure_ascii=False),
            })
        st.dataframe(pd.DataFrame(remediation_rows), use_container_width=True)
else:
    st.success("✅ Todas las transacciones cumplieron las reglas sin requerir remediación.")

st.divider()

# ---------------------------------------------------------
# 5. Métricas Principales (KPI Cards)
# ---------------------------------------------------------
st.subheader("📊 Métricas de Procesamiento Financiero")
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

# ---------------------------------------------------------
# 6. Tablas de Resumen
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 7. Filtros Interactivos y Explorador de Auditoría
# ---------------------------------------------------------
st.subheader("🔍 Explorador de Auditoría y Transacciones")

f1, f2, f3 = st.columns(3)
with f1:
    filter_validity = st.selectbox(
        "Filtro de Auditoría:",
        options=["Todas", "Solo Válidas", "Solo Inválidas (Inconsistencias)"],
    )
with f2:
    all_currencies = sorted(
        list({tx["currency"] for tx in processed_data if tx.get("currency")})
    )
    filter_currency = st.multiselect(
        "Filtrar por Moneda:", options=all_currencies, default=[]
    )
with f3:
    all_statuses = sorted(list({tx["status"] for tx in processed_data if tx.get("status")}))
    filter_status = st.multiselect(
        "Filtrar por Estado:", options=all_statuses, default=[]
    )

# Filtrado dinámico
filtered = processed_data
if filter_validity == "Solo Válidas":
    filtered = [tx for tx in filtered if tx.get("is_valid")]
elif filter_validity == "Solo Inválidas (Inconsistencias)":
    filtered = [tx for tx in filtered if not tx.get("is_valid")]

if filter_currency:
    filtered = [tx for tx in filtered if tx.get("currency") in filter_currency]

if filter_status:
    filtered = [tx for tx in filtered if tx.get("status") in filter_status]

display_rows = []
for tx in filtered:
    display_rows.append(
        {
            "ID": tx.get("id"),
            "Timestamp": tx.get("timestamp"),
            "Monto": tx.get("amount"),
            "Moneda": tx.get("currency"),
            "Tipo": tx.get("type"),
            "Estado": tx.get("status"),
            "Riesgo": tx.get("risk_level", "N/A"),
            "Origen": tx.get("source"),
            "Válida": "✅ Sí" if tx.get("is_valid") else "❌ No",
            "Errores Detectados": (
                " | ".join(tx.get("validation_errors", []))
                if tx.get("validation_errors")
                else "Ninguno"
            ),
        }
    )

df_display = pd.DataFrame(display_rows)
st.dataframe(df_display, use_container_width=True)

# ---------------------------------------------------------
# 8. Exportación de Datos Normalizados y Auditados
# ---------------------------------------------------------
st.subheader("💾 Exportación de Resultados")
export_payload = {
    "agent_metadata": agent_summary,
    "remediation_trail": remediation_trail,
    "transactions": processed_data,
}
json_output = json.dumps(export_payload, indent=2, ensure_ascii=False)

st.download_button(
    label="Descargar JSON Normalizado con Traza del Agente",
    data=json_output,
    file_name="normalized_transactions_agent_audit.json",
    mime="application/json",
)