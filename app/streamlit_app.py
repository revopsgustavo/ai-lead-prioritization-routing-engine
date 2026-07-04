from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR / "src"))

import metrics
from utils import DOCS_DIR, DATA_DIR, format_integer_br, format_percent_br, has_columns, read_markdown

st.set_page_config(page_title="AI Lead Prioritization Routing Engine", layout="wide")


@st.cache_data
def load_data():
    return metrics.load_case_data()


def read_csv(name):
    path = DATA_DIR / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def executive_note(seeing, matters, decision):
    st.markdown(f"**O que estamos vendo?** {seeing}")
    st.markdown(f"**Por que importa?** {matters}")
    st.markdown(f"**Qual decisão isso suporta?** {decision}")


def safe_chart(df, required, chart_fn):
    if df.empty or not has_columns(df, required):
        st.info("Dados insuficientes para exibir este grafico.")
        return
    st.plotly_chart(chart_fn(df), use_container_width=True)


data = load_data()
page = st.sidebar.radio("Menu", [
    "Visão Executiva", "Lead Scoring", "Routing Engine", "SLA e Tempo de Resposta",
    "Performance por SDR", "Conversão por Score", "Consultor de Gaps", "IA Consultora",
    "Análise Executiva", "Qualidade dos Dados", "Production Flow"
])

st.title("AI Lead Prioritization & Routing Engine")
st.caption("Case sintético de RevOps Analytics para priorização, roteamento, SLA e governança comercial B2B SaaS.")

if page == "Visão Executiva":
    st.header("Visão Executiva")
    executive_note(
        "Um motor rule-based que conecta score, roteamento, SLA e conversão.",
        "RevOps precisa decidir onde proteger capacidade comercial e onde revisar demanda.",
        "Priorizar leads de maior potencial, corrigir gargalos e orientar investimento por qualidade."
    )
    summary = metrics.executive_summary_metrics(data)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads", format_integer_br(summary["total_leads"]))
    c2.metric("SQLs", format_integer_br(summary["total_sqls"]))
    c3.metric("SLA compliance", format_percent_br(summary["sla_compliance_rate"]))
    c4.metric("Desperdício prioritário", format_percent_br(summary["priority_lead_waste_rate"]))
    st.markdown("### Problema de negócio")
    st.write("Times comerciais perdem eficiência quando leads são distribuídos sem considerar fit, intenção, capacidade, SLA, canal, segmento, prioridade comercial e potencial de conversão.")
    st.markdown("### Como RevOps usa o motor")
    st.write("O score define prioridade, o roteamento traduz a prioridade em dono operacional, o SLA protege velocidade e a conversão valida se as regras geram pipeline de qualidade. A IA consultora rule-based transforma gaps em hipóteses e decisões, sem afirmar causa raiz.")
    safe_chart(metrics.conversion_by_channel(data), ["channel", "sql_rate", "opportunity_rate"], lambda df: px.bar(df, x="channel", y=["sql_rate", "opportunity_rate"], barmode="group", title="Conversão por canal"))

elif page == "Lead Scoring":
    st.header("Lead Scoring")
    executive_note("Distribuição de score, fit e intenção.", "Score alto sem SLA vira oportunidade desperdiçada.", "Ajustar critério de MQL e priorização operacional.")
    scores = read_csv("lead_scores")
    safe_chart(scores, ["lead_score", "score_band"], lambda df: px.histogram(df, x="lead_score", color="score_band", nbins=20, title="Distribuição de lead score"))
    st.dataframe(scores.head(200), use_container_width=True)

elif page == "Routing Engine":
    st.header("Routing Engine")
    executive_note("Carga por SDR e regras aplicadas.", "Roteamento desbalanceado cria backlog e afeta SLA.", "Redistribuir capacidade e revisar fallback sem owner.")
    load = metrics.routing_load_by_sdr(data)
    safe_chart(load, ["sdr_id", "assigned_leads"], lambda df: px.bar(df, x="sdr_id", y="assigned_leads", title="Leads roteados por SDR"))
    st.dataframe(read_csv("routing_decisions").head(300), use_container_width=True)

elif page == "SLA e Tempo de Resposta":
    st.header("SLA e Tempo de Resposta")
    executive_note("SLA por prioridade e tempo de resposta.", "Velocidade e prioridade precisam estar conectadas.", "Criar alertas e escalonamento para leads P1/P2.")
    speed = metrics.speed_to_lead_by_priority(data)
    safe_chart(speed, ["priority_tier", "avg_response_hours"], lambda df: px.bar(df, x="priority_tier", y="avg_response_hours", title="Tempo médio de resposta por prioridade"))
    safe_chart(speed, ["priority_tier", "sla_compliance"], lambda df: px.line(df, x="priority_tier", y="sla_compliance", markers=True, title="SLA compliance por prioridade"))

elif page == "Performance por SDR":
    st.header("Performance por SDR")
    executive_note("Volume, SQL rate e oportunidade por SDR.", "Performance bruta pode refletir mix ruim, não apenas execução.", "Avaliar SDR controlando por canal, score e segmento.")
    conv = metrics.conversion_by_sdr(data)
    safe_chart(conv, ["sdr_id", "leads", "sql_rate"], lambda df: px.scatter(df, x="leads", y="sql_rate", color="sdr_id", size="leads", title="Volume vs SQL rate por SDR"))
    st.dataframe(conv, use_container_width=True)

elif page == "Conversão por Score":
    st.header("Conversão por Score")
    executive_note("Conversão agrupada por faixa de score.", "Se score alto não converte, há gap de SLA, roteamento ou critério.", "Recalibrar threshold ou proteger execução de alto potencial.")
    conv = metrics.conversion_by_score_band(data)
    safe_chart(conv, ["score_band", "sql_rate"], lambda df: px.bar(df, x="score_band", y="sql_rate", title="SQL rate por score band"))
    st.dataframe(conv, use_container_width=True)

elif page == "Consultor de Gaps":
    st.header("Consultor de Gaps")
    gaps = read_csv("consultant_gap_log")
    executive_note("Gaps priorizados por severidade.", "A liderança precisa decidir ações, não apenas observar gráficos.", "Atacar SLA, ownership, capacidade e qualidade por canal.")
    if gaps.empty:
        st.warning("Nenhum gap gerado ainda.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Críticos", format_integer_br((gaps["severity"] == "critical").sum()))
        c2.metric("Altos", format_integer_br((gaps["severity"] == "high").sum()))
        c3.metric("Médios", format_integer_br((gaps["severity"] == "medium").sum()))
        c4.metric("Baixos", format_integer_br((gaps["severity"] == "low").sum()))
        sev = st.multiselect("Severidade", sorted(gaps["severity"].unique()), default=list(sorted(gaps["severity"].unique())))
        area = st.multiselect("Area", sorted(gaps["area"].unique()), default=list(sorted(gaps["area"].unique())))
        view = gaps[gaps["severity"].isin(sev) & gaps["area"].isin(area)]
        st.markdown("### O que exige ação agora")
        for row in view[view["severity"].isin(["critical", "high"])].head(5).itertuples(index=False):
            st.warning(f"{row.area}: {row.recommended_action} | Owner: {row.owner} | Métrica: {row.follow_up_metric}")
        st.dataframe(view[["severity", "area", "evidence", "recommended_action", "owner", "urgency", "follow_up_metric"]], use_container_width=True)

elif page == "IA Consultora":
    st.header("IA Consultora")
    executive_note(
        "A análise rule-based consolida gaps, riscos e recomendações em linguagem executiva.",
        "Ela transforma evidências operacionais em hipóteses de decisão sem afirmar causa raiz.",
        "Priorizar ações imediatas de SLA, ownership, capacidade e qualidade de demanda."
    )
    st.markdown(read_markdown(DOCS_DIR / "ai_consultant_analysis.md"))

elif page == "Análise Executiva":
    st.header("Análise Executiva")
    executive_note(
        "Uma leitura consolidada do período com métricas, achados, riscos e recomendações.",
        "A liderança precisa saber se o problema está em volume, qualidade, SLA ou roteamento.",
        "Definir quais regras, canais e rotinas comerciais devem ser ajustados primeiro."
    )
    st.markdown(read_markdown(DOCS_DIR / "executive_analysis.md"))

elif page == "Qualidade dos Dados":
    st.header("Qualidade dos Dados")
    executive_note("Validações de arquivos, colunas, IDs, datas, scores e SLA.", "Sem qualidade mínima, a decisão operacional fica frágil.", "Corrigir falhas de dados antes de automatizar roteamento.")
    dq = read_csv("data_quality_report")
    if dq.empty:
        st.warning("Relatorio de qualidade ainda nao gerado.")
    else:
        st.dataframe(dq, use_container_width=True)

elif page == "Production Flow":
    st.header("Production Flow")
    executive_note(
        "Como o case evoluiria para uma operação real com CRM, Marketing Automation e Sales Engagement.",
        "Produção exige governança, segurança, data quality e workflow humano antes de automação.",
        "Planejar a evolução do protótipo sem prometer produção real nesta versão."
    )
    st.markdown(read_markdown(DOCS_DIR / "production_flow.md"))
