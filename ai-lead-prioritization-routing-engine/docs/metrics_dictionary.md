# Metrics Dictionary

Todas as taxas sao documentadas em escala 0-1 nos dados e formatadas em percentual no dashboard.

| Metric | Definition | Formula | Interpretation | Decision | Limitation |
|---|---|---|---|---|---|
| total_leads | Volume de leads | count(leads) | Demanda gerada | Dimensionar capacidade | Nao mede qualidade |
| total_mqls | Leads aceitos como MQL | sum(is_mql) | Volume qualificado inicial | Rever criterio MQL | Depende de regra sintetica |
| total_sqls | Leads convertidos em SQL | sum(is_sql) | Conversao comercial | Avaliar qualidade e execucao | Sem motivo de perda |
| average_lead_score | Score medio | avg(lead_score) | Qualidade geral | Ajustar thresholds | Score rule-based |
| average_icp_fit_score | Fit medio | avg(icp_fit_score) | Aderencia ICP | Revisar canais | Sintetico |
| average_intent_score | Intencao media | avg(intent_score) | Sinal de compra | Priorizar atendimento | Sintetico |
| priority_tier_distribution | Mix por prioridade | count por tier / total | Pressao por SLA | Planejar fila | Nao inclui custo |
| average_response_time_hours | Tempo medio de resposta | avg(response_time_hours) | Velocidade | Ajustar SLA | Tempo corrido |
| median_response_time_hours | Mediana de resposta | median(response_time_hours) | Velocidade robusta | Detectar cauda longa | Oculta extremos |
| sla_compliance_rate | SLA atendido | met / total | Governanca de SLA | Escalonar fila | Escala 0-1 |
| sla_breach_rate | SLA violado | breached / total | Risco operacional | Corrigir gargalos | Escala 0-1 |
| mql_to_sql_conversion | MQL para SQL | SQL / MQL | Qualidade e abordagem | Revisar MQL e cadencia | Escala 0-1 |
| sql_to_opportunity_conversion | SQL para oportunidade | opp / SQL | Qualidade de SQL | Ajustar handoff | Escala 0-1 |
| conversion_by_score_band | Conversao por faixa | SQL/Opp por score_band | Valida score | Recalibrar score | Amostras variam |
| routing_load_by_sdr | Carga por SDR | leads por sdr | Balanceamento | Redistribuir capacidade | Nao mede agenda real |
| accepted_leads_by_sdr | MQLs por SDR | MQL por sdr | Aceite operacional | Revisar carteira | Mix pode distorcer |
| disqualified_leads | Desqualificados | count(disqualified) | Desperdicio | Revisar origem | Sem motivo detalhado |
| leads_without_owner | Leads sem SDR | count null sdr_id | Falha de ownership | Criar fallback | Pode ser excecao planejada |
| high_priority_delayed_leads | P1 atrasados | p1 e response > target | Risco de perda | Proteger fila p1 | Tempo corrido |
| conversion_by_channel | Conversao por canal | SQL/Opp por channel | Qualidade de canal | Realocar investimento | Sem CAC |
| conversion_by_sdr | Conversao por SDR | SQL/Opp por sdr | Execucao e mix | Coaching ou roteamento | Controlar por mix |
| backlog_by_sdr | Risco de backlog | breached por sdr | Gargalo | Redistribuir fila | Proxy sintetico |
| lead_quality_by_channel | Score e fit por canal | avg por channel | Qualidade de demanda | Revisar canal | Sem custo |
| speed_to_lead_by_priority | Tempo por prioridade | avg response por tier | SLA por prioridade | Alerta p1/p2 | Tempo corrido |
| sla_compliance_by_sdr | SLA por SDR | met/total por sdr | Execucao/capacidade | Ajustar carga | Escala 0-1 |
| sql_rate_by_campaign | SQL rate por campanha | SQL/leads | Qualidade de campanha | Revisar campanha | Sem CPL |
| opportunity_rate_by_channel | Opportunity rate por canal | opp/leads | Pipeline real | Investimento | Escala 0-1 |
| priority_lead_waste_rate | Desperdicio prioritario | prioritarios sem SQL, SLA violado ou sem owner / prioritarios | Perda de potencial | Proteger alto score | Proxy operacional |
