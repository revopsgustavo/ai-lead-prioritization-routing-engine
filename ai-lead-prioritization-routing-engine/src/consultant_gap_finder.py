from __future__ import annotations

from pathlib import Path

import pandas as pd

import metrics

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"


def gap(gap_id, area, metric, actual, expected, severity, evidence, probable_cause, missing, question, action, owner, urgency, impact, follow):
    return {
        "gap_id": gap_id,
        "area": area,
        "metric": metric,
        "actual_value": actual,
        "expected_value": expected,
        "severity": severity,
        "evidence": evidence,
        "probable_cause": probable_cause,
        "missing_evidence": missing,
        "validation_questions": question,
        "recommended_action": action,
        "owner": owner,
        "urgency": urgency,
        "expected_impact": impact,
        "follow_up_metric": follow,
        "status": "open",
    }


def generate_gaps(data=None) -> pd.DataFrame:
    data = data or metrics.load_case_data()
    df = metrics.base_frame(data)
    gaps = []
    load = metrics.routing_load_by_sdr(data)
    if not load.empty and load["assigned_leads"].max() > load["assigned_leads"].median() * 1.35:
        row = load.iloc[0]
        gaps.append(gap("gap_001", "routing_capacity", "routing_load_by_sdr", int(row.assigned_leads), "max <= 1.35x median", "high",
            f"Os dados sugerem concentracao de {int(row.assigned_leads)} leads no SDR {row.sdr_id}, acima do padrao do time.",
            "Hipotese provavel: regra de roteamento ou capacidade operacional nao esta limitando entrada por carteira.",
            "Calendario real, indisponibilidades, criterios de territorio e fila manual.",
            "A capacidade diaria desse SDR estava correta e refletia agenda real no periodo?",
            "Aplicar limite de capacidade por SDR e rebalancear excedente por prioridade e fit.",
            "Sales Ops", "imediata", "Reduzir backlog e preservar velocidade de contato em leads prioritarios.", "routing_load_by_sdr"))
    hp_delay = metrics.high_priority_delayed_leads(data)
    if hp_delay:
        gaps.append(gap("gap_002", "sla", "high_priority_delayed_leads", hp_delay, "0", "critical",
            f"Ha indicios de {hp_delay} leads p1 com primeiro contato acima do SLA definido.",
            "Hipotese provavel: lead quente recebe tratamento operacional similar a leads de menor prioridade.",
            "Motivo de nao contato, tentativas por cadencia e disponibilidade real dos SDRs.",
            "Quais etapas impediram contato em ate 4 horas para leads p1?",
            "Criar fila expressa para p1, alerta de SLA e escalonamento automatico para manager.",
            "SDR Manager", "imediata", "Aumentar conversao de leads de alta intencao e reduzir desperdicio de demanda.", "speed_to_lead_by_priority"))
    sla_rate = metrics.sla_compliance_rate(data)
    if sla_rate < 0.78:
        gaps.append(gap("gap_003", "sla_governance", "sla_compliance_rate", round(sla_rate, 3), ">= 0.78", "high",
            f"A evidencia disponivel aponta SLA compliance de {sla_rate:.1%}, abaixo do patamar operacional esperado.",
            "Hipotese provavel: governanca de SLA nao esta conectada a capacidade, prioridade e alertas de execucao.",
            "Historico de alertas, cadencias, horarios comerciais e aceitacao dos leads.",
            "O SLA e medido em horario comercial ou tempo corrido, e quem recebe alertas?",
            "Revisar target por prioridade, criar aging de fila e rotina diaria de excecoes.",
            "RevOps", "curto prazo", "Melhorar previsibilidade de atendimento e reduzir perda por atraso.", "sla_compliance_rate"))
    quality = metrics.lead_quality_by_channel(data)
    high_volume_low_fit = quality[(quality["leads"] > quality["leads"].median()) & (quality["avg_fit"] < 65)]
    if not high_volume_low_fit.empty:
        row = high_volume_low_fit.sort_values(["leads", "avg_fit"], ascending=[False, True]).iloc[0]
        gaps.append(gap("gap_004", "channel_quality", "lead_quality_by_channel", f"{row.channel}: fit {row.avg_fit:.1f}", "avg_fit >= 65", "high",
            f"Canal {row.channel} gera {int(row.leads)} leads com fit medio {row.avg_fit:.1f}.",
            "Hipotese provavel: aquisicao esta otimizando volume sem filtro suficiente de ICP.",
            "Custo por canal, termos de busca, criterios de MQL e feedback qualitativo de vendas.",
            "Quais fontes dentro do canal concentram baixo fit e alta desqualificacao?",
            "Refinar segmentacao, negative keywords e criterio de MQL antes do roteamento automatico.",
            "Marketing Ops", "curto prazo", "Elevar produtividade SDR e reduzir tempo gasto em baixa aderencia.", "avg_fit_by_channel"))
    conv = metrics.conversion_by_sdr(data)
    candidates = conv[(conv["leads"] > conv["leads"].median()) & (conv["sql_rate"] < 0.14)]
    if not candidates.empty:
        row = candidates.sort_values("sql_rate").iloc[0]
        gaps.append(gap("gap_005", "sdr_execution", "conversion_by_sdr", f"{row.sdr_id}: {row.sql_rate:.1%}", ">= 14%", "medium",
            f"Ha indicios de baixo SQL rate em {row.sdr_id} apesar de volume relevante de {int(row.leads)} leads.",
            "Hipotese provavel: mix de leads, cadencia ou qualidade de abordagem pode estar reduzindo conversao.",
            "Gravacoes, motivos de perda, cadencia executada e distribuicao por segmento.",
            "O baixo resultado persiste quando controlamos por canal, score e segmento?",
            "Fazer review de cadencia e comparar performance por cohort de score antes de redistribuir volume.",
            "SDR Manager", "curto prazo", "Aumentar eficiencia de conversao sem punir SDR por mix ruim.", "conversion_by_sdr"))
    no_owner = metrics.leads_without_owner(data)
    if no_owner:
        gaps.append(gap("gap_006", "ownership", "leads_without_owner", no_owner, "0", "critical",
            f"A evidencia disponivel aponta {no_owner} leads sem SDR responsavel apos roteamento.",
            "Hipotese provavel: fallback manual ou regra incompleta esta deixando leads ICP sem owner.",
            "Logs de erro, motivo de fallback e regras reais de territorio.",
            "Quais condicoes nao encontram regra e por que nao ha owner de contingencia?",
            "Criar owner de fallback com SLA curto e fila de auditoria diaria para casos sem dono.",
            "RevOps", "imediata", "Evitar perda direta de oportunidades por falha de ownership.", "leads_without_owner"))
    campaign = metrics.sql_rate_by_campaign(data)
    bad_campaign = campaign[(campaign["leads"] > campaign["leads"].median()) & (campaign["sql_rate"] < 0.13)]
    if not bad_campaign.empty:
        row = bad_campaign.sort_values(["leads", "sql_rate"], ascending=[False, True]).iloc[0]
        gaps.append(gap("gap_007", "campaign_quality", "sql_rate_by_campaign", f"{row.campaign_id}: {row.sql_rate:.1%}", ">= 13%", "medium",
            f"Campanha {row.campaign_id} combina volume alto e SQL rate de {row.sql_rate:.1%}.",
            "Hipotese provavel: mensagem ou segmentacao atrai demanda que ainda nao esta pronta para vendas.",
            "CPL, criativos, landing pages, objecoes de venda e razoes de desqualificacao.",
            "A campanha deveria gerar MQL para vendas ou nutricao ate sinal mais forte?",
            "Separar fluxo de nutricao para baixo score e proteger agenda SDR para leads com maior fit.",
            "Growth", "curto prazo", "Reduzir desperdicio comercial e melhorar qualidade do pipeline.", "sql_rate_by_campaign"))
    waste = metrics.priority_lead_waste_rate(data)
    if waste > 0.45:
        gaps.append(gap("gap_008", "priority_management", "priority_lead_waste_rate", round(waste, 3), "<= 0.45", "high",
            f"Os dados sugerem desperdicio de {waste:.1%} em leads p1/p2 ou score alto.",
            "Hipotese provavel: priorizacao existe no score, mas nao esta suficientemente refletida em operacao e SLA.",
            "Motivos de perda, numero de tentativas, ordem real de trabalho do SDR e qualidade das conversas.",
            "A fila dos SDRs ordena por prioridade ou apenas por ordem de chegada?",
            "Ordenar fila por prioridade, aging e potencial ARR; medir ganho por cohort antes/depois.",
            "Head de Sales", "imediata", "Capturar mais SQLs em leads de maior probabilidade e potencial.", "priority_lead_waste_rate"))
    df["created_date"] = pd.to_datetime(df["created_date"])
    recent = df[df["created_date"] >= df["created_date"].max() - pd.Timedelta(days=17)]
    prior = df[df["created_date"] < df["created_date"].max() - pd.Timedelta(days=17)]
    if not recent.empty and not prior.empty and (recent["sla_status"] == "met").mean() < (prior["sla_status"] == "met").mean() - 0.08:
        gaps.append(gap("gap_009", "backlog", "recent_sla_drop", round((recent["sla_status"] == "met").mean(), 3), "no drop > 8 pts", "high",
            "No fim do periodo, ha aumento de backlog e queda visivel de SLA compliance versus semanas anteriores.",
            "Hipotese provavel: volume recente superou capacidade ou regras nao amorteceram a fila.",
            "Headcount diario, ausencias, horario de criacao e volume por dia util.",
            "A queda coincide com campanha, feriado, indisponibilidade ou mudanca de regra?",
            "Implantar monitor de backlog diario e gatilho de redistribuicao quando fila exceder capacidade.",
            "RevOps", "imediata", "Evitar deterioracao progressiva de SLA e conversao.", "backlog_by_sdr"))
    return pd.DataFrame(gaps).drop_duplicates(subset=["area", "metric"]).reset_index(drop=True)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    gaps = generate_gaps()
    gaps.to_csv(DATA_DIR / "consultant_gap_log.csv", index=False)
    print(f"Generated {len(gaps)} gaps")


if __name__ == "__main__":
    main()
