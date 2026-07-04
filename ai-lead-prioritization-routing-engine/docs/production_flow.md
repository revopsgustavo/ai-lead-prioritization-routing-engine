# Production Flow

## Fontes reais
CRM, Marketing Automation, Sales Engagement, agenda dos SDRs, enrichment de contas, billing e historico de oportunidades.

## Ingestao
Jobs recorrentes extraem leads, contas, campanhas, atividades, status de SLA, ownership e outcomes. A camada raw preserva o dado original.

## Modelagem
Camadas tratadas padronizam IDs, datas, canais, campanhas, regras de roteamento, scores e eventos de SLA.

## Data quality
Validacoes bloqueiam automacao quando ha IDs nulos, owner ausente, score fora da faixa, status invalido ou datas inconsistentes.

## Regras de roteamento
Regras devem ser versionadas, auditaveis e aprovadas por RevOps/Sales Ops. Mudancas precisam de teste retroativo antes de producao.

## Alertas
Alertas de p1 sem contato, SLA em risco, backlog por SDR, fallback sem owner e queda de conversao por campanha.

## Workflow humano
Managers recebem excecoes acionaveis. SDRs recebem fila ordenada por prioridade, aging, fit e potencial ARR.

## Seguranca
Controle de acesso por papel, mascaramento de dados sensiveis e log de decisoes automatizadas.

## Limitacoes
Mesmo em producao, o motor deve gerar hipoteses. Causa raiz exige validacao com conversas, motivos de perda, qualidade de cadencia e contexto comercial.
