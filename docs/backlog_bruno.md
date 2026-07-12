# Backlog de Trabalho - Subagente Bruno

Este arquivo serve para gerenciar e documentar o progresso das tarefas de automação, scraping e integração ligadas à loja de decantes do **Bruno**.

---

## Painel de Controle de Tarefas

| ID | Nome da Tarefa | Status | Responsável |
| :--- | :--- | :--- | :--- |
| BRU-001 | Conversor de Catálogo para Nuvemshop (`nuvemshop-uploader`) | **Concluído** | Subagente Bruno |
| BRU-002 | Captura de Dados do Fragrantica (`trazfragrantica`) | **Concluído** | Subagente Bruno |
| BRU-003 | Calculadora de Precificação Arbitragem 8/2 (`preco`) | **Concluído** | Subagente Bruno |
| BRU-004 | Atualização de Lote com Validação Unitária | **A Fazer** | Subagente Bruno |

---

## Detalhamento das Tarefas

### [Concluído] BRU-001: Conversor de Catálogo para Nuvemshop (`nuvemshop-uploader`)
*   **Status**: **Concluído**
*   **Contexto**: O Marcus precisa cadastrar centenas de perfumes e decantes no painel da Nuvemshop do Bruno. Fazer isso manualmente é lento e propenso a erros de digitação.
*   **Descrição**: Implementar um conversor automatizado que pega uma lista bruta de perfumes fornecida pelo Marcus (nomes, marcas, volumes) e gera o arquivo `produtos.csv` com as colunas corretas exigidas pela importação da Nuvemshop.
*   **Qualificação de Pronto (Definição de Pronto)**: 
    *   Leitura correta do arquivo de entrada.
    *   Geração do `produtos.csv` estruturado sem quebra de caracteres.
    *   *Qualificação da Entrega*: O script foi empacotado como a habilidade de plugin `nuvemshop-uploader` e gera a planilha com cabeçalhos padrão da Nuvemshop.

### [Concluído] BRU-002: Captura de Dados do Fragrantica (`trazfragrantica`)
*   **Status**: **Concluído**
*   **Contexto**: Para tornar a loja atraente, precisamos exibir as notas olfativas, acordes e fotos dos perfumes no catálogo. O Fragrantica Brasil é a melhor fonte pública para esses dados.
*   **Descrição**: Desenvolver uma ferramenta de scraping resiliente que busca as informações do perfume diretamente no Fragrantica, atualiza o arquivo local `perfumes_data.json` e usa o Playwright para renderizar a imagem do card de perfil.
*   **Qualificação de Pronto (Definição de Pronto)**:
    *   Bypass de proteções anti-scraping básicas (Cloudflare) via requisições HTTP seguras.
    *   Criação/Atualização do JSON local com estrutura consistente.
    *   Renderização da imagem do card em modo *headless* (sem interface gráfica visível, conforme a Regra 3 do projeto).
    *   *Qualificação da Entrega*: Habilidade `trazfragrantica` integrada e testada localmente, atualizando o `perfumes_data.json` com sucesso.

### [Concluído] BRU-003: Calculadora de Precificação Arbitragem 8/2 (`preco`)
*   **Status**: **Concluído**
*   **Contexto**: O Bruno compra frascos e insumos importados e vende frações (decantes). Ele precisa de uma precificação padronizada que garanta margem de lucro aplicando a relação de arbitragem 8/2 (comparações e taxa de conversão Brasil/China).
*   **Descrição**: Criar uma calculadora matemática parametrizada que recebe o custo de importação do perfume, custos de embalagem (frasco de decant, etiquetas) e calcula a margem ideal, sugerindo o valor final por ml.
*   **Qualificação de Pronto (Definição de Pronto)**:
    *   Fórmula matemática implementada de acordo com as especificações do Bruno.
    *   Exibição do detalhamento de custos, taxa de câmbio e margem líquida.
    *   *Qualificação da Entrega*: A calculadora foi disponibilizada na habilidade de plugin `preco` e responde de forma rápida e precisa aos inputs do Marcus.

### [A Fazer] BRU-004: Atualização de Lote com Validação Unitária
*   **Status**: **A Fazer**
*   **Contexto**: Ao atualizar preços ou estoque de muitos perfumes de uma vez no banco de dados, falhas no script podem corromper centenas de registros de uma só vez, gerando grande prejuízo e retrabalho.
*   **Descrição**: Criar um script de atualização em lote que executa a transação completa primeiro com exatamente **1 registro (1 de 1)** de teste. Se a validação unitária desse registro falhar, o script deve abortar e reverter imediatamente as alterações, notificando o erro. Só prosseguir para os demais se o primeiro passar 100%.
*   **Qualificação de Pronto (Definição de Pronto)**:
    *   O script deve aceitar um lote de entrada, mas pausar/testar no primeiro elemento.
    *   Mecanismo de log detalhado mostrando o sucesso do teste inicial.
    *   Bloqueio contra execução cega de lotes inteiros.
