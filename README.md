# AI Lead Prioritization & Routing Engine

Case de portfolio em RevOps Analytics para priorizacao e roteamento de leads em uma operacao SaaS B2B sintetica.

## Problema de negocio
Operacoes comerciais perdem eficiencia quando leads sao distribuidos apenas por round robin ou disponibilidade aparente. Sem fit, intencao, capacidade, SLA, canal, segmento e potencial de conversao, o time pode perder leads quentes, sobrecarregar SDRs e inflar volume sem gerar pipeline qualificado.

## Objetivo
Demonstrar como RevOps pode estruturar um motor analitico rule-based para priorizar leads, rotear para SDRs, proteger SLA, balancear carga operacional, identificar falhas de processo e apoiar lideranca com recomendacoes acionaveis.

## Visao geral
O projeto gera dados sinteticos de 90 dias, calcula metricas comerciais, detecta gaps consultivos, cria uma analise rule-based e entrega um dashboard Streamlit em portugues do Brasil.

## Por que importa para RevOps
O motor conecta estrategia e execucao: score define prioridade, roteamento define ownership, SLA protege velocidade e conversao valida qualidade. A leitura executiva evita decisoes baseadas apenas em volume.

## Modulos
- `src/generate_data.py`: gera CSVs e SQLite.
- `src/metrics.py`: calcula metricas executivas e operacionais.
- `src/consultant_gap_finder.py`: identifica gaps com evidencia, hipotese e acao.
- `src/ai_consultant.py`: escreve analise consultiva rule-based.
- `src/data_quality.py`: valida arquivos, colunas, IDs, datas, scores e SLA.
- `app/streamlit_app.py`: dashboard executivo.

## Dados sinteticos
Nenhum dado real e usado. Os cenarios incluem Paid Search com alto volume e fit inferior, Referral com melhor conversao, Partner com maior ticket, SDR sobrecarregado, SLA violado, leads sem owner e backlog no fim do periodo.

## Stack
Python, pandas, numpy, sqlite3, Streamlit, Plotly e pytest.

## Como rodar localmente
```bash
pip install -r requirements.txt
python src/generate_data.py
python src/consultant_gap_finder.py
python src/ai_consultant.py
python src/data_quality.py
python src/reports.py
streamlit run app/streamlit_app.py
```

Se o comando `streamlit` nao estiver no PATH do Windows, use:

```bash
python -m streamlit run app/streamlit_app.py
```

## Metricas principais
SLA compliance, tempo de resposta, MQL para SQL, SQL para oportunidade, conversao por canal, carga por SDR, backlog, leads sem owner, qualidade por canal e desperdicio de leads prioritarios.

## Consultor de gaps
O consultor aponta falhas com evidencia observada, hipotese provavel, evidencia ausente, perguntas de validacao, owner, urgencia, acao recomendada e metrica de acompanhamento.

## IA consultora rule-based
A IA nao usa modelo externo. Ela le o log de gaps e escreve uma analise executiva consultiva, deixando claro que as conclusoes sao hipoteses baseadas nos dados disponiveis.

## Limitacoes
Dados sinteticos, sem custo de aquisicao, sem cadencia real, sem motivos detalhados de perda e sem feedback qualitativo de vendas.

## Production flow
A evolucao natural integra CRM, Marketing Automation e Sales Engagement, com ingestao recorrente, data quality, regras auditaveis, alertas e workflow humano.

## Proximos passos
Adicionar custos por canal, motivos de perda, cadencia SDR e simulacao de capacidade para testar cenarios de roteamento antes da automacao.

## Dashboard Preview
O dashboard Streamlit fica em `app/streamlit_app.py`. Screenshots devem ser adicionados em `docs/screenshots/` antes da divulgação pública.

## Data Disclaimer
Todos os dados são sintéticos. O projeto não usa APIs externas nem dados reais. As análises são rule-based e devem ser tratadas como hipóteses para validação, não como causa raiz confirmada.

## Consulting Use Case
Este case pode ser usado como base para diagnóstico RevOps em SaaS B2B, apoiando liderança com evidências, hipóteses, perguntas de validação, responsáveis e métricas de acompanhamento.

## Contact
LinkedIn: https://www.linkedin.com/in/gustavo-worliczek-lazzarotto/  
E-mail: gustavo.lazzaro77o@gmail.com

