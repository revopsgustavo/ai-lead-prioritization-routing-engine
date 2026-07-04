# AI Consultant Analysis

## Veredito executivo
A operacao sintetica gerou 2247 leads, com SLA compliance de 64.2% e desperdicio estimado de leads prioritarios em 92.0%. A leitura rule-based sugere que o gargalo principal nao e apenas volume: ha combinacao de qualidade desigual por canal, distribuicao operacional desequilibrada, ownership incompleto e baixa protecao de SLA para leads de maior potencial.

## Leitura da operacao
- Volume: Paid Search sustenta volume relevante, mas os dados sugerem fit medio inferior e pressao sobre a fila.
- Qualidade: Referral e Partner tendem a entregar melhor qualidade relativa, mas com menor escala.
- Velocidade de atendimento: ha indicios de atraso em leads p1, o que cria risco direto de perda de conversao.
- Capacidade: a distribuicao por SDR mostra concentracao, sugerindo necessidade de limite operacional por carteira.
- Regra de roteamento: as regras apoiam segmentacao basica, mas ainda deixam excecoes sem owner.
- Execucao SDR: alguns resultados precisam ser avaliados controlando por mix de canal, score e segmento.
- Governanca de SLA: o SLA existe como criterio, mas precisa virar mecanismo operacional com alerta, aging e escalonamento.

## Principais gaps identificados
- CRITICAL | sla: Ha indicios de 272 leads p1 com primeiro contato acima do SLA definido. Decisao necessaria: Criar fila expressa para p1, alerta de SLA e escalonamento automatico para manager.
- CRITICAL | ownership: A evidencia disponivel aponta 25 leads sem SDR responsavel apos roteamento. Decisao necessaria: Criar owner de fallback com SLA curto e fila de auditoria diaria para casos sem dono.
- HIGH | sla_governance: A evidencia disponivel aponta SLA compliance de 64.2%, abaixo do patamar operacional esperado. Decisao necessaria: Revisar target por prioridade, criar aging de fila e rotina diaria de excecoes.
- HIGH | channel_quality: Canal paid_search gera 816 leads com fit medio 58.4. Decisao necessaria: Refinar segmentacao, negative keywords e criterio de MQL antes do roteamento automatico.
- HIGH | routing_capacity: Os dados sugerem concentracao de 746 leads no SDR sdr_01, acima do padrao do time. Decisao necessaria: Aplicar limite de capacidade por SDR e rebalancear excedente por prioridade e fit.
- HIGH | priority_management: Os dados sugerem desperdicio de 92.0% em leads p1/p2 ou score alto. Decisao necessaria: Ordenar fila por prioridade, aging e potencial ARR; medir ganho por cohort antes/depois.
- HIGH | backlog: No fim do periodo, ha aumento de backlog e queda visivel de SLA compliance versus semanas anteriores. Decisao necessaria: Implantar monitor de backlog diario e gatilho de redistribuicao quando fila exceder capacidade.
- MEDIUM | sdr_execution: Ha indicios de baixo SQL rate em sdr_02 apesar de volume relevante de 523 leads. Decisao necessaria: Fazer review de cadencia e comparar performance por cohort de score antes de redistribuir volume.
- MEDIUM | campaign_quality: Campanha camp_04 combina volume alto e SQL rate de 11.8%. Decisao necessaria: Separar fluxo de nutricao para baixo score e proteger agenda SDR para leads com maior fit.

## Hipoteses provaveis
Os dados sugerem que parte da perda esta na execucao operacional depois do score: leads bons existem, mas nem sempre recebem contato rapido, owner claro e priorizacao real na fila. Tambem ha indicios de que alguns canais geram volume que consome capacidade sem converter na mesma proporcao.

## Evidencias observadas
- Leads totais: 2247.
- Leads sem owner: 25.
- Leads prioritarios atrasados: 272.
- MQL para SQL: 24.5%.
- SQL para oportunidade: 56.1%.

## Evidencias ausentes
- Motivo de desqualificacao por lead.
- Qualidade real das conversas.
- Cadencia SDR executada, nao apenas planejada.
- Motivo de nao contato.
- Disponibilidade real dos SDRs.
- Regras reais de territorio e excecoes comerciais.
- Feedback de vendas e motivo de no-show, quando aplicavel.

## Perguntas para validacao
- SDR Manager: quais SDRs estavam com ausencia, treinamento ou carteira temporariamente alterada?
- Head de Sales: o time quer maximizar velocidade em p1/p2 ou manter round robin estrito?
- Marketing Ops: quais campanhas otimizam volume versus qualidade real de SQL?
- RevOps: quais regras geram fallback sem owner e quem audita isso diariamente?
- Growth/Acquisition: quais canais ainda justificam investimento quando controlamos por fit e SLA?

## Recomendacoes priorizadas
### Fazer agora
- RevOps | esforco medio | implantar fallback obrigatorio, alerta de SLA e fila ordenada por prioridade | acompanhar `sla_compliance_rate` e `leads_without_owner` | 7 dias.
- SDR Manager | esforco baixo | revisar carga dos SDRs com maior backlog e redistribuir p1/p2 atrasados | acompanhar `speed_to_lead_by_priority` | 48 horas.

### Fazer depois
- Marketing Ops | esforco medio | recalibrar criterios de MQL em canais de alto volume e baixo fit | acompanhar `sql_rate_by_campaign` | 30 dias.
- Sales Ops | esforco medio | testar roteamento com capacity cap e regra por potencial ARR | acompanhar `routing_load_by_sdr` | 30 dias.

### Monitorar
- Head de Sales | esforco baixo | avaliar conversao por SDR controlando por score, canal e segmento | acompanhar `conversion_by_sdr` | quinzenal.

## Riscos de decisao
Decidir apenas por volume pode transferir capacidade dos SDRs para leads de menor fit, reduzir velocidade em contas de maior potencial e mascarar falhas de ownership. A evidencia disponivel aponta que o score precisa estar conectado ao roteamento, ao SLA e a cadencia; caso contrario, vira apenas uma classificacao analitica sem impacto operacional.

## Conclusao executiva
A decisao recomendada para lideranca e tratar priorizacao como processo operacional, nao como dashboard. O proximo movimento deve proteger p1/p2, corrigir leads sem owner, limitar sobrecarga por SDR e revisar canais/campanhas que compram volume sem qualidade suficiente. As hipoteses precisam ser validadas com dados de cadencia, motivos de perda e disponibilidade antes de mudancas definitivas de territorio ou investimento.
