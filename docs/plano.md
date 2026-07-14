# Plano de Estrutura Organizacional - Agente Brem

Este documento apresenta a interpretação e a proposta de organização de contexto, regras, habilidades, comandos e subagentes para o projeto **Brem**, inspirando-se em padrões avançados de design de sistemas multiagentes modulares (como a estrutura de diretórios do Claude Desktop / Cline).

---

## 1. Introdução

À medida que o projeto **Brem** cresce e abrange diferentes focos — desde a automação e precificação para a loja de decantes do **Bruno** até novos ecossistemas como o da **Utopia** —, a organização centralizada de regras torna-se um gargalo cognitivo e operacional. 

Inspirados no padrão modular de agentes de código, propomos uma arquitetura em que o agente principal (Brem) gerencia contextos especializados por meio de:
*   **Regras Modulares (`rules/`)**: Instruções técnicas específicas para cada domínio de negócio ou tecnologia.
*   **Habilidades On-Demand (`skills/`)**: Scripts e ferramentas reutilizáveis carregados apenas sob demanda.
*   **Subagentes Dedicados (`agents/`)**: Agentes com papéis focados, contextos isolados e autonomia delimitada (ex: Bruno e Utopia).
*   **Backlogs Isolados (`docs/backlog_*.md`)**: Filas de tarefas separadas por agente para evitar mistura de escopos.

---

## 2. Mapeamento Atual vs. Desejado

A tabela abaixo ilustra a transição do estado atual do repositório para o modelo ideal proposto:

| Componente | Organização Atual (Brem) | Modelo Modular Proposto (.brem/) | Benefício Principal |
| :--- | :--- | :--- | :--- |
| **Regras Gerais** | `.agents/AGENTS.md` | `.brem/agents.md` | Ponto de partida único e leve. |
| **Regras de Domínio** | Misturadas no arquivo geral | `.brem/rules/pricing.md`<br>`.brem/rules/scraping.md` | Regras específicas são lidas apenas se a tarefa exigir. |
| **Ferramentas / Skills** | Plugins instalados no sistema do usuário | `.brem/skills/nuvemshop/`<br>`.brem/skills/preco/` | Habilidades são versionadas junto ao código do projeto. |
| **Subagentes** | Identificados apenas em texto | `.brem/agents/bruno.md`<br>`.brem/agents/utopia.md` | Configurações de modelo e contexto isolados para cada foco. |
| **Backlogs** | Controlados via chat ou arquivos temporários | `docs/backlog_bruno.md`<br>`docs/backlog_utopia.md` | Rastreabilidade total das demandas com "definição de pronto". |

---

## 3. Estrutura de Diretórios Proposta

Durante nossa fase de testes de estrutura, a organização dos arquivos de planejamento e controle fica restrita à pasta `docs/`. Em um estágio de adoção completa, a estrutura ideal do projeto seguirá este formato:

```
brem/
├── .agents/
│   └── AGENTS.md                  # Regras gerais de comportamento, EFT e Autonomia
├── .agents/                       # Customizações e habilidades do workspace
├── .vscode/                       # Configurações do VS Code
├── apresentacoes/                 # Apresentações de slides e análises do time
├── PROJETOS/                      # Projetos em desenvolvimento ativo
│   ├── Bruno/                     # Scripts de automação do cliente Bruno
│   └── Utopia/                    # Código-fonte e scripts do projeto Utopia
├── docs/                          # Documentações e backlogs
├── SUMMONS/                       # Subagentes e maestros de fluxo (ex: estagiariovisual)
├── GRIMORIO/                      # Habilidades técnicas e scripts de utilidades
└── MEMORIAS/                      # Registros históricos e causas raízes (causas_raizes.md)
```

---

## 4. Detalhamento dos Componentes e Divisão de Responsabilidades

### A. Subagente Bruno
*   **Foco Principal**: Automação da loja de decantes de perfumes do Bruno, conversão de tabelas de produtos para o formato Nuvemshop e sincronização de dados do Fragrantica.
*   **Diretrizes de Negócio**: Aplicação estrita da fórmula de precificação arbitrage 8/2 (Brasil/China), restrição à interface gráfica do navegador (Playwright sem modo visual por padrão) e raspagem resiliente com tratamento de erros.

### B. Subagente Utopia
*   **Foco Principal**: Desenvolvimento e automação do ecossistema Utopia (módulos adicionais, testes estruturais e outras integrações do Marcus).
*   **Diretrizes de Negócio**: Foco em design de software desacoplado e testes unitários.

---

## 5. Gestão de Backlogs e Rastreabilidade

Cada subagente conta com seu próprio arquivo de controle em `docs/` (`backlog_bruno.md` e `backlog_utopia.md`). Para manter a qualidade máxima nas entregas, todas as tarefas devem seguir o padrão:

1.  **Contexto**: O motivo técnico/comercial pelo qual a tarefa existe.
2.  **Descrição**: Passos detalhados e pragmáticos de execução.
3.  **Qualificação de Pronto (Definition of Done)**: Critérios específicos de validação. Caso a tarefa já tenha sido concluída, esse campo conterá a prova de funcionamento (ex: logs de teste, arquivos gerados ou caminhos validados).

---

## 6. Plano de Implementação Incremental

Para testar esta estrutura de forma segura, seguiremos as etapas:
1.  **Fase 1 (Atual)**: Criação dos arquivos de planejamento e backlogs na pasta `docs/` sem interferir nos arquivos de código das pastas `PROJETOS/Bruno/` ou `PROJETOS/Utopia/`.
2.  **Fase 2**: Validação unitária (1 de 1) de qualquer script de migração ou criação das pastas `.brem/` caso Marcus decida avançar para a estruturação de pastas ocultas de agente.
3.  **Fase 3**: Modularização gradual das regras do `AGENTS.md` para arquivos de regras menores sob demanda.
