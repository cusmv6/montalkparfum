---
name: estagiariovisual
description: Auxiliar de arte digital para o e-commerce. Unifica a orquestração e geração automática das Fotos 1, 2 e 3 de produtos a partir dos dados do catálogo de perfumes, acionando inteligência generativa de imagem para criar composições fotorrealistas de luxo.
---

# Habilidade estagiariovisual (Maestro de Arte)

Esta habilidade costura as três ferramentas visuais do ecossistema da Montalk:

1.  **Foto 1 (Estúdio de Luxo):** Gerada via `trazfragrantica3.py complete` a partir de uma foto de estúdio do frasco.
2.  **Foto 2 (Perfil Olfativo/Infográfico):** Gerada via `render_profiles.py` contendo acordes, notas e o frasco.
3.  **Foto 3 (Composição Olfativa):** Gerada via `trazfragrantica2.py` a partir da imagem fotorrealista com ingredientes.

## Como Funciona a Geração Automatizada de Imagens
Se a imagem de composição do perfume (`[id]_composicao.png`) não existir na pasta de fotos, o `estagiariovisual` analisa os acordes e notas do perfume e usa a ferramenta interna de geração de imagens do Gemini para criar o frasco original em cima de um pedestal cercado pelos ingredientes físicos da pirâmide olfativa.

## Comandos Disponíveis

Execute o script no terminal usando:

*   **Processar um perfume específico:**
    ```bash
    python SUMMONS/estagiariovisual/scripts/estagiariovisual.py --perfume <id_perfume>
    ```

*   **Processar N perfumes:**
    ```bash
    python SUMMONS/estagiariovisual/scripts/estagiariovisual.py --limit <numero>
    ```

*   **Processar todo o catálogo:**
    ```bash
    python SUMMONS/estagiariovisual/scripts/estagiariovisual.py --all
    ```
