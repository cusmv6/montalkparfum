import os
import sys
import json
import re
import urllib.request
import urllib.parse
import ssl
import time
from bs4 import BeautifulSoup

# Importa Playwright para renderizar o PDF
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass

# Importa o SDK oficial do Gemini
try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

WORKSPACE_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem"
JSON_PATH = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\produtos\catalogo.json"
OUTPUT_PDF_DIR = os.path.join(WORKSPACE_DIR, "apresenta", "apresenta_bruno")
OUTPUT_PDF_PATH = os.path.join(OUTPUT_PDF_DIR, "apresentacao_perfumes.pdf")

# 5 Exemplares de Referência Editorial (Few-Shot) para alinhar a IA
FEW_SHOT_EXAMPLES = """
EXEMPLO 1:
Perfume: CRISTAL & GOLD MAN (AMOUAGE)
Perfumista: Alexandra Carlin, Ano: 2023
Notas: Aldeídos, Mel, Olíbano, Néroli, Petitgrain, Bergamota, Heliotrópio, Jasmim, Rosa Damascena, Ylang Ylang, Raíz de Orris, Civeta, Âmbar Cinzento, Ládano, Sândalo, Patchouli, Vetiver, Madeira Guaiac
Resenha Editorial: "Cristal & Gold Man é uma reinterpretação majestosa do clássico de 1983 pela perfumista Alexandra Carlin. Este Floral Aldeídico Amadeirado de alta concentração (25% de óleo) funde aldeídos brilhantes a um corpo floral suntuoso de jasmim e rosa, repousando sobre uma base animalítica marcante de civeta e sândalo. Um aroma opulento, atemporal e luxuoso."
Ocasiões Recomendadas: "Ideal para ocasiões de gala, eventos formais noturnos ou climas amenos onde se busca exalar opulência e sofisticação clássica."

EXEMPLO 2:
Perfume: CRISTAL & GOLD WOMAN (AMOUAGE)
Perfumista: Alexandra Carlin, Ano: 2023
Notas: Aldeídos, Néroli, Petitgrain, Olíbano, Bergamota, Rosa, Jasmim, Heliotrópio, Ylang Ylang, Raíz de Orris, Âmbar, Civeta, Baunilha de Bourbon, Vetiver, Ládano, Sândalo
Resenha Editorial: "Criado para comemorar os 40 anos da Amouage, Cristal & Gold Woman é uma reedição majestosa feita por Alexandra Carlin. Este Floral Aldeídico de alta concentração (25% de óleo) funde aldeídos luminosos e néroli a um corpo suntuoso de jasmim e rosa, repousando sobre uma base marcante de civeta e baunilha de Bourbon. Luxo atemporal."
Ocasiões Recomendadas: "Excelente para jantares de gala, noites frias de outono e inverno, ou ocasiões especiais onde se deseja projetar uma aura aristocrática e elegante."

EXEMPLO 3:
Perfume: GUIDANCE (AMOUAGE)
Perfumista: Quentin Bisch, Ano: 2023
Notas: Pera, Avelã, Olíbano, Osmanthus, Rosa, Açafrão, Jasmim Sambac, Sândalo, Baunilha, Akigalawood, Âmbar Cinzento, Ládano
Resenha Editorial: "Destaque da coleção Odyssey (Capítulo III) da Amouage, Guidance é um Floral Frutado fascinante assinado por Quentin Bisch. O perfume reinventa a clássica tríade de rosa, olíbano e âmbar cinzento com notas viciantes de pera e avelã. Uma fragrância de textura sedosa, sensualidade carnal e projeção magnética. Uma obra de arte moderna."
Ocasiões Recomendadas: "Perfeito para climas amenos, encontros românticos ou jantares sofisticados onde se busca uma presença marcante, cremosa e altamente sedutora."

EXEMPLO 4:
Perfume: GUIDANCE 46 (AMOUAGE)
Perfumista: Quentin Bisch, Ano: 2024
Notas: Pera, Avelã, Olíbano, Pimenta Rosa, Rosa de Água, Amêndoa Amarga, Osmanthus, Rosa de Maio, Açafrão, Jasmim Sambac, Sândalo, Baunilha, Akigalawood, Âmbar Cinzento, Ládano, Georgywood, Cipriol, Ambrette
Resenha Editorial: "Guidance 46 é um Extrait de Parfum magnífico que eleva a assinatura de Quentin Bisch ao ápice da intensidade (46% de concentração de óleos). Uma evolução rica e misteriosa que aprofunda as notas de pera e avelã com um toque opulento de osmanthus, sândalo e fava tonka. Uma fragrância hipnótica, de fixação colossal e presença inesquecível."
Ocasiões Recomendadas: "Excelente para grandes eventos, climas frios e ocasiões solenes onde se busca a máxima distinção olfativa com um rastro monumental."

EXEMPLO 5:
Perfume: INTERLUDE 53 (AMOUAGE)
Perfumista: Pierre Negrin, Ano: 2020
Notas: Orégano, Pimenta da Jamaica, Bergamota, Incenso, Âmbar, Opoponax, Ládano, Fumaça, Agarwood (Oud), Couro, Patchouli, Sândalo
Resenha Editorial: "Interlude 53 eleva o clássico Amouage a uma dimensão tridimensional. Com 53% de óleos puros, é mais profundo, macio e intenso. O aroma equilibra o defumado do incenso e orégano com um toque de couro e resinas mais animalítico e imponente. Uma obra de arte moderna."
Ocasiões Recomendadas: "Ideal para noites frias de outono e inverno, encontros noturnos sofisticados ou eventos formais que exigem uma presença magnética e de extremo luxo."
"""

def buscar_artigo_cafleurebon(brand, name):
    query = f"site:cafleurebon.com {brand} {name} review"
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    print(f"   [*] Buscando no DuckDuckGo por artigos de '{brand} {name}' no ÇaFleureBon...")
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=context, timeout=8) as response:
            html = response.read().decode('utf-8', errors='replace')
            
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        
        target_url = None
        for link in links:
            href = link.get("href", "")
            if "cafleurebon.com/" in href and "/tag/" not in href and "/category/" not in href and "/page/" not in href:
                # Extrai a URL real
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                actual_url = qs.get("uddg", [None])[0]
                if not actual_url and "uddg=" in href:
                    match = re.search(r'uddg=(https%3A%2F%2F[^\s&]+)', href)
                    if match:
                        actual_url = urllib.parse.unquote(match.group(1))
                if not actual_url:
                    actual_url = href
                
                if "cafleurebon.com/" in actual_url:
                    target_url = actual_url.split("?")[0]
                    break
        
        if target_url:
            print(f"   [+] Artigo encontrado: {target_url}")
            # Baixa o conteúdo da página do ÇaFleureBon
            req_page = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req_page, context=context, timeout=10) as page_resp:
                page_html = page_resp.read().decode('utf-8', errors='replace')
            
            page_soup = BeautifulSoup(page_html, "html.parser")
            # Pega o texto do artigo principal (comum no WordPress do blog)
            entry_content = page_soup.find("div", class_="entry-content")
            if not entry_content:
                entry_content = page_soup.find("article")
            
            if entry_content:
                text = entry_content.get_text(separator=" ", strip=True)
                # Remove espaços duplos
                text = re.sub(r'\s+', ' ', text)
                # Retorna os primeiros 8000 caracteres para não estourar o prompt
                return text[:8000]
            else:
                text = page_soup.get_text(separator=" ", strip=True)
                return re.sub(r'\s+', ' ', text)[:6000]
    except Exception as e:
        print(f"   [AVISO] Falha ao raspar review em tempo real: {e}. O Gemini usará fallback criativo.")
    return None

def enriquecer_perfume(perfume, client):
    p_id = perfume.get("id")
    brand = perfume.get("marca")
    name = perfume.get("nome")
    perfumistas = ", ".join(perfume.get("perfumistas", []))
    ano = perfume.get("ano_lancamento", "N/A")
    
    # Junta as notas e acordes
    notas = perfume.get("notas", {})
    piramide_text = f"Saída: {', '.join(notas.get('topo', []))}. Corpo: {', '.join(notas.get('coracao', []))}. Fundo: {', '.join(notas.get('base', []))}"
    acordes_list = [f"{a['nome']} ({a['intensidade']:.1f}%)" for a in perfume.get("principais_acordes", [])]
    acordes_text = ", ".join(acordes_list)
    
    # 1. Tenta buscar texto real do ÇaFleureBon
    raw_review_text = buscar_artigo_cafleurebon(brand, name)
    
    # 2. Constrói o Prompt de Redação (Etapa 1)
    prompt_redator = f"""
Você é um redator de perfumaria de nicho especialista em traduzir resenhas críticas e criar poesia olfativa.
Sua tarefa é analisar o review do ÇaFleureBon sobre o perfume "{name}" da marca "{brand}".

Informações Técnicas do Perfume:
- Perfumista: {perfumistas}
- Ano de lançamento: {ano}
- Pirâmide de Notas: {piramide_text}
- Principais Acordes Olfativos (ordenados por intensidade física): {acordes_text}

Review do ÇaFleureBon (se disponível):
\"\"\"{raw_review_text if raw_review_text else "Não disponível. Use seu conhecimento enciclopédico sobre os artigos do blog ÇaFleureBon para este perfume."}\"\"\"

Instruções e Filtro de Acordes:
1. Escreva um rascunho de resenha crítica editorial em português inspirado na perspectiva do ÇaFleureBon. O texto deve ter cerca de 300 a 360 caracteres.
2. PRIORIZAÇÃO SENSORIAL: Os acordes principais definem o que é fisicamente mais presente no perfume. Ao sintetizar as metáforas, sensações e texturas poéticas descritas no ÇaFleureBon, você deve PRIORIZAR estritamente as passagens que descrevem e correspondem aos 3 acordes mais intensos (ex: se o acorde dominante for Amadeirado, foque em imagens mentais de madeira nobre descritas pelo crítico). Evite gastar caracteres com notas irrelevantes.
3. Tom Curatorial Artístico: Não faça marketing de vendas. Descreva o perfume como uma obra de arte, focando em cenários poéticos, analogias e texturas (seda, névoa, solene, etc.).
4. Identifique e escreva as ocasiões de uso recomendadas sugeridas pela crítica.
"""

    print("   [*] Gerando rascunho do redator olfativo...")
    response_draft = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt_redator]
    )
    draft_text = response_draft.text.strip()
    
    # 3. Constrói o Prompt do Supervisor Editorial Sênior de Luxo (Etapa 2)
    prompt_supervisor = f"""
Você é o Diretor Editorial e Revisor Sênior de Textos de Luxo da Montalk Perfumes.
Seu critério de revisão é de altíssimo nível, pois a marca preza por extrema sofisticação estética, conformidade de fatos e verdade sensorial.

Sua tarefa é analisar e refinar o rascunho da resenha e ocasiões gerados para o perfume "{name}" ({brand}).

Metadados Técnicos Oficiais (Use para conferir os fatos):
- Nome Oficial: {name}
- Grife: {brand}
- Perfumista Criador: {perfumistas}
- Ano de Lançamento: {ano}
- Notas Oficiais da Pirâmide: {piramide_text}
- Principais Acordes Olfativos: {acordes_text}

Rascunho a ser revisado:
\"\"\"{draft_text}\"\"\"

Diretrizes de Revisão de Luxo (Fact-Checking, Estilo e Consistência):
1. FACT-CHECK TOTAL: Verifique se o texto menciona qualquer nota olfativa ou ingrediente que NÃO esteja na lista de notas oficiais acima. Se houver notas alucinadas ou incorretas, modifique o texto para omitir ou corrigir o ingrediente.
2. CONFORMIDADE DE DADOS: Garanta que o ano de lançamento e o perfumista citados batam exatamente com os metadados técnicos fornecidos.
3. CONSISTÊNCIA SENSORIAL: Certifique-se de que as metáforas literárias descrevam e destaquem as sensações físicas dos acordes mais presentes e intensos do perfume, mantendo a verdade do que o cliente sentirá ao usar.
4. ESTILO LUXO SEM CLICHÊS: Elimine termos vulgares, adjetivos de vendas vazios ("maravilhoso", "delicioso", "perfumaço", "cheiro de rico") e gírias de massa. Substitua por uma prosa lírica, fluida, artística e digna de prêmios editoriais (Curadoria Artística ÇaFleureBon).
5. ALMA OPINATIVA: Mantenha o caráter poético, subjetivo e independente do crítico original.

Exemplos de Referência de Sucesso (Siga exatamente este padrão e tom):
{FEW_SHOT_EXAMPLES}

Responda ESTRITAMENTE em formato JSON com as chaves:
{{
  "resenha_editorial": "Sua resenha final revisada (em torno de 300-360 caracteres)",
  "ocasioes_recomendadas": "Suas ocasiões sugeridas revisadas"
}}
"""

    print("   [*] Executando a revisão sênior de luxo e fact-checking...")
    response_final = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt_supervisor],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    try:
        res_json = json.loads(response_final.text.strip())
        return res_json
    except Exception as e:
        print(f"   [ERRO] Falha ao decodificar JSON final da IA: {e}")
        # Tenta extrair usando regex básico em caso de formatação quebrada
        text_clean = response_final.text.strip()
        match_resenha = re.search(r'"resenha_editorial"\s*:\s*"([^"]+)"', text_clean)
        match_ocasioes = re.search(r'"ocasioes_recomendadas"\s*:\s*"([^"]+)"', text_clean)
        if match_resenha and match_ocasioes:
            return {
                "resenha_editorial": match_resenha.group(1),
                "ocasioes_recomendadas": match_ocasioes.group(1)
            }
    return None

def gerar_apresentacao_pdf(perfumes_list):
    print("\n[INFO] Inicializando a geração do PDF de Apresentação...")
    
    # Estilo CSS e HTML premium em formato de catálogo belas-artes
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Apresentação - Perspectiva ÇaFleureBon</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500&family=Playfair+Display:ital,wght@0,500;0,600;1,500&display=swap" rel="stylesheet">
    <style>
        @page {
            size: A4;
            margin: 20mm;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: #FAF9F6;
            color: #2C2A29;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        .page-header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 1.5px solid #C5A880;
            padding-bottom: 20px;
        }
        .catalog-title {
            font-family: 'Playfair Display', serif;
            font-size: 28px;
            font-weight: 500;
            color: #1A3B32;
            letter-spacing: 1.5px;
            margin: 0;
            text-transform: uppercase;
        }
        .catalog-subtitle {
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 16px;
            color: #8C8475;
            margin: 5px 0 0 0;
        }
        .perfume-card {
            background-color: #FFFFFF;
            border: 1px solid rgba(197, 168, 128, 0.4);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.02);
            page-break-inside: avoid;
        }
        .perfume-header {
            font-size: 14px;
            color: #5E5A54;
            margin-bottom: 15px;
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            letter-spacing: 0.5px;
        }
        .perfume-title {
            font-family: 'Playfair Display', serif;
            font-size: 20px;
            color: #1A3B32;
            margin: 0;
            font-weight: 600;
        }
        .perfume-brand {
            font-weight: 400;
            color: #C5A880;
        }
        .critique-box {
            position: relative;
            background-color: #FCFAF7;
            border-left: 3px solid #C5A880;
            padding: 20px 25px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        .critique-title {
            font-family: 'Playfair Display', serif;
            font-style: italic;
            font-size: 16px;
            color: #1A3B32;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .critique-subtitle {
            font-size: 9px;
            color: #8C8475;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: -8px;
            margin-bottom: 15px;
            display: block;
        }
        .critique-text {
            font-family: 'Cormorant Garamond', serif;
            font-size: 16.5px;
            font-style: italic;
            line-height: 1.7;
            color: #4A4439;
            margin-bottom: 15px;
        }
        .occasions {
            font-family: 'Cormorant Garamond', serif;
            font-size: 16px;
            color: #2C2A29;
            margin-top: 15px;
        }
        .occasions strong {
            font-family: 'Playfair Display', serif;
            font-style: italic;
            color: #1A3B32;
            font-weight: 600;
        }
        .notes-list {
            margin-top: 20px;
            padding-left: 0;
            list-style: none;
            font-size: 13.5px;
            color: #5E5A54;
        }
        .notes-list li {
            margin-bottom: 8px;
            position: relative;
            padding-left: 18px;
        }
        .notes-list li::before {
            content: "•";
            color: #C5A880;
            position: absolute;
            left: 0;
            font-size: 16px;
            top: -2px;
        }
        .footer-note {
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 13px;
            color: #8C8475;
            text-align: center;
            border-top: 1px solid rgba(197, 168, 128, 0.2);
            padding-top: 12px;
            margin-top: 20px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="page-header">
        <h1 class="catalog-title">Montalk - Parfum d'Artiste</h1>
        <p class="catalog-subtitle">Perspectivas e Resenhas da Crítica de Perfumaria de Luxo</p>
    </div>
"""

    for p in perfumes_list:
        notas = p.get("notas", {})
        topo = ", ".join(notas.get("topo", []))
        coracao = ", ".join(notas.get("coracao", []))
        base = ", ".join(notas.get("base", []))
        
        # Extração inteligente do perfumista criador (fallback de dados no e-commerce)
        perfumistas_list = p.get("perfumistas", [])
        if len(perfumistas_list) == 1 and perfumistas_list[0].strip().lower() == "perfumista":
            perfumistas_list = []
            
        perfumistas_str = ""
        if perfumistas_list:
            validos = [n.strip() for n in perfumistas_list if n.strip().lower() not in ["", "perfumista"]]
            if validos:
                perfumistas_str = ", ".join(validos[:-1]) + " e " + validos[-1] if len(validos) > 1 else validos[0]
                
        if not perfumistas_str:
            detalhes = p.get("perfumistas_detalhes", [])
            if detalhes:
                nomes = [d.get("nome", "").strip() for d in detalhes if d.get("nome", "").strip().lower() not in ["", "perfumista"]]
                if nomes:
                    perfumistas_str = ", ".join(nomes[:-1]) + " e " + nomes[-1] if len(nomes) > 1 else nomes[0]
                    
        if not perfumistas_str:
            resenha = p.get("resenha_editorial", "")
            if resenha:
                match = re.search(r'(?:assinado|criado|feito|desenvolvido)\s+por\s+([A-Z][a-zA-ZÀ-ÿ]+(?:\s+[A-Z][a-zA-ZÀ-ÿ]+)+)', resenha)
                if match:
                    perfumistas_str = match.group(1).strip()
                    
        if not perfumistas_str:
            perfumistas_str = "Perfumista Exclusivo"
            
        gen_fam = f"{p.get('familia_olfativa', 'Exclusivo')} {p.get('genero_comercial', 'Compartilhável')}"
        ano = p.get("ano_lancamento", "2020")
        
        html_content += f"""
        <div class="perfume-card">
            <div class="perfume-header">
                <strong>{p['nome'].upper()}</strong> de <span class="perfume-brand"><strong>{p['marca'].upper()}</strong></span> é um perfume <em>{gen_fam}</em> lançado em <strong>{ano}</strong>. O perfumista que assina esta fragrância é <strong>{perfumistas_str}</strong>.
            </div>
            
            <div class="critique-box">
                <div class="critique-title">"A perspectiva de ÇaFleureBon...</div>
                <span class="critique-subtitle">PERSPECTIVA EDITORIAL DO BLOG CRÍTICO MAIS PREMIADO DA PERFUMARIA DE NICHO</span>
                <span class="critique-subtitle" style="margin-top: -12px; font-size: 7.5px; font-style: italic; opacity: 0.85;">(PERFUMED PLUME AWARDS, FRAGRANCE FOUNDATION AWARDS - FIFI, BASENOTES READER'S AWARDS)</span>
                
                <div class="critique-text">
                    {p.get('resenha_editorial', 'Crítica editorial em processamento.')}
                </div>
                
                <div class="occasions">
                    <strong>Ocasiões Recomendadas:</strong> <em>{p.get('ocasioes_recomendadas', 'Ocasiões recomendadas em processamento.')} "</em>
                </div>
            </div>
            
            <ul class="notes-list">
                <li><strong>Notas de Saída (5 a 15 min):</strong> {topo}</li>
                <li><strong>Notas de Corpo (2 a 6 h):</strong> {coracao}</li>
                <li><strong>Notas de Fundo (6 a 12h+):</strong> {base}</li>
            </ul>
            
            <div class="footer-note">
                Os decantes são uma excelente oportunidade para conhecer e testar fragrâncias exclusivas antes de investir em um frasco cheio. Nossos decantes são fracionados de forma profissional diretamente do frasco original em porta-perfumes de vidro com borrifador.
            </div>
        </div>
        """
        
    html_content += """
</body>
</html>
"""

    temp_html_path = os.path.join(WORKSPACE_DIR, "apresenta", "temp_apresentacao.html")
    
    # Garante que a pasta apresenta exista
    os.makedirs(os.path.dirname(temp_html_path), exist_ok=True)
    os.makedirs(OUTPUT_PDF_DIR, exist_ok=True)
    
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Renderiza via Playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            file_url = f"file:///{temp_html_path.replace(os.sep, '/')}"
            page.goto(file_url)
            
            # Espera carregar fontes e estilizações
            page.wait_for_timeout(2000)
            
            page.pdf(
                path=OUTPUT_PDF_PATH,
                format="A4",
                print_background=True,
                margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
            )
            
            browser.close()
            print(f"[SUCESSO] Apresentação PDF gerada com sucesso em: {OUTPUT_PDF_PATH}")
    except Exception as e:
        print(f"[ERRO] Falha ao renderizar PDF via Playwright: {e}")
        
    # Limpa arquivo temporário
    try:
        os.remove(temp_html_path)
    except OSError:
        pass

def main():
    parser = argparse_setup()
    args = parser.parse_args()
    
    if not os.path.exists(JSON_PATH):
        print(f"[ERRO] Banco de dados não encontrado em: {JSON_PATH}")
        sys.exit(1)
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        perfumes = json.load(f)
        
    target_perfumes = []
    
    if args.perfume:
        target_ids = [i.strip() for i in args.perfume.split(",")]
        target_perfumes = [p for p in perfumes if p.get("id") in target_ids]
        print(f"[INFO] Selecionados {len(target_perfumes)} perfumes específicos via ID.")
    elif args.limit:
        target_perfumes = perfumes[:args.limit]
        print(f"[INFO] Selecionados os primeiros {args.limit} perfumes do catálogo.")
    elif args.all:
        target_perfumes = perfumes
        print(f"[INFO] Selecionado todo o catálogo ({len(perfumes)} perfumes).")
    else:
        print("[AVISO] Nenhum escopo definido. Use --perfume <id>, --limit <n> ou --all.")
        sys.exit(0)
        
    if not target_perfumes:
        print("[AVISO] Nenhum perfume encontrado para o escopo definido.")
        sys.exit(0)
        
    if not args.pdf_only:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("[ERRO] A variável GEMINI_API_KEY não foi encontrada no ambiente.")
            sys.exit(1)
            
        client = genai.Client(api_key=api_key)
        
        print(f"\n[INFO] Iniciando processamento de {len(target_perfumes)} perfume(s)...")
        
        for idx, perfume in enumerate(target_perfumes):
            p_id = perfume.get("id")
            print(f"\n[{idx+1}/{len(target_perfumes)}] Enriquecendo: {perfume['nome']} ({perfume['marca']})...")
            
            enrich_data = enriquecer_perfume(perfume, client)
            
            if enrich_data:
                perfume["resenha_editorial"] = enrich_data.get("resenha_editorial", "")
                perfume["ocasioes_recomendadas"] = enrich_data.get("ocasioes_recomendadas", "")
                print(f"   [OK] Resenha: {perfume['resenha_editorial'][:60]}...")
                print(f"   [OK] Ocasiões: {perfume['ocasioes_recomendadas'][:60]}...")
            else:
                print("   [ERRO] Falha ao gerar enriquecimento para este perfume.")
                
            # Rate limiting preventivo para chamadas à API e busca DuckDuckGo
            time.sleep(1.5)
            
        # Grava de volta no JSON
        with open(JSON_PATH, "w", encoding="utf-8") as f_out:
            json.dump(perfumes, f_out, indent=2, ensure_ascii=False)
        print(f"\n[SUCESSO] Arquivo {JSON_PATH} atualizado com sucesso no disco!")
        
    # Gera o PDF se solicitado
    if args.pdf or args.pdf_only:
        # Pega a versão mais recente dos perfumes enriquecidos
        gerar_apresentacao_pdf(target_perfumes)

def argparse_setup():
    import argparse
    parser = argparse.ArgumentParser(description="opiblog - Enriquecimento editorial de perfumes via ÇaFleureBon e IA")
    parser.add_argument("--perfume", help="IDs de perfumes separados por vírgula")
    parser.add_argument("--limit", type=int, help="Limita a quantidade de perfumes do início do JSON")
    parser.add_argument("--all", action="store_true", help="Processa todo o catálogo")
    parser.add_argument("--pdf", action="store_true", help="Gera uma apresentação PDF após o processamento")
    parser.add_argument("--pdf-only", action="store_true", help="Gera apenas o PDF a partir dos dados existentes sem chamar a IA")
    return parser

if __name__ == "__main__":
    main()
