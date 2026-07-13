# Habilidade opiblog (Opinião e Resenha Editorial)

## Overview
A habilidade `opiblog` automatiza a captura, síntese e curadoria da crítica especializada do prestigiado blog internacional *ÇaFleureBon* para os perfumes do catálogo da Montalk. 

Ela enriquece o arquivo `perfumes_data.json` com dois campos cruciais para a descrição de produtos do e-commerce:
1. **`resenha_editorial`**: Um resumo poético e crítico de cerca de 300 a 360 caracteres, em português, destacando a essência e o valor artístico do perfume, escrito a partir da visão dos críticos do blog.
2. **`ocasioes_recomendadas`**: Sugestões de uso, climas e intenções de projeção derivadas da análise.

## Pipeline de IA e Supervisão de Luxo
Para garantir que as descrições mantenham o nível altíssimo de curadoria exigido pelo e-commerce e evitem erros de alucinação de dados, a habilidade implementa um fluxo de duas etapas:
1. **Etapa 1 (Redação):** Um agente olfativo extrai a essência opinativa e as ocasiões sugeridas no review do *ÇaFleureBon*.
2. **Etapa 2 (Revisor Sênior de Luxo):** Um supervisor editorial revisa o texto gerado contra a pirâmide técnica de notas do perfume (evitando alucinar notas falsas), elimina clichês de marketing corporativo e garante que o tom continue autêntico, crítico e opinativo como o blog original.

## Como Usar

### 1. Processar um único perfume:
```bash
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\opiblog\scripts\opiblog.py --perfume amouage_guidance
```

### 2. Processar os primeiros N perfumes (lote inicial):
```bash
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\opiblog\scripts\opiblog.py --limit 10
```

### 3. Processar todo o catálogo:
```bash
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\opiblog\scripts\opiblog.py --all
```

### 4. Gerar apresentação PDF dos perfumes processados:
```bash
python C:\Users\odeao\OneDrive\Desktop\brem\grimorio\opiblog\scripts\opiblog.py --limit 10 --pdf
```
O PDF será salvo em `C:\Users\odeao\OneDrive\Desktop\brem\apresenta\apresenta_bruno\apresentacao_perfumes.pdf` usando renderização HTML de alta curadoria via Playwright.
