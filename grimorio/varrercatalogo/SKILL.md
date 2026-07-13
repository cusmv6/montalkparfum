---
name: varrercatalogo
description: Orquestrador mestre do pipeline da Montalk. Varre o catálogo, atualiza dados técnicos no Fragrantica, enriquece com resenhas críticas do ÇaFleureBon, regera cards infográficos e atualiza a planilha Nuvemshop.
---

# Habilidade varrercatalogo

Esta habilidade orquestra e executa o pipeline completo de produtos de ponta a ponta de forma 100% integrada.

## Como Funciona

O orquestrador chama as ferramentas especializadas em sequência:

```
[varrercatalogo] 
   └── 1. trazfragrantica.py (Sincroniza acordes/votos/notas)
   └── 2. opiblog.py (Enriquece com ÇaFleureBon)
   └── 3. render_profiles.py (Regera card de perfil infográfico SKU base e limpa duplicatas)
   └── 4. nuvemshop_converter.py (Exporta importar_nuvemshop.csv)
```

## Comandos Disponíveis

Execute o script no terminal usando:

*   **Para rodar um perfume específico:**
    ```bash
    python grimorio/varrercatalogo/scripts/varrercatalogo.py --perfume <id_perfume>
    ```
    *Exemplo:* `python grimorio/varrercatalogo/scripts/varrercatalogo.py --perfume amouage_guidance`

*   **Para rodar os N primeiros perfumes:**
    ```bash
    python grimorio/varrercatalogo/scripts/varrercatalogo.py --limit <numero>
    ```

*   **Para rodar todo o catálogo massivamente:**
    ```bash
    python grimorio/varrercatalogo/scripts/varrercatalogo.py --all
    ```
