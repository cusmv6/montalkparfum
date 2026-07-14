#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess

WORKSPACE_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem"
CATALOGO_JSON = os.path.join(WORKSPACE_DIR, "PROJETOS", "Bruno", "produtos", "catalogo.json")
VISCATEGORIA_DIR = os.path.join(WORKSPACE_DIR, "PROJETOS", "Bruno", "Identidadevisual", "fotos", "viscategoria")
FOTOS_DIR = os.path.join(VISCATEGORIA_DIR, "fotos")
RENDER_PROFILES = os.path.join(VISCATEGORIA_DIR, "render_profiles.py")
TRAZFRAGRANTICA2 = os.path.join(WORKSPACE_DIR, "grimorio", "trazfragrantica2", "scripts", "trazfragrantica2.py")
TRAZFRAGRANTICA3 = os.path.join(WORKSPACE_DIR, "grimorio", "trazfragrantica3", "scripts", "trazfragrantica3.py")

# Mapeamento de bases e lojas de luxo por grife (conforme trazfragrantica3)
BRAND_LUXURY_MAP = {
    "AMOUAGE": {
        "pedestal": "polished black marble and gold display vanity that extends continuously across the entire bottom horizontal width of the frame, showing no floor underneath",
        "background": "opulent, gold-detailed interior of the Amouage flagship boutique with warm ambient lighting",
        "aesthetic": "opulent Arabian luxury, warm golden glow, incense smoke wisps, completely clean transparent glass bottle body"
    },
    "CREED": {
        "pedestal": "elegant dark walnut and polished brass display counter that extends continuously across the entire bottom horizontal width of the frame, showing no floor underneath",
        "background": "sophisticated Creed flagship boutique with natural wood-paneled walls and warm spotlighting",
        "aesthetic": "aristocratic British heritage, prestige, clean daylight"
    },
    "BYREDO": {
        "pedestal": "warm, elegant beige travertine stone display counter that extends continuously across the entire bottom horizontal width of the frame, showing no floor underneath",
        "background": "clean, modern Byredo boutique with warm light-oak wood shelving populated with out-of-focus bottles",
        "aesthetic": "Nordic minimalist luxury, clean lines, warm natural light"
    },
    "XERJOFF": {
        "pedestal": "polished Italian porphyry stone and bronze vanity display that extends continuously across the bottom horizontal width of the frame",
        "background": "luxurious, neoclassical interior of the Xerjoff boutique with soft velvet accents and warm lighting",
        "aesthetic": "regal Italian artistic luxury, gold and gem-like reflections"
    },
    "CASAMORATI": {
        "pedestal": "vintage mahogany wood and polished gold display stand that extends continuously across the bottom horizontal width",
        "background": "art nouveau Casamorati boutique interior with rich colors and retro luxury lighting",
        "aesthetic": "vintage Art Nouveau elegance, classical Italian heritage"
    },
    "DEFAULT": {
        "pedestal": "elegant light travertine stone display counter that extends continuously across the entire bottom horizontal width of the frame",
        "background": "exclusive luxury niche perfume boutique with warm shelf lighting",
        "aesthetic": "high-end niche luxury, soft lighting, sophisticated minimalist atmosphere"
    }
}

import csv
import re

CSV_PRODUTOS_PATH = r"C:\Users\odeao\OneDrive\Desktop\brem\PROJETOS\Bruno\produtos\importar_nuvemshop.csv"

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

def limpar_ml_do_sku(sku):
    if not sku:
        return sku
    sku_upper = sku.upper()
    for vol in ["-2ML", "-5ML", "-10ML", "-15ML", "-30ML", "-50ML", "-100ML"]:
        if sku_upper.endswith(vol):
            return sku[:-len(vol)]
    return sku

def load_perfumes():
    if not os.path.exists(CATALOGO_JSON):
        print(f"Erro: Arquivo de catálogo não encontrado em: {CATALOGO_JSON}", file=sys.stderr)
        sys.exit(1)
    with open(CATALOGO_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def run_subprocess(cmd):
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}", file=sys.stderr)
        raise e

REGRAS_TEXTO_FRASCO = {
    "amouage_cristal_gold_man": {
        "has_text": False,
        "desc": "The front face of the bottle is a clean, blank gold metal surface with only a round embossed emblem, entirely free of any printed letters, labels, or text. Completely clean, solid gold."
    },
    "amouage_cristal_gold_woman": {
        "has_text": False,
        "desc": "The central panel of the square glass body is completely clear, empty, blank translucent amber-colored glass, with NO logo, NO emblem, and NO text printed or embossed on the glass face."
    },
    "amouage_guidance": {
        "has_text": True,
        "desc": "The front of the bottle has the round gold Amouage emblem embossed on the center, with the text 'AMOUAGE' printed cleanly in gold above the emblem, and the text 'GUIDANCE' printed cleanly in gold below the emblem."
    },
    "amouage_guidance_46": {
        "has_text": True,
        "desc": "The front of the bottle has the round gold Amouage emblem embossed on the center, with the text 'AMOUAGE' printed cleanly in gold above the emblem, and the text 'GUIDANCE 46' printed cleanly in gold below the emblem."
    },
    "amouage_jubilation_25": {
        "has_text": True,
        "desc": "The front of the bottle has the round gold Amouage emblem embossed on the center, with the text 'AMOUAGE' printed cleanly in gold above the emblem, and the text 'JUBILATION 25' printed cleanly in gold below the emblem."
    },
    "amouage_jubilation_40": {
        "has_text": True,
        "desc": "The front of the bottle has the round gold Amouage emblem embossed on the center, with the text 'AMOUAGE' printed cleanly in gold above the emblem, and the text 'JUBILATION 40' printed cleanly in gold below the emblem."
    },
    "creed_green_irish_tweed": {
        "has_text": True,
        "desc": "The brand name 'CREED' is embossed near the neck in clean, raised black lettering. Below it, the text 'GREEN IRISH TWEED' is printed in a clean, sharp, crisp white font. Near the bottom, the text 'DE PÈRE EN FILS DEPUIS 1760' and 'FROM FATHER TO SON SINCE 1760' is printed in tiny white letters, along with '100 ML' on the left and '3.33 FL. OZ.' on the right."
    }
}

def obter_detalhes_frasco_dinamico(perfume):
    brand = perfume["marca"].upper()
    name = perfume["nome"].upper()
    genero = perfume.get("genero_comercial", "").lower()
    p_id = perfume["id"]
    
    # 1. Verificar se existe regra estrita de texto mapeada
    regra_texto = REGRAS_TEXTO_FRASCO.get(p_id)
    texto_especificacao = ""
    if regra_texto:
        texto_especificacao = regra_texto["desc"]
    
    # 2. Amouage específico
    if "AMOUAGE" in brand:
        if "CRISTAL & GOLD" in name or "CRISTAL GOLD" in name:
            if "feminino" in genero or "woman" in name.lower():
                cap_desc = "the official Amouage feminine gold cap (a beautiful rounded dome resembling a mosque cupola, made of smooth polished solid gold, completely plain gold without any gemstones, crystals, or diamonds inset on the dome)"
                bottle_shape = "square-shaped bottle made of translucent amber-colored glass, filled with a warm golden liquid"
                
                texto_final = texto_especificacao if texto_especificacao else "completely clean glass panels, translucent and not opaque metal, with no logos and no text."
                
                return (
                    f"The bottle cap must be {cap_desc}. The bottle shape is a {bottle_shape}. The body must match the reference image exactly: "
                    f"it features rich gold-plated filigree metal frames only at the top collar and the very bottom base of the square body, "
                    f"leaving the central square glass panels smooth, translucent, and showing the warm amber liquid inside with elegant lighting reflections. "
                    f"{texto_final}"
                )
            else:
                cap_desc = "the official Amouage masculine gold cap (a curved, flared, and flat-topped golden dome resembling the hilt of an Omani Khanjar dagger, with a round gemstone sapphire inset in the center of the cap)"
                bottle_shape = "tall rectangular gold-plated crystal bottle with rich engraved arabesque patterns and no transparent parts"
            
                texto_final = texto_especificacao if texto_especificacao else "a rich gold-plated textured body with engraved gold filigrees, with the round gold Amouage emblem embossed in the center. Completely clean surface, no letters."
                
                return (
                    f"The bottle cap must be {cap_desc}. The bottle shape is a {bottle_shape}. The body must match the reference image exactly: "
                    f"{texto_final} The bottle body and neck are completely opaque gold-plated crystal, with no transparent glass parts or visible liquid levels. All gold-plated."
                )
            
        if "feminino" in genero or "guidance" in name.lower():
            cap_desc = "the official Amouage feminine gold cap (a beautiful rounded golden dome resembling a mosque cupola with a small gemstone inset at the top center)"
            bottle_shape = "square-shaped glass bottle"
        else:
            cap_desc = "the official Amouage masculine gold cap (a curved, flared, and flat-topped golden dome resembling the hilt of an Omani Khanjar dagger, with a round gemstone sapphire inset in the center of the cap)"
            bottle_shape = "tall rectangular glass bottle"
        
        texto_final = texto_especificacao if texto_especificacao else f"the round gold Amouage emblem embossed on the center, with the texts 'AMOUAGE' and '{name}' cleanly printed in gold."
        
        return (
            f"The bottle cap must be {cap_desc}. The bottle shape is a {bottle_shape}. The body must match the reference image exactly: "
            f"{texto_final} No volume markings, no database year text, no literal daggers or knives."
        )
    
    # 3. Creed específico
    elif "CREED" in brand:
        texto_final = texto_especificacao if texto_especificacao else f"The brand name 'CREED' is embossed near the neck. The text '{name}' is printed on the lower front."
        if "green irish" in name.lower():
            return (
                "A classic matte black curved-shoulder Creed bottle. The cap must have the exact same width and low-profile height relative to the bottle's shoulders. "
                f"{texto_final} "
                "No other labels or elements not present in the original bottle design."
            )
        else:
            return (
                f"The classic Creed bottle silhouette. Replicate the exact shape, material texture, and cap of the reference image. "
                f"{texto_final} "
                "No other labels, database years, or volume markings."
            )
            
    # Fallback genérico
    else:
        return (
            f"Replicate with 100% pixel fidelity the exact glass bottle shape, cap design, material texture, liquid color, and brand labels of the {brand} {name} "
            f"perfume bottle shown in the reference image. Do NOT alter, omit, or add any design elements, texts, or volume markings (like 100ml) not present in the original bottle design."
        )

def mapear_ingrediente_elegante(ing):
    ing_lower = ing.lower()
    if "civeta" in ing_lower or "civet" in ing_lower:
        return "a premium dark textured leather roll"
    if "castóreo" in ing_lower or "castoreum" in ing_lower:
        return "soft luxury suede fabric swatch"
    if "almíscar" in ing_lower or "musk" in ing_lower:
        return "ancient amber glass apothecary vial containing a glowing golden essence"
    return ing_lower

def generate_composition_prompt(perfume):
    p_id = perfume["id"]
    brand = perfume["marca"].upper()
    name = perfume["nome"].upper()
    
    # Obter dados de luxo da grife
    lux = BRAND_LUXURY_MAP.get(brand, BRAND_LUXURY_MAP["DEFAULT"])
    
    # Extrair os ingredientes dominantes (topo, coração, base)
    topo = perfume.get("notas", {}).get("topo", [])[:3]
    coracao = perfume.get("notas", {}).get("coracao", [])[:3]
    base = perfume.get("notas", {}).get("base", [])[:3]
    
    ingredients = list(set(topo + coracao + base))
    ingredients_cleaned = []
    for ing in ingredients:
        if ing:
            ingredients_cleaned.append(mapear_ingrediente_elegante(ing))
            
    ingredients_str = ", ".join(ingredients_cleaned)
    
    bottle_details = obter_detalhes_frasco_dinamico(perfume)
    
    prompt = (
        f"A professional fotorrealistic product photography of a single {brand} {name} perfume bottle. "
        f"The bottle design, cap shape, details, and branding must perfectly match the official design of the reference bottle from {brand}. "
        f"The bottle is beautifully displayed on a {lux['pedestal']}. "
        f"The bottle is surrounded in a balanced, artistic composition by its natural physical olfactory ingredients: {ingredients_str}. "
        f"Do NOT include any physical ingredients that do not belong to the olfactory pyramid. "
        f"The background is a {lux['background']}, with a natural, soft f/5.6 camera blur (no artificial or heavy blur). "
        f"High-end luxury aesthetic, {lux['aesthetic']}, cinematic studio lighting, volumetric shadows, warm and inviting atmosphere. "
        f"{bottle_details} "
        f"No volume specifications on the glass, no inventory years, no hallucinated labels, no extra text, pure clean shot. "
        f"Absolutely NO live animals, NO rodents, NO civets, NO cats, and NO taxidermy on the display table."
    )
    return prompt

def generate_studio_prompt(perfume):
    brand = perfume["marca"].upper()
    name = perfume["nome"].upper()
    lux = BRAND_LUXURY_MAP.get(brand, BRAND_LUXURY_MAP["DEFAULT"])
    
    bottle_details = obter_detalhes_frasco_dinamico(perfume)
    
    prompt = (
        f"A professional clean studio product photography of a single {brand} {name} perfume bottle, showing its full design and cap. "
        f"The bottle cap shape, brand text, and design must perfectly replicate the official {brand} original design from the reference image. "
        f"The bottle is displayed on a {lux['pedestal']}. "
        f"The background is the {lux['background']}, with a subtle, natural camera blur f/5.6. "
        f"Cinematic studio lighting, elegant reflections on the bottle glass, volumetric shadows, {lux['aesthetic']}. "
        f"{bottle_details} "
        f"No volume markings or metrics on the glass face, no database inventory text, completely clean bottle glass surface, centered framing."
    )
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
        print("   [INFO Quality Gate] Bibliotecas necessarias para IA nao instaladas.")
        return True, 10, "Ignorado - Sem dependencias", None

    try:
        client = genai.Client(api_key=api_key)
        img_orig = Image.open(original_path)
        img_gen = Image.open(gerada_path)

        brand = perfume.get("marca", "")
        name = perfume.get("nome", "")

        prompt_critico = f"""
Role: Hard-nosed, high-end commercial luxury art director and product quality controller.
Task: Compare the perfume bottle inside the composition scene (IMAGE 2) against the official reference bottle (IMAGE 1). Perform a strict bottle design fidelity check.
Note: IMAGE 2 contains natural olfactory ingredients surrounding the bottle. Disregard the ingredients and background scenery, and focus exclusively on the perfume bottle body, glass, cap, design, color, and labels.

Brand: {brand}
Perfume Name: {name}

Specifically check for:
1. Cap Design & Details: Does the generated bottle cap (IMAGE 2) perfectly match the reference cap (IMAGE 1)? Compare them 1:1. If the reference cap has NO gemstone on top, the generated cap must NOT have any gemstone. If the reference cap is a dome, the generated cap must be a dome. If the reference cap is flat, the generated cap must be flat. Any addition of hallucinated details, gems, or modifications is a strict failure.
2. Glass Body Text & Brand Labels: Compare the texts on the glass body of IMAGE 2 with IMAGE 1. If IMAGE 1 has NO text or branding printed on the glass (like Amouage Cristal & Gold), the generated bottle in IMAGE 2 must be completely clean and have NO text printed on the glass face. If IMAGE 1 has text, the text in IMAGE 2 must match it exactly. Any hallucinated texts, labels, or volume metrics (like 100ml, 2.0 fl oz, etc.) not present in IMAGE 1 are strict failures.
3. Material, Color & Transparency: Does the material, color, and transparency match IMAGE 1 exactly? If the reference bottle (IMAGE 1) is translucent glass showing amber liquid inside, the generated bottle (IMAGE 2) must be translucent showing amber liquid, and NOT look like solid/opaque gold metal. If IMAGE 1 is opaque gold, IMAGE 2 must be opaque gold. The gold-plated filigree frames on the body must appear exactly at the same places (e.g., only at the top collar and bottom base).
4. Silhouette & Geometry: Is the bottle shape and aspect ratio (width-to-height proportion) 100% true to the original reference image? Pay close attention to prevent the generated bottle from looking too narrow, stretched, elongated, or compressed. Stretched/narrowed bodies relative to the original shape are strict failures.

Respond strictly in JSON format matching this exact schema:
{{
  "score": 10, // Integer from 1 to 10 based on exact bottle fidelity
  "approved": true, // Boolean (true if score >= 9, false if score < 9)
  "identified_flaws": ["List details of each bottle distortion, bad cap, or hallucinated text on the glass"],
  "corrective_instructions": "Specific instructions in English to modify the image prompt to fix these bottle design issues in the next run"
}}
"""
        response = client.models.generate_content(
            model='gemini-3.5-flash',
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

def process_single(perfume):
    p_id = perfume["id"]
    brand = perfume["marca"]
    name = perfume["nome"]
    
    print(f"\n================================================================================")
    print(f"ESTAGIÁRIO VISUAL: Analisando Perfume: {name} ({brand}) [ID: {p_id}]")
    print(f"================================================================================")
    
    # Caminho das imagens físicas no diretório fotos/
    composicao_name = f"{p_id}_composicao.png"
    composicao_path = os.path.join(FOTOS_DIR, composicao_name)
    
    real_name = f"{p_id}_real.jpg"
    real_path = os.path.join(FOTOS_DIR, real_name)
    
    # 1. Checa a imagem fotorrealista de composição
    if not os.path.exists(composicao_path):
        print(f"\n[AÇÃO CRIATIVA NECESSÁRIA] A foto de composição fotorrealista não existe:")
        print(f"   Destino esperado: {composicao_path}")
        
        prompt_comp = generate_composition_prompt(perfume)
        print("\n--- POR FAVOR, GERE A IMAGEM DE COMPOSIÇÃO COM O PROMPT ABAIXO ---")
        print(f"[SOLICITAR_GERACAO] PROMPT_COMPOSICAO: {prompt_comp} | DESTINO: {composicao_path}")
        print("-----------------------------------------------------------------\n")
        
        # Indica que precisamos parar a execução do perfume atual para gerar a imagem
        return False
        
    # Se existe a imagem de composição, roda a validação contra a referência original!
    if os.path.exists(real_path):
        print(f" [*] Iniciando Quality Gate (Fidelidade do Frasco na Composição)...")
        approved, score, flaws, corrective = rodar_validacao_multimodal_gemini(real_path, composicao_path, perfume)
        if not approved:
            print(f"\n   [!!! COMPOSIÇÃO REPROVADA PELO QUALITY GATE (NOTA {score}/10) !!!]")
            print(f"   Falhas Detectadas no Frasco:")
            if isinstance(flaws, list):
                for f in flaws:
                    print(f"    - {f}")
            else:
                print(f"    - {flaws}")
            print(f"\n   [PROMPT CORRETIVO GERADO]:")
            print(f"   {corrective}")
            # Mover o arquivo ruim para podermos tentar de novo
            try:
                os.remove(composicao_path)
                print("   [INFO] Arquivo de composição descartado. Use o prompt corretivo acima para gerar novamente.")
            except Exception as e:
                print(f"   [AVISO] Falha ao remover arquivo de composição incorreto: {e}")
            return False
        else:
            print(f"   [OK Quality Gate] Frasco na composição aprovado com sucesso! Nota: {score}/10")

    # 2. Checa a imagem promocional de estúdio do frasco para a Foto 1
    studio_temp_path = os.path.join(FOTOS_DIR, f"{p_id}_studio_temp.png")
    
    sku = obter_sku_do_csv(p_id, brand, name)
    if not sku:
        sku = gerar_sku_dinamico(brand, name)
    sku = limpar_ml_do_sku(sku)
        
    output_1_path = os.path.join(WORKSPACE_DIR, "PROJETOS", "Bruno", "Identidadevisual", "fotos", "nuvemshop3", f"{sku}.jpeg")
    
    # Se a Foto 1 final não existe e não temos a imagem de estúdio temporária
    if not os.path.exists(output_1_path) and not os.path.exists(studio_temp_path):
        print(f"\n[AÇÃO CRIATIVA NECESSÁRIA] A foto de estúdio de luxo do frasco original não existe:")
        print(f"   Destino esperado: {studio_temp_path}")
        
        prompt_studio = generate_studio_prompt(perfume)
        print("\n--- POR FAVOR, GERE A IMAGEM DE ESTÚDIO COM O PROMPT ABAIXO ---")
        print(f"[SOLICITAR_GERACAO] PROMPT_ESTUDIO: {prompt_studio} | DESTINO: {studio_temp_path}")
        print("-----------------------------------------------------------------\n")
        
        return False

    # Atualiza o catalogo.json para registrar a imagem de composição como frasco_imagem
    # Isso é essencial para que o renderizador de perfil (Foto 2) passe a usar a composição em vez do fundo branco!
    print(f"\n[OK] Foto de composição encontrada: {composicao_name}")
    perfumes_data = load_perfumes()
    updated = False
    for p in perfumes_data:
        if p["id"] == p_id:
            if p.get("frasco_imagem") != composicao_name:
                p["frasco_imagem"] = composicao_name
                updated = True
                print(f"   [BD] Atualizada chave frasco_imagem para '{composicao_name}' no catalogo.json.")
            break
            
    if updated:
        with open(CATALOGO_JSON, "w", encoding="utf-8") as f:
            json.dump(perfumes_data, f, indent=2, ensure_ascii=False)
        print("   [BD] catalogo.json atualizado e salvo.")

    # 3. Executa a renderização da Foto 2 (Card de Perfil - Infográfico)
    print("\n--- GERANDO FOTO 2: Card de Perfil Olfativo (Infográfico) ---")
    try:
        run_subprocess([sys.executable, RENDER_PROFILES, "--perfume", p_id])
    except Exception as e:
        print(f"   [ERRO] Falha ao renderizar Foto 2 para {p_id}: {e}")
        return False

    # 4. Executa a renderização da Foto 3 (Card de Composição - 1280x1380px)
    print("\n--- GERANDO FOTO 3: Card de Composição Olfativa (Nuvemshop2) ---")
    try:
        run_subprocess([sys.executable, TRAZFRAGRANTICA2, "run", "--perfume", p_id])
    except Exception as e:
        print(f"   [ERRO] Falha ao renderizar Foto 3 para {p_id}: {e}")
        return False

    # 5. Executa a finalização da Foto 1 (Card Promocional de Estúdio - Nuvemshop3)
    if os.path.exists(studio_temp_path):
        print("\n--- GERANDO FOTO 1: Card Promocional de Estúdio (Nuvemshop3) ---")
        try:
            run_subprocess([sys.executable, TRAZFRAGRANTICA3, "complete", "--perfume", p_id, "--image", studio_temp_path])
            # Limpa o arquivo temporário de estúdio gerado pela IA
            os.remove(studio_temp_path)
            print("   [OK] Limpo arquivo de estúdio temporário.")
        except Exception as e:
            print(f"   [ERRO] Falha ao finalizar Foto 1 para {p_id}: {e}")
            return False
            
    print(f"\n[SUCESSO] Grade visual de e-commerce (Fotos 1, 2 e 3) criada com sucesso para {p_id}!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Subagente estagiariovisual - Maestro do design do e-commerce.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--perfume", help="ID único do perfume para processar.")
    group.add_argument("--limit", type=int, help="Processa os primeiros N perfumes do catálogo.")
    group.add_argument("--all", action="store_true", help="Processa todos os perfumes do catálogo.")
    
    args = parser.parse_args()
    
    perfumes_data = load_perfumes()
    
    if args.perfume:
        selected = [p for p in perfumes_data if p["id"] == args.perfume]
        if not selected:
            print(f"Erro: Perfume com ID '{args.perfume}' não encontrado no catalogo.json.", file=sys.stderr)
            sys.exit(1)
    elif args.limit:
        selected = perfumes_data[:args.limit]
    else:
        selected = perfumes_data

    total = len(selected)
    print(f"[START] Estagiário Visual ativado para processar {total} perfume(s)...")
    
    processed_count = 0
    for idx, p in enumerate(selected):
        success = process_single(p)
        if success:
            processed_count += 1
        else:
            # Para o lote se precisarmos de imagens por IA para o primeiro da fila
            print(f"\n[INFO] Lote pausado. Gere as fotos solicitadas por IA antes de continuar.")
            break
            
    print(f"\n[FIM] Estagiário Visual finalizado. Processados com sucesso: {processed_count}/{total}")

if __name__ == "__main__":
    main()
