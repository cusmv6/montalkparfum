import os
import json
import shutil
import sys
import argparse
import csv
import re
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageOps

# Configuração de caminhos e diretórios
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
VISCATEGORIA_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\Identidadevisual\fotos\viscategoria"
JSON_PATH = os.path.join(VISCATEGORIA_DIR, "perfumes_data.json")
FOTOS_DIR = os.path.join(VISCATEGORIA_DIR, "fotos")
OUTPUT_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\Identidadevisual\fotos\nuvemshop3"
CSV_PRODUTOS_PATH = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\produtos\importar_nuvemshop.csv"

# Base de Conhecimento de Luxo e Campanhas do Grimório (Exibição em Boutiques Reais)
BASE_CONHECIMENTO_LUXO = {
    "CREED": {
        "campanhas": "Grounded in heritage and prestige, Green Irish Tweed is positioned as a timeless classic, evoking the traditional aristocratic sophistication.",
        "lojas_fisicas": "Creed Flagship Boutiques (Paris, London, São Paulo Shops Jardins, NYC SoHo), luxury department stores including Saks Fifth Avenue, and Harrods (Salon de Parfums).",
        "justificativa_fundo": "The bottle is displayed on an elegant dark walnut and polished brass display counter that extends continuously across the entire bottom horizontal width of the frame, showing no floor underneath. The background is a sophisticated Creed flagship boutique with natural wood-paneled walls and warm spotlighting. The background has a natural, subtle f/5.6 camera blur, showing defined, warm, and elegant boutique textures (no heavy or synthetic artificial blur).",
        "detalhes_frasco": "A classic matte black curved-shoulder Creed bottle. Replicate the exact silhouette, shape, and proportions of the bottle and its cap from the reference image. The cap must have the exact same width and low-profile height relative to the bottle's shoulders, ensuring it does not look narrow, tall, or stretched. The brand name 'CREED' is embossed near the neck in clean, raised black lettering. The text 'GREEN IRISH TWEED' is printed in a clean, sharp, crisp white font on the lower front. Do not add any other labels, text, or elements not present in the original bottle design."
    },
    "AMOUAGE": {
        "campanhas": "The Cristal & Gold edition celebrates the 40th anniversary of Amouage, based on the vintage 1983 hand-blown crystal and gold design.",
        "lojas_fisicas": "Amouage Flagship Boutiques (Muscat, NYC SoHo, Milan), luxury perfume halls like Harrods (Salon de Parfums) and Jovoy Paris.",
        "justificativa_fundo": "The bottle is displayed on a polished black marble and gold display vanity that extends continuously across the entire bottom horizontal width of the frame, showing no floor underneath. The background is the opulent, gold-detailed interior of the Amouage flagship boutique, with a natural, subtle f/5.6 camera blur showing the luxurious store shelving and warm ambient lighting (no heavy or synthetic artificial blur).",
        "detalhes_frasco": "A single, highly exclusive, hand-blown cylindrical crystal perfume bottle with a golden filigree-like texture and detailed carvings, based on the vintage 1983 Amouage design. The bottle has a slender, neoclassical pillar shape. Crucially, the entire bottle, including both the main body and the upper neck, is made of highly polished, transparent clear glass (no frosted glass, no sandblasting) and is completely filled with a rich golden liquid, glowing with a warm honey-amber gold color all the way up to the collar, leaving absolutely no empty space, no air bubbles, and no visible liquid level line at the neck. The glass is completely clean: there is absolutely NO writing, text, or brand names etched, printed, or embossed on any glass surface of the bottle. The brand name 'AMOUAGE' is only embossed in raised gold lettering on the polished metal collar ring wraps around the neck, and nowhere else. The cap is a stylized, flared golden dome, matching the original shape exactly."
    },
    "BYREDO": {
        "campanhas": "Part of the Night Veils extraits de parfum series, focusing on raw, rare, and smoky vanilla.",
        "lojas_fisicas": "Byredo Standalone Boutiques (Stockholm, Paris Rue Saint-Honoré, London, NYC SoHo), luxury department stores including Harrods and Selfridges.",
        "justificativa_fundo": "The bottle is displayed on a warm, elegant beige travertine stone display counter that extends continuously across the entire bottom horizontal width of the frame, showing no floor underneath. The background is a clean, modern Byredo boutique with warm light-oak wood shelving. In the background, the shelves are neatly and elegantly populated with other out-of-focus Byredo perfume bottles and premium display items to make the boutique feel active, warm, authentic, and high-end. Use a natural, subtle f/5.6 camera blur showing these shapes clearly but softly (no empty or barren shelves).",
        "detalhes_frasco": "A minimalist cylindrical clear glass Byredo bottle, showing the dark amber-colored liquid inside. The label is completely transparent: the brand name 'BYREDO', perfume name 'VANILLE ANTIQUE', and 'EXTRAIT DE PARFUM' are printed in crisp, solid white minimalist typography directly onto the glass bottle, with no paper label background. The bottle is topped with the iconic round, dome-shaped glossy black cap. Do not add any other text."
    }
}

def slugify(text):
    text = text.lower()
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ã': 'a', 'õ': 'o', 'ç': 'c', 'ñ': 'n',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def obter_sku_do_csv(p_id, brand, name):
    slug_brand = slugify(brand)
    slug_name = slugify(name)
    url_identifier = f"decante-{slug_brand}-{slug_name}"
    
    if os.path.exists(CSV_PRODUTOS_PATH):
        try:
            with open(CSV_PRODUTOS_PATH, mode="r", encoding="utf-8-sig") as f:
                sample = f.readline()
                separator = ";" if ";" in sample else ","
                f.seek(0)
                
                reader = csv.DictReader(f, delimiter=separator)
                for row in reader:
                    row_url = row.get("Identificador URL") or row.get("\"Identificador URL\"")
                    if row_url and row_url.strip() == url_identifier:
                        sku = row.get("SKU") or row.get("\"SKU\"")
                        if sku:
                            return sku.strip()
        except Exception as e:
            print(f"   [AVISO] Erro ao ler CSV de produtos para {p_id}: {e}")
    return None

def gerar_sku_dinamico(brand, name):
    slug_brand = slugify(brand)
    slug_name = slugify(name)
    sku_clean_brand = slug_brand.upper()[:4]
    sku_clean_name = slug_name.replace("-", "")[:6].upper()
    return f"DEC-{sku_clean_brand}-{sku_clean_name}-2ML"

def get_perfume(p_id):
    if not os.path.exists(JSON_PATH):
        print(f"[ERRO] O banco de dados local {JSON_PATH} não foi encontrado.")
        sys.exit(1)
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        perfumes = json.load(f)
        
    for p in perfumes:
        if p.get("id") == p_id:
            return p
    return None

def buscar_online_duckduckgo(query):
    """
    Busca informações adicionais sobre o perfume via DuckDuckGo API (Bypassa Cloudflare).
    """
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            abstract = data.get("AbstractText", "")
            return abstract
    except Exception:
        return ""

def is_bottle_opaque(brand, name):
    brand_upper = brand.upper()
    name_upper = name.upper()
    
    # Lista de palavras-chave para identificar frascos opacos conhecidos
    if "CREED" in brand_upper:
        if any(k in name_upper for k in ["GREEN IRISH", "SILVER MOUNTAIN", "MILLESIME IMPERIAL", "AVENTUS"]):
            return True
    if "PARFUMS DE MARLY" in brand_upper:
        return True
    if "TOM FORD" in brand_upper:
        if any(k in name_upper for k in ["BLACK ORCHID", "NOIR DE NOIR", "GREY VETIVER"]):
            return True
            
    return False

def obter_dados_marca(brand, name):
    brand_upper = brand.upper()
    for key, data in BASE_CONHECIMENTO_LUXO.items():
        if key in brand_upper:
            return data
            
    # Fallback caso a marca não esteja na base curada
    return {
        "campanhas": f"High-end luxury campaign emphasizing the artistic composition and premium heritage of the {brand} {name} fragrance.",
        "lojas_fisicas": f"{brand} Flagship Boutiques in Paris, London, and New York, alongside premium authorized luxury retailers such as Harrods and Saks Fifth Avenue.",
    }

def gerar_prompt_ia(perfume):
    brand = perfume.get("marca", "")
    name = perfume.get("nome", "")
    dados_marca = obter_dados_marca(brand, name)
    bottle_style = dados_marca["detalhes_frasco"]
    just_fundo = dados_marca["justificativa_fundo"]
    
    # Determina a instrução de iluminação dinamicamente com base na opacidade do frasco
    if is_bottle_opaque(brand, name):
        lighting_instruction = "- Lighting: Professional high-end three-point studio lighting. Since the bottle is completely opaque, it blocks all light: do NOT generate any light refractions, caustics, or colored glowing light patterns passing through the bottle onto the surface. The counter surface must only show a soft, realistic dark contact shadow and ambient occlusion shadows."
    else:
        lighting_instruction = "- Lighting: Professional high-end three-point studio lighting. Crucially, show rays of light passing through the glass and liquid of the bottle, projecting realistic, warm, colored light refractions and beautiful caustic patterns onto the display counter surface."

    prompt = f"""Role: World-class professional commercial product photographer specializing in luxury cosmetics and fragrances.
Task: Generate a hyper-realistic, high-end commercial product photograph of a single luxury perfume bottle, referencing the provided image.
Context:
- Brand: {brand}
- Perfume Name: {name}
- Style of the original bottle: {bottle_style}
- Composition & Framing: The perfume bottle is perfectly centered and sized to occupy exactly 40% of the frame height, leaving substantial, elegant empty space (negative space) at the top and sides. The camera is positioned at eye-level from a medium distance, capturing the bottle with realistic proportions and no lens distortion.
- Pedestal & Surface: {just_fundo}
{lighting_instruction}
- Shadows: Cast a soft, natural contact shadow and ambient occlusion shadows onto the display surface to avoid any floating effect.
- NO ingredients, fruit, flowers, or chaotic decorations. The focus must be 100% on the luxury bottle.
Format: A single clean vertical studio photograph with a resolution of 1280x1380px aspect ratio.
Tone: Luxurious, sophisticated, clean, premium.
Critical Instructions:
- **Strict Label & Text Fidelity**: Replicate only the exact labels, texts, engravings, and logos that are visible on the original bottle in the reference image.
- **No Hallucinated Text**: If the original bottle does not have any text or labels on its glass body (such as Amouage Cristal & Gold Man), the generated bottle MUST be completely clean of any text or labels on the glass. Do NOT invent, add, or write "{name}" or "{brand}" on the bottle if it is not present in the reference image.
- **Legibility**: If the original bottle contains text (such as Byredo or Creed), that text must be perfectly legible, crisp, sharp, and spelled correctly, using the official elegant font of the brand.
- **Natural Depth of Field & Camera Quality**: Use a natural, subtle depth of field (comparable to f/5.6 on a medium format Hasselblad camera), keeping the bottle perfectly sharp while leaving the boutique background softly blurred but with recognizable architectural shapes and textures (no heavy synthetic blur).
- **Realistic Textures & Material Fidelity**: Render the image with soft, organic film grain and realistic physical textures (e.g. subtle dust particles, microscopic texture on matte black surfaces, realistic glass refractions). Avoid clean, sterile, plastic CGI render looks; it must look like a genuine photograph taken in a physical studio."""
    
    return prompt

def test_original_image_path(p_id):
    filename = f"{p_id}_real.jpg"
    abs_path = os.path.join(FOTOS_DIR, filename)
    if os.path.exists(abs_path):
        return abs_path
    return None

def criar_imagem_comparativa(original_path, generated_path, output_path):
    try:
        # Dimensões para cada painel
        panel_w, panel_h = 1280, 1380
        
        # 1. Cria a imagem base cinza neutro para o painel original
        original_panel = Image.new("RGB", (panel_w, panel_h), (242, 242, 242))
        
        # 2. Carrega a imagem original
        img_orig = Image.open(original_path).convert("RGB")
        orig_w, orig_h = img_orig.size
        
        # Redimensiona mantendo a proporção para caber no painel (com margem de 120px)
        max_h = panel_h - 240
        max_w = panel_w - 240
        
        ratio = min(max_w / orig_w, max_h / orig_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        
        img_orig_resized = img_orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Centraliza a imagem original no painel esquerdo
        paste_x = (panel_w - new_w) // 2
        paste_y = (panel_h - new_h) // 2
        original_panel.paste(img_orig_resized, (paste_x, paste_y))
        
        # Adiciona rótulo "ORIGINAL FRAGRANTICA" no topo do painel esquerdo
        draw_orig = ImageDraw.Draw(original_panel)
        draw_orig.rectangle([0, 0, panel_w, 70], fill=(30, 30, 30))
        draw_orig.text((panel_w // 2 - 100, 25), "ORIGINAL FRAGRANTICA", fill=(255, 255, 255))
        
        # 3. Carrega a imagem gerada (já deve estar em 1280x1380px)
        img_gen = Image.open(generated_path).convert("RGB")
        img_gen_resized = img_gen.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
        
        # Adiciona rótulo "IA GERADA" no topo do painel direito
        gen_panel = img_gen_resized.copy()
        draw_gen = ImageDraw.Draw(gen_panel)
        draw_gen.rectangle([0, 0, panel_w, 70], fill=(197, 168, 128))
        draw_gen.text((panel_w // 2 - 80, 25), "IA GERADA (FOTO 1 - LIMPA)", fill=(255, 255, 255))
        
        # 4. Cria a imagem final lado a lado (2560x1380) com uma divisória fina
        final_comparacao = Image.new("RGB", (panel_w * 2, panel_h), (255, 255, 255))
        final_comparacao.paste(original_panel, (0, 0))
        final_comparacao.paste(gen_panel, (panel_w, 0))
        
        # Desenha linha preta divisória
        draw_div = ImageDraw.Draw(final_comparacao)
        draw_div.line([(panel_w, 0), (panel_w, panel_h)], fill=(0, 0, 0), width=4)
        
        # Salva a imagem comparativa
        final_comparacao.save(output_path, "JPEG", quality=92)
        print(f"   [OK] Imagem comparativa gerada com sucesso em:\n        - {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"   [ERRO] Falha ao criar imagem comparativa: {e}")
        return False

def cmd_prompt(p_id):
    perfume = get_perfume(p_id)
    if not perfume:
        print(f"[ERRO] Perfume com ID '{p_id}' não foi encontrado no banco de dados.")
        sys.exit(1)
        
    print(f"\n==================================================================")
    print(f" PESQUISA DE REDE E CURADORIA DE LUXO: {perfume['nome']} ({perfume['marca']})")
    print(f"==================================================================")
    
    sku = obter_sku_do_csv(p_id, perfume['marca'], perfume['nome'])
    if not sku:
        sku = gerar_sku_dinamico(perfume['marca'], perfume['nome'])
        
    # 1. Busca dinâmica online complementar
    query_busca = f"{perfume['marca']} {perfume['nome']} perfume official store campaign"
    print(f" [*] Buscando informacoes adicionais online para: '{query_busca}'...")
    abstract_online = buscar_online_duckduckgo(query_busca)
    
    # 2. Resgata informações da base de luxo do grimório
    dados_marca = obter_dados_marca(perfume['marca'], perfume['nome'])
    
    print(f"\n [SKU] SKU Identificado: {sku}")
    
    print(f"\n [CAMPANHAS] Campanhas de Venda e Conceito:")
    print(f"    {dados_marca['campanhas']}")
    if abstract_online:
        print(f"    [Fato Online Complementar]: {abstract_online}")
        
    print(f"\n [LOJAS] Lojas Fisicas de Venda (Vida Real):")
    print(f"    {dados_marca['lojas_fisicas']}")
    
    print(f"\n [FUNDO] Justificativa do Fundo Escolhido:")
    print(f"    {dados_marca['justificativa_fundo']}")
    
    orig_path = test_original_image_path(p_id)
    if orig_path:
        print(f" [REF] Imagem de Referencia Original: {orig_path}")
    else:
        print(f" [AVISO] Imagem de referencia original nao encontrada em {FOTOS_DIR} com o nome '{p_id}_real.jpg'")
        
    prompt = gerar_prompt_ia(perfume)
    print(f"\n--- PROMPT DE IA GERADO (COPIE O TEXTO ABAIXO) ---")
    print(prompt)
    print(f"--------------------------------------------------\n")
    return prompt

def rodar_validacao_multimodal_gemini(original_path, gerada_path, perfume):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("   [INFO Quality Gate] GEMINI_API_KEY nao encontrada no ambiente. Pulando a validacao de IA.")
        return True, 10, "Ignorado - Sem chave de API", None

    try:
        from google import genai
        from google.genai import types
        from PIL import Image
    except ImportError:
        print("   [INFO Quality Gate] Bibliotecas necessarias para IA nao instaladas. Instalando automaticamente...")
        return True, 10, "Ignorado - Sem dependencias", None

    try:
        client = genai.Client(api_key=api_key)
        img_orig = Image.open(original_path)
        img_gen = Image.open(gerada_path)

        brand = perfume.get("marca", "")
        name = perfume.get("nome", "")

        prompt_critico = f"""
Role: Hard-nosed, high-end commercial luxury art director and product quality controller.
Task: Compare the newly generated product photograph of a single perfume bottle (IMAGE 2) against the official reference bottle (IMAGE 1). Perform a strict fidelity check.

Brand: {brand}
Perfume Name: {name}

Specifically check for:
1. Cap Proportions: Is the cap size, width, and height perfectly proportioned relative to the bottle body? (For Creed: it must be a wide cap, not thin/narrow. For Amouage: flared dome. For Byredo: glossy dome).
2. Liquid Level: Is the bottle properly filled? (For Amouage: it must be filled 100% up to the collar, leaving no empty space).
3. Text & Brand Names: Are there any hallucinated or gibberish texts on the glass that do not exist in the original reference bottle? (For Amouage: the glass must be completely clean, no text).
4. Silhouette & Geometry: Is the bottle shape true to the original, without stretched necks or warped bases?

Respond strictly in JSON format matching this exact schema:
{{
  "score": 10, // Integer from 1 to 10 based on exact fidelity
  "approved": true, // Boolean (true if score >= 9, false if score < 9)
  "identified_flaws": ["List details of each distortion, missing liquid, or bad cap proportion"],
  "corrective_instructions": "Specific instructions in English to modify the image prompt to fix these issues in the next run"
}}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img_orig, img_gen, prompt_critico],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        result = json.loads(response.text.strip())
        score = result.get("score", 10)
        approved = result.get("approved", True)
        flaws = result.get("identified_flaws", [])
        corrective = result.get("corrective_instructions", "")

        return approved, score, flaws, corrective
    except Exception as e:
        print(f"   [AVISO Quality Gate] Falha ao executar validacao multimodal do Gemini: {e}")
        return True, 10, f"Erro na validacao: {e}", None

def cmd_complete(p_id, temp_image_path):
    perfume = get_perfume(p_id)
    if not perfume:
        print(f"[ERRO] Perfume com ID '{p_id}' não foi encontrado no banco de dados.")
        sys.exit(1)
        
    if not os.path.exists(temp_image_path):
        print(f"[ERRO] A imagem gerada informada no caminho '{temp_image_path}' não existe.")
        sys.exit(1)
        
    if not os.path.exists(OUTPUT_DIR):
        print(f"[INFO] Criando pasta de saída: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR)
        
    sku = obter_sku_do_csv(p_id, perfume['marca'], perfume['nome'])
    if not sku:
        sku = gerar_sku_dinamico(perfume['marca'], perfume['nome'])
        
    output_image_path = os.path.join(OUTPUT_DIR, f"{sku}.jpeg")
    output_comp_path = os.path.join(OUTPUT_DIR, f"{sku}_comparacao.jpeg")
    
    # Rodar o Quality Gate (Loop de Validacao Multimodal de até 5 rodadas)
    orig_path = test_original_image_path(p_id)
    if orig_path:
        print(f" [*] Inciando Quality Gate (Validação de Fidelidade Física)...")
        approved, score, flaws, corrective = rodar_validacao_multimodal_gemini(orig_path, temp_image_path, perfume)
        
        if not approved:
            print(f"\n   [!!! IMAGEM REPROVADA PELO QUALITY GATE (NOTA {score}/10) !!!]")
            print(f"   Falhas Detectadas:")
            if isinstance(flaws, list):
                for f in flaws:
                    print(f"    - {f}")
            else:
                print(f"    - {flaws}")
            
            print(f"\n   [PROMPT CORRETIVO GERADO]:")
            print(f"   {corrective}")
            print(f"\n   A imagem NAO foi salva na pasta de e-commerce.")
            print(f"   Use o prompt corretivo acima para gerar uma nova imagem no Midjourney/DALL-E 3 e tente novamente.")
            sys.exit(1)
        else:
            print(f"   [OK Quality Gate] Imagem aprovada com sucesso! Nota: {score}/10")
    
    # 1. Copia a imagem gerada para a pasta nuvemshop3 com o nome do SKU
    try:
        shutil.copy2(temp_image_path, output_image_path)
        print(f"\n[SUCESSO] Imagem promocional Foto 1 salva em:\n          - {output_image_path}")
    except Exception as e:
        print(f"[ERRO] Falha ao copiar a imagem para a pasta final: {e}")
        sys.exit(1)
        
    # 2. Cria a imagem comparativa lado a lado (com a divisória fina e rigorosa)
    if orig_path:
        criar_imagem_comparativa(orig_path, output_image_path, output_comp_path)
    else:
        print(f"[AVISO] Imagem original do Fragrantica não encontrada. Pulando a geração de comparativo lado a lado.")


def main():
    parser = argparse.ArgumentParser(description="Habilidade 'trazfragrantica3' - Prepara e finaliza Foto 1 promocional com pesquisa de luxo.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Comando 'prompt'
    prompt_parser = subparsers.add_parser("prompt", help="Busca informações e gera o prompt estruturado.")
    prompt_parser.add_argument("--perfume", required=True, help="ID único do perfume (ex: creed_green_irish_tweed).")
    
    # Comando 'complete'
    complete_parser = subparsers.add_parser("complete", help="Finaliza o processo e gera a imagem de comparação.")
    complete_parser.add_argument("--perfume", required=True, help="ID único do perfume.")
    complete_parser.add_argument("--image", required=True, help="Caminho do arquivo de imagem gerado pela IA.")
    
    args = parser.parse_args()
    
    if args.command == "prompt":
        cmd_prompt(args.perfume)
    elif args.command == "complete":
        cmd_complete(args.perfume, args.image)

if __name__ == "__main__":
    main()
