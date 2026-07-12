# Manual de Identidade Visual - Montalk

Este documento reúne de forma simples e estruturada as diretrizes tipográficas, a paleta de cores e os padrões visuais que definem a presença premium da marca **Montalk** (Parfum d'Artiste) nos cards e elementos do e-commerce.

---

## 1. Tipografia (Tipos de Letra)

A identidade visual da Montalk baseia-se em um contraste clássico entre uma tipografia serifada sofisticada para títulos e uma sem serifa limpa para informações de apoio.

### 1.1. Cormorant Garamond (Serif)
*   **Aplicação:** Usada no logotipo principal **"MONTALK"**, no nome do perfume e da marca no topo dos cards de perfil, e em cabeçalhos de alta relevância.
*   **Estilos Padrão:**
    *   `font-family: 'Cormorant Garamond', serif;`
    *   **Logo Rodapé:** `font-size: 32px; font-weight: 600; letter-spacing: 8px;`
    *   **Nome do Perfume:** `font-size: 56px; font-weight: 600; letter-spacing: 2px; line-height: 1.1;`
    *   **Marca no Topo:** `font-size: 26px; font-weight: 500; letter-spacing: 6px;`
*   **Importação:** [Cormorant Garamond no Google Fonts](https://fonts.google.com/specimen/Cormorant+Garamond)

### 1.2. Montserrat (Sans-Serif)
*   **Aplicação:** Usada no texto de apoio do rodapé **"PARFUM D'ARTISTE"**, notas olfativas, tags de acordes, dados de performance/estação e textos gerais de dados do card.
*   **Estilos Padrão:**
    *   `font-family: 'Montserrat', sans-serif;`
    *   **Assinatura Rodapé:** `font-size: 10px; font-weight: 500; letter-spacing: 5px;`
    *   **Texto Geral:** `font-size: 13.5px; font-weight: 400;`
*   **Importação:** [Montserrat no Google Fonts](https://fonts.google.com/specimen/Montserrat)

### 1.3. Playfair Display (Serif - Italic)
*   **Aplicação:** Usada para destacar citações editoriais críticas de blogs e resenhas (como nas descrições de produtos no e-commerce).
*   **Estilos Padrão:**
    *   `font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-weight: 600;`
*   **Importação:** [Playfair Display no Google Fonts](https://fonts.google.com/specimen/Playfair+Display)

### 1.4. Inter (Sans-Serif)
*   **Aplicação:** Usada em legendas técnicas minúsculas e tags secundárias nas descrições de produto para melhor legibilidade em escala reduzida.
*   **Estilos Padrão:**
    *   `font-family: 'Inter', sans-serif; text-transform: uppercase;`
*   **Importação:** [Inter no Google Fonts](https://fonts.google.com/specimen/Inter)

---

## 2. Paleta de Cores (Cores Oficiais)

A paleta de cores da Montalk transmite luxo, sofisticação e nobreza através de tons terrosos, dourados e verdes profundos.

| Cor | Nome Técnico | Código HEX | Aplicação no Projeto |
| :---: | :--- | :---: | :--- |
| <div style="background:#122B24; width:30px; height:30px; border-radius:4px; margin:auto;"></div> | **Verde Garrafa Imperial** | `#122B24` | Fundo sólido do rodapé premium dos cards. |
| <div style="background:#1A3B32; width:30px; height:30px; border-radius:4px; margin:auto;"></div> | **Verde Musgo Destaque** | `#1A3B32` | Texto dos nomes de perfumes, tags ativas e marcas de gênero. |
| <div style="background:#C5A880; width:30px; height:30px; border-radius:4px; margin:auto;"></div> | **Dourado Champagne** | `#C5A880` | Subtítulos de grifes, bordas divisórias finas e texto do rodapé. |
| <div style="background:#D4AF37; width:30px; height:30px; border-radius:4px; margin:auto;"></div> | **Dourado Metálico** | `#D4AF37` | Estrelas de avaliação e detalhes da tampa do frasco de decante. |
| <div style="background:#F6F4EE; width:30px; height:30px; border-radius:4px; border:1px solid #D6D2C4; margin:auto;"></div> | **Off-White Premium** | `#F6F4EE` | Cor de fundo do card principal. |
| <div style="background:#FAF9F6; width:30px; height:30px; border-radius:4px; border:1px solid #EAE6DB; margin:auto;"></div> | **Alabastro Nobre** | `#FAF9F6` | Fundo das caixas e seções de informação (ex: pirâmide). |
| <div style="background:#4A4439; width:30px; height:30px; border-radius:4px; margin:auto;"></div> | **Marrom Terroso** | `#4A4439` | Cor principal para textos longos e descrições do perfume. |
| <div style="background:#151515; width:30px; height:30px; border-radius:4px; margin:auto;"></div> | **Preto Carbono** | `#151515` | Fundo do rótulo físico colado nos decantes de vidro. |

---

## 3. Padrões Físicos dos Cards de Imagem

*   **Resolução Padrão:** **1280px × 1380px** (largura × altura).
*   **Margens Simétricas (Padding):**
    *   Topo e Laterais: `60px`
    *   Base: `160px` (sendo `100px` para a altura do rodapé verde e `60px` de margem livre interna).
*   **Design de Componente Decante:**
    *   **Tampa:** Dourada metálica gradiente (`#FFE4A0` a `#AA8010`).
    *   **Corpo:** Vidro translúcido em camadas (`backdrop-filter: blur(2px)`).
    *   **Rótulo:** Preto fosco com borda fina dourada (`#C5A880`) e tipografia Montalk centralizada.
