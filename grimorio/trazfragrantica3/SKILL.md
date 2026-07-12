---
name: trazfragrantica3
description: >-
  Gera a Foto 1 (imagem promocional de luxo focada no frasco original, limpa de estúdio) 
  para e-commerce (proporção 1280x1380px) com base na foto de referência do Fragrantica 
  e gera uma imagem comparativa de semelhança.
---

# trazfragrantica3

## Overview
Esta habilidade automatiza a preparação de dados, a geração de prompts de altíssimo luxo personalizados por marca e modelo alinhados com balcões de boutiques oficiais reais, e a validação de semelhança visual (Foto 1 do carrossel da Nuvemshop) para os perfumes do catálogo local. A imagem final deve representar o frasco real em qualidade de campanha internacional, com proporções delicadas, iluminação de estúdio refinada e escrita legível (respeitando rigorosamente a imagem original para não introduzir textos fantasmas).

## Quick Start

### 1. Preparar e obter o prompt de geração:
Para gerar os parâmetros do perfume e obter o prompt de IA em inglês para copiar:
```powershell
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\trazfragrantica3\scripts\trazfragrantica3.py prompt --perfume creed_green_irish_tweed
```

### 2. Geração da imagem (IA):
Use a ferramenta `generate_image` (ou a interface de geração do modelo) passando a imagem original do Fragrantica (`viscategoria/fotos/<p_id>_real.jpg`) em `ImagePaths` e o prompt estruturado retornado pelo comando anterior. Salve a imagem resultante como um artefato.

### 3. Finalizar e Criar Comparativo:
Execute a rotina para copiar a imagem gerada da pasta de artefatos (ou de um caminho temporário) para a pasta final de fotos com o SKU correto, criando também a imagem lado a lado para validação visual:
```powershell
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\trazfragrantica3\scripts\trazfragrantica3.py complete --perfume creed_green_irish_tweed --image <caminho_da_imagem_gerada>
```

## Como funciona
1. **Fase de Preparação (`prompt`)**:
   - O script localiza o perfume em `perfumes_data.json` e o seu SKU correspondente em `importar_nuvemshop.csv`.
   - Lê as características físicas e a marca do perfume e monta um prompt detalhado em inglês.
   - Aponta o caminho da foto original (`<id>_real.jpg`) para ser usada como base de semelhança.

2. **Fase de Geração (IA)**:
   - A IA gera a imagem comercial de balcão de boutique (1280x1380px) usando a foto real como base de formato e composição do frasco.

3. **Fase de Pós-produção (`complete`)**:
   - Move a imagem gerada para `Bruno/Identidadevisual/fotos/nuvemshop3/<sku>.jpeg`.
   - Gera uma imagem lado a lado `nuvemshop3/<sku>_comparacao.jpeg` unindo a imagem original do Fragrantica (redimensionada) e a gerada pela IA para controle de qualidade visual rápida.

## Estrutura de Arquivos
- **[SKILL.md](file:///C:/Users/odeao/OneDrive/Desktop/brem/grimorio/trazfragrantica3/SKILL.md)**: Esta documentação.
- **[trazfragrantica3.py](file:///C:/Users/odeao/OneDrive/Desktop/brem/grimorio/trazfragrantica3/scripts/trazfragrantica3.py)**: Script principal da habilidade.
- **Fotos de Saída**: Salvas na pasta [nuvemshop3](file:///C:/Users/odeao/OneDrive/Desktop/brem/Bruno/Identidadevisual/fotos/nuvemshop3).
