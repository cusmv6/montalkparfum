# Protocolo de Padronização de Imagens e SKUs - Montalk

Este protocolo estabelece o padrão de nomenclatura e estruturação de imagens para importação em lote na plataforma Nuvemshop.

## 1. Estrutura do SKU
Os SKUs de variação principal (2ml) e secundárias devem ser gerados com **12 caracteres** para o nome do perfume, eliminando colisões de nomes semelhantes:
- **Padrão**: `DEC-[MARCA_CURTA]-[NOME_CURTO_12_CHARS]-[VOLUMETRIA]`
- **Exemplos**:
  * `DEC-AMOU-CRISTALGOLDM-2ML` (Amouage Cristal & Gold Man, 2ml)
  * `DEC-AMOU-CRISTALGOLDW-2ML` (Amouage Cristal & Gold Woman, 2ml)
  * `DEC-AMOU-GUIDANCE-2ML` (Amouage Guidance, 2ml)

## 2. Padrão de 3 Imagens por Perfume
Para cada perfume no catálogo, devem ser geradas exatamente 3 fotos estruturadas na pasta `Bruno/Identidadevisual/fotos/nuvemshop_final/` usando o SKU correspondente da variação de 2ml:

- **Foto 1 (Frasco Real)**:
  * Nomenclatura: `<sku_2ml>_1.jpeg`
  * Origem: O arquivo original `<id>_real.jpg` de `viscategoria/fotos/`, convertido e salvo em formato JPEG.
  
- **Foto 2 (Card Perfil Olfativo)**:
  * Nomenclatura: `<sku_2ml>_2.jpeg`
  * Origem: O card completo de 1280x1380px gerado pelo renderizador `render_profiles.py` (Playwright).

- **Foto 3 (Card de Composição)**:
  * Nomenclatura: `<sku_2ml>_3.jpeg`
  * Origem: O card de estúdio fotorrealista de 1280x1380px gerado pelo renderizador `trazfragrantica2.py` (Playwright).
