---
name: trazfragrantica2
description: >-
  Gera cards visuais de composição olfativa-visual (Foto 3) para e-commerce (tamanho 1280x1380px)
  com base na imagem fotorrealista (frasco + ingredientes) salva no diretório local de fotos.
---

# trazfragrantica2

## Overview
Esta habilidade automatiza a renderização de cards visuais complementares (Foto 3 do carrossel da Nuvemshop) para os perfumes do catálogo local. O card final tem a resolução e proporção exatas de **1280x1380px** (idêntico ao card de perfil/Foto 2), centralizando a imagem da composição fotorrealista do perfume (frasco rodeado por seus ingredientes em proporção aos acordes olfativos), aplicando a moldura de design correspondente à grife e exibindo cabeçalhos e rodapés institucionais premium da marca.

## Quick Start
Para executar a geração do card de composição para um perfume específico (ou uma lista de perfumes separados por vírgula):

```powershell
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\trazfragrantica2\scripts\trazfragrantica2.py run --perfume amouage_cristal_gold_man
```

Ou para múltiplos perfumes em lote:

```powershell
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\trazfragrantica2\scripts\trazfragrantica2.py run --perfume amouage_cristal_gold_man,amouage_cristal_gold_woman
```

## Como funciona
1. O script localiza o perfume no banco de dados local `perfumes_data.json`.
2. Identifica o arquivo de imagem da composição no campo `frasco_imagem` (ex: `amouage_cristal_gold_man_composicao.png`). Se não houver, busca o arquivo fallback `<id>_real.jpg`.
3. Injeta as informações básicas (Nome, Marca, Concentração e Imagem do Frasco/Composição) no template HTML `composition_template.html`.
4. Utiliza o renderizador Playwright em modo headless para carregar a página temporária a 1280x1380px.
5. Captura o screenshot da área e salva como `nuvemshop2/<id>_composicao_perfil.jpeg` e duplica como `nuvemshop2/<id>_3.jpeg` na qualidade 92.
6. Remove os arquivos HTML temporários.

## Estrutura de Arquivos
- **[SKILL.md](file:///C:/Users/odeao/OneDrive/Desktop/brem/grimorio/trazfragrantica2/SKILL.md)**: Esta documentação.
- **[trazfragrantica2.py](file:///C:/Users/odeao/OneDrive/Desktop/brem/grimorio/trazfragrantica2/scripts/trazfragrantica2.py)**: Script orquestrador principal da automação.
- **[composition_template.html](file:///C:/Users/odeao/OneDrive/Desktop/brem/grimorio/trazfragrantica2/scripts/composition_template.html)**: Template HTML para a montagem visual do card.
- **[composition_style.css](file:///C:/Users/odeao/OneDrive/Desktop/brem/grimorio/trazfragrantica2/scripts/composition_style.css)**: Estilos CSS do card, alinhado ao sistema visual do projeto.
