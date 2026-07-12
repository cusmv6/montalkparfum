import os
import sys
import json

# Mapeador semântico de acordes olfativos (chaves normalizadas sem acento) para descrições visuais em inglês
ACCORD_VISUAL_MAP = {
    "ozonico": "dewy green mint and lemon verbena leaves covered in fresh morning dew",
    "verde": "vibrant fresh green leaves, sliced verbena and fresh mint leaves",
    "aquatico": "dynamic, crystal-clear water splashes frozen in mid-air and clean water droplets, evoking a refreshing sea breeze",
    "iris": "a single elegant blue-purple iris flower in full bloom with soft petals",
    "violeta": "delicate dark purple violet flowers scattered elegantly",
    "atalcado": "fine powdery texture highlights and soft, elegant velvet-like reflections",
    "amadeirado": "small natural sandalwood logs and cedarwood bark blocks",
    "sandalo": "polished aromatic sandalwood logs",
    "mel": "glistening honeycombs dripping with warm, gold liquid honey",
    "animalico": "raw leather textures and warm, organic golden resin shapes",
    "almiscarado": "soft, fluffy cotton-like textures in a clean, soft-focus background",
    "ambar": "glowing translucent warm amber resin pieces",
    "balsamico": "glistening aromatic resin tears and a thin wisp of clean incense smoke",
    "couro": "a premium dark rolled leather scroll",
    "floral": "soft rose petals and fresh floral elements in bloom",
    "floral branco": "star-like white jasmine and orange blossom flowers",
    "rosa": "blooming pink roses with delicate dew-covered petals",
    "especiado quente": "cinnamon sticks and whole star anise spices",
    "frutado": "fresh sliced juicy pears and hints of ripe fruit textures",
    "citrico": "slices of fresh yellow bergamot and green limes",
    "doce": "black vanilla pods and crystals of brown sugar",
    "defumado": "a thin, elegant curl of incense smoke rising softly in the air",
    "baunilha": "black gourmet vanilla pods and crystals of raw brown sugar"
}

def normalizar_termo(texto):
    texto = texto.lower()
    # Corrige problemas comuns de encoding/decodificação ANSI/UTF-8 no JSON local
    if "mbar" in texto or "mbar" in texto:
        return "ambar"
    if "alm" in texto or "muscar" in texto or "mscar" in texto:
        return "almiscarado"
    if "sandal" in texto or "snd" in texto:
        return "sandalo"
    if "balsam" in texto or "balsm" in texto:
        return "balsamico"
    if "citric" in texto or "ctr" in texto:
        return "citrico"
    if "defum" in texto or "fum" in texto:
        return "defumado"
    if "baun" in texto or "vanil" in texto:
        return "baunilha"
    if "iris" in texto or "ris" in texto:
        return "iris"
    if "ozon" in texto or "ozn" in texto:
        return "ozonico"
    if "aquat" in texto or "aqut" in texto:
        return "aquatico"
        
    # Limpeza básica de acentos
    substituicoes = {
        "á": "a", "ã": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u", "ç": "c"
    }
    for original, subs in substituicoes.items():
        texto = texto.replace(original, subs)
    return texto

def gerar_prompt_para_perfume(target_id):
    workspace_dir = r"C:\Users\odeao\OneDrive\Desktop\brem"
    json_path = os.path.join(workspace_dir, "Bruno", "Identidadevisual", "fotos", "viscategoria", "perfumes_data.json")
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return None
        
    with open(json_path, "r", encoding="utf-8") as f:
        perfumes = json.load(f)
        
    perfume = None
    for p in perfumes:
        if p.get("id") == target_id:
            perfume = p
            break
            
    if not perfume:
        print(f"Error: Perfume '{target_id}' not found in database.")
        return None
        
    brand = perfume["marca"].upper()
    name = perfume["nome"].upper()
    acordes = perfume.get("principais_acordes", [])
    
    # 1. Constrói a descrição fidedigna da garrafa baseada na grife
    if brand == "CREED":
        bottle_desc = (
            f"A luxury matte black Creed perfume bottle, featuring a matching matte black cap. "
            f"The 3D embossed word 'CREED' with its signature crest is sculpted on the upper body of the bottle. "
            f"At the lower third of the bottle, fine, crisp metallic silver text is perfectly printed, reading: "
            f"'{name}', 'DE PÈRE EN FILS DEPUIS 1760', 'FROM FATHER TO SON SINCE 1760', and '100 ML 3.33 FL. OZ.'."
        )
    elif brand == "AMOUAGE":
        is_man = "man" in target_id or perfume.get("genero_comercial", "").lower() == "masculino"
        if is_man:
            bottle_desc = (
                f"A luxury cylindrical gold glass Amouage perfume bottle with detailed engravings, "
                f"filled with amber-gold juice, topped with a polished gold dagger-handle-shaped cap. "
                f"The name 'AMOUAGE' is printed on a gold plaque at the base of the stone pedestal."
            )
        else:
            bottle_desc = (
                f"A luxury transparent square glass Amouage perfume bottle with gold filigree details, "
                f"filled with golden liquid, topped with a polished gold mosque-dome-shaped cap. "
                f"The name 'AMOUAGE' is printed on a gold plaque at the base of the stone pedestal."
            )
    elif brand == "BYREDO":
        bottle_desc = (
            f"A minimalist cylindrical clear glass Byredo perfume bottle filled with transparent warm golden-amber liquid, "
            f"featuring a clean white rectangular label with bold black sans-serif text reading 'BYREDO' and '{name}', "
            f"topped with a signature glossy black dome-shaped magnetic cap."
        )
    else:
        bottle_desc = (
            f"A luxury designer glass perfume bottle for the brand '{brand}', containing the perfume '{name}', "
            f"resting upright on a stone pedestal with elegant detailing."
        )
        
    # 2. Mapeia e filtra os ingredientes em ordem de importância real
    elementos_validos = []
    for acorde in acordes:
        nome_limpo = normalizar_termo(acorde["nome"])
        visual_desc = ACCORD_VISUAL_MAP.get(nome_limpo, None)
        if visual_desc and visual_desc not in elementos_validos:
            elementos_validos.append(visual_desc)
            
    # 3. Distribui os elementos na hierarquia visual
    primary_elements = elementos_validos[0:2]
    secondary_elements = elementos_validos[2:3]
    base_elements = elementos_validos[3:6]
    
    # Fallbacks elegantes
    if not primary_elements:
        primary_elements.append("fresh green botanicals and delicate white flower petals")
    if not secondary_elements:
        secondary_elements.append("soft light rays reflecting on stone textures")
    if not base_elements:
        base_elements.append("small cedarwood chips scattered on the surface")
        
    # 4. Monta o prompt final descrevendo a cena na hierarquia exata
    prompt = (
        f"A high-end luxury product advertisement photograph. "
        f"{bottle_desc} The bottle stands centered and upright on a rustic cream travertine stone circular pedestal. "
        f"To the left and right of the pedestal in the immediate foreground, there is a prominent composition of: "
        f"{' and '.join(primary_elements)}. Next to it, as a beautiful secondary accent, is "
        f"{' and '.join(secondary_elements)}. Scattered elegantly on the warm wooden table base supporting the pedestal are "
        f"{', '.join(base_elements)}. The background is a soft-focus warm beige textured wall in gentle bokeh. "
        f"Warm studio lighting, natural delicate shadows, clean commercial advertising shot, fotorrealist, 8k resolution."
    )
    
    return prompt

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gerar_prompt_composicao.py <perfume_id>")
        sys.exit(1)
        
    p_id = sys.argv[1]
    prompt_result = gerar_prompt_para_perfume(p_id)
    
    if prompt_result:
        print("\n=== GENERATED PROMPT ===")
        print(prompt_result)
        print("========================\n")
