# Backlog de Trabalho - Subagente Utopia

Este arquivo serve para gerenciar e documentar o progresso das tarefas de arquitetura, estruturação e novos módulos vinculados ao projeto **Utopia**.

---

## Painel de Controle de Tarefas

| ID | Nome da Tarefa | Status | Responsável |
| :--- | :--- | :--- | :--- |
| UTO-001 | Estruturação Inicial da Pasta Utopia | **Concluído** | Subagente Utopia |
| UTO-002 | Testes Iniciais de Estruturação Multiagente | **Em Progresso** | Subagente Utopia |
| UTO-003 | Sandbox de Testes de Ferramentas Utopia | **A Fazer** | Subagente Utopia |

---

## Detalhamento das Tarefas

### [Concluído] UTO-001: Estruturação Inicial da Pasta Utopia
*   **Status**: **Concluído**
*   **Contexto**: Iniciar um ecossistema de código isolado das regras de negócio comerciais do Bruno, de modo que Marcus possa desenvolver ideias e códigos experimentais de forma livre na pasta Utopia.
*   **Descrição**: Criar a pasta base `Utopia` na raiz do repositório para centralizar todos os códigos-fonte e scripts de teste desse ecossistema.
*   **Qualificação de Pronto (Definição de Pronto)**:
    *   Diretório `Utopia/` criado.
    *   Isolamento completo garantido em relação aos scripts da pasta `Bruno/`.
    *   *Qualificação da Entrega*: Pasta criada e confirmada no mapeamento de diretórios da raiz do projeto.

### [Em Progresso] UTO-002: Testes Iniciais de Estruturação Multiagente
*   **Status**: **Em Progresso**
*   **Contexto**: O Marcus propôs organizar o repositório adotando conceitos de modularização (regras, habilidades e backlogs isolados por projeto) para guiar a atuação do agente Brem de forma mais autônoma e limpa.
*   **Descrição**: Elaborar a documentação de plano organizacional (`docs/plano.md`) e os arquivos de backlog isolados por subagente (`docs/backlog_bruno.md` e `docs/backlog_utopia.md`), limitando as criações e alterações estritamente ao diretório `docs/`.
*   **Qualificação de Pronto (Definição de Pronto)**:
    *   Arquivos criados na pasta `docs/`.
    *   Zero modificações em arquivos de código ou regras fora de `docs/`.
    *   Estrutura clara explicando a separação de escopos e a qualificação de tarefas prontas.
    *   *Qualificação da Entrega*: Criação dos três arquivos concluída e aguardando validação final de estrutura pelo Marcus.

### [A Fazer] UTO-003: Sandbox de Testes de Ferramentas Utopia
*   **Status**: **A Fazer**
*   **Contexto**: Criar um ambiente isolado de testes e simulações para novas ferramentas da Utopia que possam vir a ser solicitadas pelo Marcus.
*   **Descrição**: Implementar uma subpasta ou script de sandbox dentro de `Utopia/` contendo infraestrutura mínima de testes (ex: unit tests simplificados).
*   **Qualificação de Pronto (Definição de Pronto)**:
    *   Diretório de sandbox configurado.
    *   Um script de teste inicial (ex: `test_sandbox.py` ou `.js`) executando e retornando código `0` (sucesso).
