from __future__ import annotations

from pathlib import Path

import pandas as pd

import metrics

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"
DATA_DIR = ROOT_DIR / "data" / "processed"


def write_reports():
    data = metrics.load_case_data()
    summary = metrics.executive_summary_metrics(data)
    channels = metrics.lead_quality_by_channel(data).sort_values("avg_fit")
    sdrs = metrics.conversion_by_sdr(data).sort_values("sql_rate")
    gaps_path = DATA_DIR / "consultant_gap_log.csv"
    gaps = pd.read_csv(gaps_path) if gaps_path.exists() else pd.DataFrame()
    executive = f"""# Analise Executiva

## Veredito executivo
A operacao apresenta demanda suficiente, mas os dados sugerem perda de eficiencia por combinacao de SLA, roteamento e qualidade de canais. O problema nao parece ser apenas volume; a prioridade deve ser proteger leads p1/p2, corrigir ownership e recalibrar canais de alto volume com fit inferior.

## Resumo de metricas
- Leads totais: {summary['total_leads']}
- MQLs: {summary['total_mqls']}
- SQLs: {summary['total_sqls']}
- Score medio: {summary['average_lead_score']:.1f}
- SLA compliance: {summary['sla_compliance_rate']:.1%}
- MQL para SQL: {summary['mql_to_sql_conversion']:.1%}
- SQL para oportunidade: {summary['sql_to_opportunity_conversion']:.1%}
- Leads sem owner: {summary['leads_without_owner']}
- Leads prioritarios atrasados: {summary['high_priority_delayed_leads']}

## Diagnostico do periodo
O periodo de 90 dias mostra piora no fim da serie, indicando que a capacidade operacional ficou mais pressionada. Paid Search sustenta volume, mas exige filtro de qualidade. Referral e Partner mostram melhor leitura de qualidade relativa e deveriam orientar aprendizados de ICP e mensagem.

## Principais achados
- O problema parece estar mais em SLA, roteamento e qualidade do que em falta de volume.
- Canais com alto volume e fit inferior devem ser revisados antes de receber mais investimento.
- SDRs com alto volume e baixa conversao precisam ser avaliados por mix, nao apenas por resultado bruto.
- Regras de roteamento devem incluir limite de capacidade e fallback obrigatorio.
- Lideranca deve decidir agora como proteger p1/p2: fila expressa, alerta de SLA e redistribuicao por backlog.

## Riscos
Decidir por volume bruto pode aumentar pipeline aparente e reduzir produtividade real. A ausencia de motivos de perda e cadencia impede afirmar causa raiz.

## Recomendacoes priorizadas
1. Corrigir leads sem owner e criar owner de contingencia.
2. Criar fila expressa para p1/p2 com SLA e escalonamento.
3. Rebalancear SDRs sobrecarregados por capacidade diaria.
4. Revisar Paid Search e campanhas com SQL rate baixo.
5. Medir conversao por score, canal, segmento e SDR antes de mudar territorios.

## Limitacoes
Dados sao sinteticos, rule-based e sem validacao qualitativa de conversas ou motivos de perda.

## Conclusao executiva
O motor deve ser usado como sistema de governanca comercial: priorizar, rotear, proteger SLA e orientar decisoes de investimento e capacidade.
"""
    (DOCS_DIR / "executive_analysis.md").write_text(executive, encoding="utf-8")
    handoff = f"""# Final Handoff Report

## Status
Projeto criado e pipeline executado localmente.

## Arquivos gerados
Scripts em `src/`, dashboard em `app/`, docs em `docs/`, slides em `slides/` e dados em `data/processed/`.

## Dados gerados
Foram gerados {summary['total_leads']} leads sinteticos em 90 dias, alem de contas, canais, campanhas, SDRs, regras, atividades, SLA, scores, decisoes de roteamento e outcomes.

## Validacoes
Rodar `python -m compileall src app`, `python -m pytest` e `streamlit run app/streamlit_app.py`.

## Pendencias
Integrar dados reais de CRM, Marketing Automation e Sales Engagement em uma evolucao de producao.

## Como rodar
1. `python src/generate_data.py`
2. `python src/consultant_gap_finder.py`
3. `python src/ai_consultant.py`
4. `python src/data_quality.py`
5. `streamlit run app/streamlit_app.py`
"""
    (DOCS_DIR / "final_handoff_report.md").write_text(handoff, encoding="utf-8")
    return {"channels": channels, "sdrs": sdrs, "gaps": gaps}


if __name__ == "__main__":
    write_reports()
