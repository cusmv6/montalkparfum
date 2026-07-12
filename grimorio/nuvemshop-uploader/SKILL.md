---
name: nuvemshop-uploader
description: >-
  Conversor de lista de perfumes para planilha de importação da Nuvemshop. Deve ser ativada sempre que o usuário solicitar a conversão de listas de perfumes, marcas ou catálogos para o formato de upload da loja online (produtos.csv).
---

# Habilidade Nuvemshop Uploader (Planilha de Importação)

## Overview
A habilidade `nuvemshop-uploader` permite transformar qualquer listagem estruturada de perfumes (tabelas markdown, texto chave-valor ou listas simples de "Marca - Nome") no formato CSV oficial compatível com a importação em massa da Nuvemshop. 

O conversor cria automaticamente as variações de volumetria de decante (2ml, 5ml, 10ml) com seus respectivos pesos, dimensões de frete, SKUs exclusivos e regras de visibilidade.

## Dependencies
* Python 3
* `uv` (opcional, para execução isolada)

## Quick Start

### 1. Converter tabela do catálogo de perfumes para CSV usando preços padrão:
```bash
python C:\Users\odeao\.gemini\config\plugins\custom-helper\skills\nuvemshop-uploader\scripts\nuvemshop_converter.py -i C:\Users\odeao\OneDrive\Desktop\brem\Bruno\Decante\catalogo_perfumes.md -o C:\Users\odeao\OneDrive\Desktop\brem\Bruno\produtos\importar_nuvemshop.csv
```

### 2. Converter definindo preços personalizados para as volumetrias de decante:
```bash
python C:\Users\odeao\.gemini\config\plugins\custom-helper\skills\nuvemshop-uploader\scripts\nuvemshop_converter.py -i listagem_perfumes.txt -o produtos_nuvemshop.csv --price-2ml 40.00 --price-5ml 90.00 --price-10ml 160.00 --stock 10
```

## Formatos de Entrada Suportados

### Formato A: Tabela Markdown (Extraído de `catalogo_perfumes.md`)
O script procura por padrões de tabela e extrai colunas como:
```markdown
| # | Marca | Perfume |
| :---: | :--- | :--- |
| 1 | Amouage | Guidance |
```

### Formato B: Texto Estruturado Chave-Valor
Ideal para quando você já tem custos ou preços específicos para cada volumetria:
```text
Marca: Creed
Nome: Aventus
Preço 2ml: 50.00
Preço 5ml: 110.00
Preço 10ml: 210.00
Estoque 10ml: 3
Custo 10ml: 90.00
---
Marca: Amouage
Nome: Guidance
Preço 2ml: 45.00
Preço 5ml: 95.00
Preço 10ml: 180.00
```

### Formato C: Texto Simples Linha-por-Linha (Marca - Perfume)
```text
Creed - Aventus
Amouage - Guidance
Xerjoff - Naxos
```

## Regras de Negócio Aplicadas Automática pela Conversão

1. **Agrupamento de Variações:** As volumetrias `2ml`, `5ml` e `10ml` são salvas como linhas do mesmo produto (compartilhando o mesmo `Identificador URL`).
2. **Campos Específicos de Variação:** Apenas a primeira linha de cada produto recebe Nome, Categorias, Marca, Descrição e SEO. Linhas subsequentes mantêm esses campos em branco.
3. **SKU Automático:** Gerado no padrão `DEC-[MARCA]-[NOME]-[VOL]`.
4. **Pesos Padrão (Cálculo de Frete):**
   - 2ml = `0.02 kg` (20g)
   - 5ml = `0.03 kg` (30g)
   - 10ml = `0.05 kg` (50g)
5. **Dimensões Mínimas (Correios/Transportadora):**
   - Altura = `2cm` (2ml), `3cm` (5ml), `5cm` (10ml)
   - Largura = `11cm`
   - Comprimento = `16cm`

## Erros Comuns e Cuidados
1. **Separador do CSV:** Certifique-se de que o Excel ou editor de planilhas ao importar o arquivo use ponto e vírgula (`;`) como separador.
2. **Duplicidade de URLs:** Caso use nomes muito parecidos, revise a coluna `Identificador URL` para garantir que a Nuvemshop não misture dois perfumes diferentes como variações de um só.
