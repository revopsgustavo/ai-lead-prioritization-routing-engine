from __future__ import annotations

from pathlib import Path

import pandas as pd

import metrics

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "processed"
DOCS_DIR = ROOT_DIR / "docs"


def severity_order(value: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(value, 9)


def build_analysis() -> str:
    gaps_path = DATA_DIR / "consultant_gap_log.csv"
    gaps = pd.read_csv(gaps_path) if gaps_path.exists() else pd.DataFrame()
    data = metrics.load_case_data()
    summary = metrics.executive_summary_metrics(data)
    lines = [
        "# AI Consultant Analysis",
        "",
        "## Veredito executivo",
        f"A operacao sintetica gerou {summary['total_leads']} leads, com SLA compliance de {summary['sla_compliance_rate']:.1%} e desperdicio estimado de leads prioritarios em {summary['priority_lead_waste_rate']:.1%}. A leitura rule-based sugere que o gargalo principal nao e apenas volume: ha combinacao de qualidade desigual por canal, distribuicao operacional desequilibrada, ownership incompleto e baixa protecao de SLA para leads de maior potencial.",
        "",
        "## Leitura da operacao",
        "- Volume: Paid Search sustenta volume relevante, mas os dados sugerem fit medio inferior e pressao sobre a fila.",
        "- Qualidade: Referral e Partner tendem a entregar melhor qualidade relativa, mas com menor escala.",
        "- Velocidade de atendimento: ha indicios de atraso em leads p1, o que cria risco direto de perda de conversao.",
        "- Capacidade: a distribuicao por SDR mostra concentracao, sugerindo necessidade de limite operacional por carteira.",
        "- Regra de roteamento: as regras apoiam segmentacao basica, mas ainda deixam excecoes sem owner.",
        "- Execucao SDR: alguns resultados precisam ser avaliados controlando por mix de canal, score e segmento.",
        "- Governanca de SLA: o SLA existe como criterio, mas precisa virar mecanismo operacional com alerta, aging e escalonamento.",
        "",
        "## Principais gaps identificados",
    ]
    if gaps.empty:
        lines.append("Nenhum gap foi gerado. Isso deve ser validado porque a ausencia de alerta pode indicar dados incompletos.")
    else:
        gaps = gaps.assign(_order=gaps["severity"].map(severity_order)).sort_values(["_order", "urgency"])
        for row in gaps.itertuples(index=False):
            lines.append(f"- {row.severity.upper()} | {row.area}: {row.evidence} Decisao necessaria: {row.recommended_action}")
    lines += [
        "",
        "## Hipoteses provaveis",
        "Os dados sugerem que parte da perda esta na execucao operacional depois do score: leads bons existem, mas nem sempre recebem contato rapido, owner claro e priorizacao real na fila. Tambem ha indicios de que alguns canais geram volume que consome capacidade sem converter na mesma proporcao.",
        "",
        "## Evidencias observadas",
        f"- Leads totais: {summary['total_leads']}.",
        f"- Leads sem owner: {summary['leads_without_owner']}.",
        f"- Leads prioritarios atrasados: {summary['high_priority_delayed_leads']}.",
        f"- MQL para SQL: {summary['mql_to_sql_conversion']:.1%}.",
        f"- SQL para oportunidade: {summary['sql_to_opportunity_conversion']:.1%}.",
        "",
        "## Evidencias ausentes",
        "- Motivo de desqualificacao por lead.",
        "- Qualidade real das conversas.",
        "- Cadencia SDR executada, nao apenas planejada.",
        "- Motivo de nao contato.",
        "- Disponibilidade real dos SDRs.",
        "- Regras reais de territorio e excecoes comerciais.",
        "- Feedback de vendas e motivo de no-show, quando aplicavel.",
        "",
        "## Perguntas para validacao",
        "- SDR Manager: quais SDRs estavam com ausencia, treinamento ou carteira temporariamente alterada?",
        "- Head de Sales: o time quer maximizar velocidade em p1/p2 ou manter round robin estrito?",
        "- Marketing Ops: quais campanhas otimizam volume versus qualidade real de SQL?",
        "- RevOps: quais regras geram fallback sem owner e quem audita isso diariamente?",
        "- Growth/Acquisition: quais canais ainda justificam investimento quando controlamos por fit e SLA?",
        "",
        "## Recomendacoes priorizadas",
        "### Fazer agora",
        "- RevOps | esforco medio | implantar fallback obrigatorio, alerta de SLA e fila ordenada por prioridade | acompanhar `sla_compliance_rate` e `leads_without_owner` | 7 dias.",
        "- SDR Manager | esforco baixo | revisar carga dos SDRs com maior backlog e redistribuir p1/p2 atrasados | acompanhar `speed_to_lead_by_priority` | 48 horas.",
        "",
        "### Fazer depois",
        "- Marketing Ops | esforco medio | recalibrar criterios de MQL em canais de alto volume e baixo fit | acompanhar `sql_rate_by_campaign` | 30 dias.",
        "- Sales Ops | esforco medio | testar roteamento com capacity cap e regra por potencial ARR | acompanhar `routing_load_by_sdr` | 30 dias.",
        "",
        "### Monitorar",
        "- Head de Sales | esforco baixo | avaliar conversao por SDR controlando por score, canal e segmento | acompanhar `conversion_by_sdr` | quinzenal.",
        "",
        "## Riscos de decisao",
        "Decidir apenas por volume pode transferir capacidade dos SDRs para leads de menor fit, reduzir velocidade em contas de maior potencial e mascarar falhas de ownership. A evidencia disponivel aponta que o score precisa estar conectado ao roteamento, ao SLA e a cadencia; caso contrario, vira apenas uma classificacao analitica sem impacto operacional.",
        "",
        "## Conclusao executiva",
        "A decisao recomendada para lideranca e tratar priorizacao como processo operacional, nao como dashboard. O proximo movimento deve proteger p1/p2, corrigir leads sem owner, limitar sobrecarga por SDR e revisar canais/campanhas que compram volume sem qualidade suficiente. As hipoteses precisam ser validadas com dados de cadencia, motivos de perda e disponibilidade antes de mudancas definitivas de territorio ou investimento.",
    ]
    return "\n".join(lines) + "\n"


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    output = build_analysis()
    (DOCS_DIR / "ai_consultant_analysis.md").write_text(output, encoding="utf-8")
    print("Generated docs/ai_consultant_analysis.md")


if __name__ == "__main__":
    main()
