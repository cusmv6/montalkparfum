# Manual do Modelo de Importação Nuvemshop - Montalk Decantes

Este manual detalha a estrutura de colunas e características do template de importação em massa da Nuvemshop (`produtos.csv`). Use-o como referência para cadastrar novos decantes ou atualizar produtos existentes por planilha.

---

## 📌 1. Regras de Estruturação e Variações

A Nuvemshop utiliza uma estrutura de **linha pai** e **linhas filhas** para representar variações de um mesmo produto (ex: decantes de diferentes tamanhos para o mesmo perfume):

1. **Agrupamento por `Identificador URL`:** Todas as linhas que pertencem ao mesmo produto devem compartilhar exatamente o mesmo `Identificador URL` (ex: `amouage-interlude-man`).
2. **Preenchimento Único por Produto:** Campos gerais do produto (Nome, Descrição, Categorias, Marca, Exibir na loja, SEO, etc.) devem ser preenchidos **apenas na primeira linha** do produto. Nas linhas seguintes das variações, esses campos **devem ficar em branco**.
3. **Preenchimento por Variação:** Campos específicos da variação (Preço, Peso, Estoque, SKU, Código de barras, Custo, Dimensões) devem ser preenchidos **em todas as linhas**.

---

## 📊 2. Dicionário de Colunas (30 Características)

Abaixo está o detalhamento de cada uma das 30 colunas do template:

| # | Coluna | Tipo / Formato | Descrição | Regras de Preenchimento |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `Identificador URL` | Texto (Slug) | O identificador único e amigável da URL do produto. | Obrigatório. Usar letras minúsculas, números e hifens (sem espaços ou acentos). Ex: `creed-aventus`. |
| **2** | `Nome` | Texto | Nome do produto visível na loja. | Preencher apenas na 1ª linha. Ex: `Decante Creed Aventus`. |
| **3** | `Categorias` | Texto | Categorias do produto, separadas por `>` para subníveis. | Preencher apenas na 1ª linha. Ex: `Decantes > Creed`. |
| **4** | `Nome da variação 1` | Texto | O nome da primeira propriedade de variação. | Preencher em todas as linhas se houver variação. Para decantes, use: `Volumetria`. |
| **5** | `Valor da variação 1` | Texto | O valor correspondente à propriedade da variação 1. | Ex: `2ml`, `5ml` ou `10ml`. |
| **6** | `Nome da variação 2` | Texto | O nome da segunda propriedade de variação. | Deixar em branco se não houver segunda variação. |
| **7** | `Valor da variação 2` | Texto | O valor correspondente à propriedade da variação 2. | Deixar em branco se não houver segunda variação. |
| **8** | `Nome da variação 3` | Texto | O nome da terceira propriedade de variação. | Deixar em branco se não houver terceira variação. |
| **9** | `Valor da variação 3` | Texto | O valor correspondente à propriedade da variação 3. | Deixar em branco se não houver terceira variação. |
| **10** | `Preço` | Numérico | Preço de venda da variação. | Obrigatório para todas as variações. Decimal com ponto `.`. Ex: `201.71`. |
| **11** | `Preço promocional` | Numérico | Preço com desconto. | Opcional. Se preenchido, deve ser menor que `Preço`. Ex: `185.00`. |
| **12** | `Peso (kg)` | Numérico | Peso total da embalagem do decante em quilos. | Obrigatório para cálculo de frete. Decimal com ponto `.`. Ex: `0.05` para 50g. |
| **13** | `Altura (cm)` | Numérico | Altura da caixa/embalagem de envio. | Obrigatório para cálculo de frete (Correios/Melhor Envio). Ex: `5`. |
| **14** | `Largura (cm)` | Numérico | Largura da caixa/embalagem de envio. | Obrigatório para cálculo de frete. Ex: `11`. |
| **15** | `Comprimento (cm)` | Numérico | Comprimento da caixa/embalagem de envio. | Obrigatório para cálculo de frete. Ex: `16`. |
| **16** | `Estoque` | Inteiro | Quantidade física disponível. | Opcional. Se em branco, o estoque é infinito. Ex: `10`. |
| **17** | `SKU` | Texto | Código de identificação único da variação. | Altamente recomendado. Ex: `DEC-CREED-AVE-10ML`. |
| **18** | `Código de barras` | Texto | Código EAN/GTIN da variação. | Opcional para decantes. Deixar em branco. |
| **19** | `Exibir na loja` | SIM / NÃO | Define se o produto estará visível na loja. | Preencher apenas na 1ª linha. Ex: `SIM`. |
| **20** | `Frete gratis` | SIM / NÃO | Define se o frete deste produto é gratuito. | Preencher em todas as variações. Ex: `NÃO` ou `SIM` (se embutido no preço de 10ml). |
| **21** | `Descrição` | HTML / Texto | Descrição completa do perfume (notas olfativas, família). | Preencher apenas na 1ª linha. Pode conter tags HTML. Ex: `<strong>Aventus</strong> é uma fragrância marcante...` |
| **22** | `Tags` | Texto | Palavras-chave separadas por vírgula para busca na loja. | Opcional. Preencher apenas na 1ª linha. Ex: `Creed, Aventus, Importado, Masculino`. |
| **23** | `Título para SEO` | Texto | Título da página para buscadores (Google). | Opcional. Limite recomendado de 70 caracteres. Preencher na 1ª linha. |
| **24** | `Descrição para SEO` | Texto | Resumo da página para buscadores (Google). | Opcional. Limite recomendado de 160 caracteres. Preencher na 1ª linha. |
| **25** | `Marca` | Texto | Marca fabricante do perfume. | Preencher apenas na 1ª linha. Ex: `Creed`. |
| **26** | `Produto Físico` | SIM / NÃO | Define se é um produto físico que precisa ser enviado. | Obrigatório. Para decantes físicos, use: `SIM`. |
| **27** | `MPN` | Texto | Manufacturer Part Number (Cód. Fabricante). | Opcional. Deixar em branco para decantes. |
| **28** | `Sexo` | Texto | Gênero alvo da fragrância. | Opcional. Ex: `Masculino`, `Feminino` ou `Unissex`. |
| **29** | `Faixa etária` | Texto | Faixa etária sugerida. | Opcional. Deixar em branco. |
| **30** | `Custo` | Numérico | Custo de aquisição/produção da variação. | Opcional (usado para relatórios internos de lucro). Ex: `90.00`. |

---

## 💡 3. Boas Práticas para Cadastro de Decantes

* **Identificador URL Único:** Nunca repita o mesmo identificador URL para perfumes diferentes. Ex:
  * `amouage-guidance` para a versão EDP normal.
  * `amouage-guidance-46` para a versão Extrait.
* **Nomes Padronizados:** Mantenha um padrão profissional para o nome do produto.
  * Padrão recomendado: `Decante [Nome do Perfume] - [Marca]` ou simplesmente `[Nome do Perfume] - [Marca] (Decante)`.
  * Ex: `Decante Guidance EDP - Amouage`.
* **Dimensões Mínimas de Frete:** Os Correios e transportadoras exigem dimensões mínimas para pacotes de envio (geralmente altura mínima de 2cm, largura 11cm e comprimento 16cm). Mesmo que o decante seja pequeno, insira dimensões viáveis para cálculo do frete real da embalagem de envio.
* **Separador de Colunas:** O arquivo gerado deve ser salvo no formato CSV delimitado por ponto e vírgula (`;`), compatível com o Excel em português e com o leitor da Nuvemshop.
