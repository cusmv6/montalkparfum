---
name: trazfragrantica
description: >-
  Busca dados do Fragrantica Brasil via urllib (bypassing Cloudflare), atualiza
  o banco de dados local 'perfumes_data.json' e regera a imagem do card de perfil
  usando o renderizador Playwright.
---

# trazfragrantica

## Overview
Esta habilidade automatiza o processo de atualizar as informações de perfumes (nota de avaliação, quantidade de votos, pirâmide olfativa, acordes originais coloridos e dados/foto do perfumista criador) diretamente do site Fragrantica Brasil, atualizando o banco de dados `perfumes_data.json` e regerando as imagens dos cards de perfil associados.

### Nova Funcionalidade - Perfumista:
- **Extração Automatizada**: Busca o nome e avatar do perfumista criador do perfume direto da página do Fragrantica.
- **Armazenamento Offline**: As fotos de avatar dos perfumistas são baixadas para a pasta local `fotos/perfumistas/<nome>.jpg` para que a renderização dos cards funcione perfeitamente sem conexão com a internet.
- **Fallback Vetorial**: Caso o perfume não possua um perfumista cadastrado, um elegante avatar silhueta vetorizado no tom dourado da marca é renderizado automaticamente.

## Quick Start
Para executar a extração e renderização para um único perfume:
```bash
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\trazfragrantica\scripts\trazfragrantica.py run --perfume amouage_interlude_53
```

### Nova Funcionalidade - Geração de Prompts de Composição (Fact-Checking):
- **Script Auxiliar**: `grimorio/trazfragrantica/scripts/gerar_prompt_composicao.py`
- **Mapeamento de Ingredientes**: Associa acordes e notas olfativas do Fragrantica (ex: Mel, Ládano, Rosa, Jasmim) a elementos físicos reais fotorrealistas em inglês.
- **Fidelidade da Grife**: Ajusta o estilo do frasco conforme a marca (ex: Byredo, Chanel, Amouage) e adiciona a placa de metal dourada com a marca exata no pedestal de mármore.
- **Como executar**:
  ```bash
  python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\trazfragrantica\scripts\gerar_prompt_composicao.py --perfume <ID_PERFUME>
  ```

Para verificar o status das cores dos acordes de um perfume no banco de dados:
```bash
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\trazfragrantica\scripts\trazfragrantica.py status --perfume amouage_interlude_53
```

## Utility Scripts
O script auxiliar está localizado em `grimorio/trazfragrantica/scripts/trazfragrantica.py`.

### Comandos:
- **`run --perfume ID`**:
  Executa a rotina de busca de dados no Fragrantica Brasil (usando `urllib` para evitar bloqueios de Cloudflare e realizando a conversão Hex/RGB de cores) e regera o perfil de card correspondente.
  - Exemplo de ID único: `amouage_interlude_53`
  - Exemplo de múltiplos IDs (lote): `--perfume amouage_guidance,amouage_guidance_46`
  - **Tratamento de Erros em Lote**: Se múltiplos perfumes forem passados (separados por vírgula) e algum deles falhar, o script continuará processando os demais e exibirá uma síntese detalhada das falhas no final do lote com o código de erro `1`.

- **`status --perfume ID`**:
  Inspeciona o banco de dados local para verificar se o perfume existe e se as cores dos seus acordes já foram extraídas com sucesso ou se ainda estão no tom dourado padrão (`#C5A880`).

## Rate Limiting
Nas execuções em lote (múltiplos perfumes), o script insere automaticamente um **atraso (delay) de 1 segundo** entre as requisições HTTP para respeitar os limites de requisições do site do Fragrantica e evitar banimentos de IP.

## Common Mistakes
1. **Passar IDs inexistentes**: Certifique-se de que o ID do perfume existe no arquivo `perfumes_data.json` local antes de rodar o comando.
2. **URLs desatualizados ou errados no DuckDuckGo**: Caso o script de busca automatizada encontre uma página de perfume errada (devido a homônimos), adicione manualmente o mapeamento de URL no dicionário `URL_OVERRIDES` dentro de `trazfragrantica.py`.
