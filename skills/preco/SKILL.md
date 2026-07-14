---
name: preco
description: >-
  Calculadora de precificação para decantes e perfumes baseada na relação de arbitragem 8/2 (Brasil/China). Deve ser invocada sempre que o usuário solicitar cálculos de preços, margens de lucro ou avaliações de perfumes importados da loja do Bruno.
---

# Habilidade Preco (Precificação de Decantes)

## Overview
A habilidade `preco` realiza a estimativa inteligente de preços de venda para decantes. Ela utiliza uma lógica de ponderação de mercado que atribui peso maior à percepção de valor nacional (Brasil) e peso menor ao custo real de importação (China), permitindo repassar competitividade ao cliente e manter margens de lucro elevadas.

## Dependencies
* Python 3
* `uv` (para execução do script de apoio de forma isolada)

## Quick Start

### 1. Calcular preço do decante padrão de 10ml
```bash
python C:\Users\odeao\.gemini\config\plugins\custom-helper\skills\preco\scripts\preco.py -vc 10 -vf 100 -p1 1856 -p2 600
```

### 2. Calcular uma lista de perfumes em lote
```bash
python C:\Users\odeao\.gemini\config\plugins\custom-helper\skills\preco\scripts\preco.py -l caminho_da_lista.json
```

## Utility Scripts

O script `preco.py` gerencia o cálculo matemático detalhado.

### Parâmetros Suportados

* `-vc`, `--volume-chosen`: Volume do decante final (ml) (padrão 10.0).
* `-vf`, `--volume-full`: Volume total do frasco cheio original (ml).
* `-p1`, `--price1`: Primeira referência de preço (BRL).
* `-p2`, `--price2`: Segunda referência de preço (BRL).
* `-l`, `--list-file`: Caminho para um arquivo JSON contendo uma lista de perfumes para calcular em lote.
* `-n`, `--name`: Nome do perfume para pesquisar no concorrente King of Decants em tempo real.
* `-o`, `--output`: Caminho para exportar o relatório detalhado em JSON.

### Lógica da Fórmula

1. **Valor Ponderado do Frasco:**
   `Valor_Ponderado = ((Preço_Brasil * 8) + (Preço_China * 2)) / 10`
2. **Divisão Insumo vs Líquido:**
   * **Frasco original vazio:** `15%` do Valor Ponderado
   * **Líquido total:** `100%` do Valor Ponderado
3. **Custo do líquido por ml:**
   `Custo_Líquido_Total / Volume_Total`
4. **Preço do Decante Base:**
   `Preço_Base = ((Custo_ml * Volume_Escolhido) * 1.07) + R$ 30,00`
5. **Regra de Ajuste Competitivo (16% mais barato):**
   * Se o parâmetro `-n/--name` for passado, pesquisa o preço de 10ml no concorrente **King of Decants** (com fallback de busca avançada/categoria).
   * Se nosso preço calculado for maior que o preço do concorrente menos 16% (ou seja, `Preço_Concorrente * 0.84`), nosso preço final é ajustado para o limite competitivo: `Preço_Ajustado = Preço_Concorrente_Proporcional * 0.84`.

## Common Mistakes
1. **Ordem dos Preços:** O script ordena automaticamente os preços fornecidos, assumindo o maior como preço nacional (peso 8) e o menor como preço de custo (peso 2). Não se preocupe com a ordem em `-p1` e `-p2`.
2. **Negativar valores:** Todos os valores numéricos de preço e volume devem ser estritamente positivos.
3. **Especificar volumes incoerentes:** O volume escolhido (`-vc`) nunca deve ser maior que o volume total do frasco cheio (`-vf`).
