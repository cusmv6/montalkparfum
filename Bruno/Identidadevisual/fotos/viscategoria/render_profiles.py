import os
import json
import shutil
import subprocess
import sys
import re

def slugify(text):
    text = str(text).lower()
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

def get_sku_2ml(brand, name):
    slug_brand = slugify(brand)
    slug_name = slugify(name)
    sku_clean_brand = slug_brand.upper()[:4]
    # Remove hifens para o nome e trunca em 12 caracteres
    sku_clean_name = slug_name.replace("-", "")[:12].upper()
    
    # Tratamento especial de hifens duplos para marcas curtas no protocolo
    if len(sku_clean_brand) < 4:
        return f"DEC-{sku_clean_brand}--{sku_clean_name}-2ML"
    return f"DEC-{sku_clean_brand}-{sku_clean_name}-2ML"


# Tenta importar playwright, se falhar explica ao usuário
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("[AVISO] A biblioteca 'playwright' não está instalada.")
    print("Por favor, execute no seu terminal:")
    print("  pip install playwright")
    print("  playwright install chromium")
    print("\nTentando instalar automaticamente para você...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright
        print("[SUCESSO] Playwright instalado e configurado!")
    except Exception as e:
        print(f"[ERRO] Não foi possível instalar automaticamente: {e}")
        print("Instale manualmente rodando as instruções acima no terminal.")
        sys.exit(1)

def build_accords_html(accords):
    html = ""
    for accord in accords:
        nome = accord["nome"]
        intensidade = accord["intensidade"]
        cor = accord["cor"]
        texto_cor = accord["texto_cor"]
        html += f'<div class="accord-item" style="width: {intensidade}%; background-color: {cor}; color: {texto_cor};">{nome}</div>\n'
    return html

def build_notes_html(notes, current_dir=None):
    html = '<div class="note-tags-list">\n'
    for note in notes:
        html += f'  <span class="note-tag">{note}</span>\n'
    html += '</div>\n'
    return html

def build_seasons_html(seasons):
    translation = {
        "inverno": {"nome": "Inverno", "icon": "❄️"},
        "primavera": {"nome": "Primavera", "icon": "🌸"},
        "verao": {"nome": "Verão", "icon": "☀️"},
        "outono": {"nome": "Outono", "icon": "🍂"}
    }
    
    total_votos = sum(data.get("votos", 0) for data in seasons.values())
    if total_votos == 0:
        total_votos = 1
        
    html = ""
    for key, data in seasons.items():
        trans = translation.get(key, {"nome": key.capitalize(), "icon": "✨"})
        votos = data.get("votos", 0)
        pct = round((votos / total_votos) * 100)
        cor = data.get("cor", "#C5A880")
        
        style = f'background: linear-gradient(to right, {cor} {pct}%, #FAF9F6 {pct}%); border-color: {cor};'
        
        html += f'<div class="season-btn" style="{style}">\n'
        html += f'  <span class="btn-content"><span class="btn-icon">{trans["icon"]}</span> {trans["nome"]}</span>\n'
        html += f'  <span class="season-pct">{pct}%</span>\n'
        html += f'</div>\n'
    return html

def build_turnos_html(diurno_votos):
    dia_votos = diurno_votos.get("dia", 0)
    noite_votos = diurno_votos.get("noite", 0)
    total_votos = dia_votos + noite_votos
    if total_votos == 0:
        total_votos = 1
        
    dia_pct = round((dia_votos / total_votos) * 100)
    noite_pct = round((noite_votos / total_votos) * 100)
    
    # Dia styling: sky blue background linear gradient (30% to 100%), text always black (#000000)
    bg_opacity_dia = 0.30 + (dia_pct / 100) * 0.70
    border_opacity_dia = 0.40 + (dia_pct / 100) * 0.60
    dia_style = f"background-color: rgba(176, 226, 255, {bg_opacity_dia:.2f}); border-color: rgba(144, 202, 249, {border_opacity_dia:.2f}); color: #000000;"
        
    # Noite styling: starry night blue linear gradient (40% to 85% of rgb(16, 37, 76)), text always white (#FFFFFF)
    bg_opacity_noite = 0.40 + (noite_pct / 100) * 0.45
    border_opacity_noite = 0.45 + (noite_pct / 100) * 0.40
    noite_style = f"background-color: rgba(16, 37, 76, {bg_opacity_noite:.2f}); border-color: rgba(10, 24, 52, {border_opacity_noite:.2f}); color: #FFFFFF; text-shadow: 0 1px 2px rgba(10, 24, 52, 0.2);"
        
    html = f'<div class="time-btn" style="{dia_style}">\n'
    html += f'  <span class="btn-content"><span class="btn-icon">☀️</span> Dia</span>\n'
    html += f'  <span class="time-pct">{dia_pct}%</span>\n'
    html += f'</div>\n'
    
    html += f'<div class="time-btn" style="{noite_style}">\n'
    html += f'  <span class="btn-content"><span class="btn-icon">🌙</span> Noite</span>\n'
    html += f'  <span class="time-pct">{noite_pct}%</span>\n'
    html += f'</div>\n'
    return html

def build_description(perfume):
    perfumistas_list = perfume.get("perfumistas", [])
    perfumistas_bold = [f"<b>{p}</b>" for p in perfumistas_list]
    
    if len(perfumistas_bold) > 1:
        perfumistas_str = ", ".join(perfumistas_bold[:-1]) + " e " + perfumistas_bold[-1]
    elif len(perfumistas_bold) == 1:
        perfumistas_str = perfumistas_bold[0]
    else:
        perfumistas_str = "um perfumista exclusivo"
        
    topo_str = ", ".join(perfume["notas"]["topo"][:-1]) + " e " + perfume["notas"]["topo"][-1] if len(perfume["notas"]["topo"]) > 1 else perfume["notas"]["topo"][0]
    coracao_str = ", ".join(perfume["notas"]["coracao"][:-1]) + " e " + perfume["notas"]["coracao"][-1] if len(perfume["notas"]["coracao"]) > 1 else perfume["notas"]["coracao"][0]
    base_str = ", ".join(perfume["notas"]["base"][:-1]) + " e " + perfume["notas"]["base"][-1] if len(perfume["notas"]["base"]) > 1 else perfume["notas"]["base"][0]
    
    desc = f"<b>{perfume['nome']}</b> de <b>{perfume['marca']}</b> é um perfume {perfume.get('familia_olfativa', 'Exclusivo')} {perfume.get('genero_comercial', 'Compartilhável')}. "
    desc += f"<b>{perfume['nome']}</b> foi lançado em {perfume.get('ano_lancamento', '2020')}. "
    desc += f"<b>{perfume['nome']}</b> foi criado por {perfumistas_str}. "
    desc += f"As notas de topo são {topo_str}. "
    desc += f"As notas de coração são {coracao_str}. "
    desc += f"As notas de fundo são {base_str}."
    return desc

def build_adjectives_html(adjectives):
    icons = ["✨", "🔥", "💨", "⭐", "🌿", "💎"]
    html = ""
    for i, adj in enumerate(adjectives):
        icon = icons[i % len(icons)]
        html += f'<div class="char-item"><span class="char-icon">{icon}</span><span>{adj}</span></div>\n'
    return html

def build_perfumistas_html(perfumistas, current_dir=None):
    if not perfumistas:
        # Golden user avatar SVG data URI placeholder
        svg_placeholder = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23C5A880'><path d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/></svg>"
        return f'''
        <div class="perfumista-container">
            <img class="perfumista-avatar" src="{svg_placeholder}" alt="Perfumista Exclusivo">
            <span class="perfumista-name">Perfumista Exclusivo</span>
        </div>
        '''
    
    html = ""
    for p in perfumistas:
        nome = p["nome"]
        foto = p["foto"]
        
        # Adjust local path to photos folder
        if foto and not foto.startswith("http") and not foto.startswith("fotos/"):
            foto = "fotos/" + foto
            
        html += f'''
        <div class="perfumista-container">
            <img class="perfumista-avatar" src="{foto}" alt="{nome}">
            <span class="perfumista-name">{nome}</span>
        </div>
        '''
    return html

def build_gender_html(gender_data):
    votos = {
        "feminino": gender_data.get("feminino", 0),
        "mais_feminino": gender_data.get("mais_feminino", 0),
        "unissex": gender_data.get("unissex", 0),
        "mais_masculino": gender_data.get("mais_masculino", 0),
        "masculino": gender_data.get("masculino", 0)
    }
    mais_votada = gender_data.get("classe_genero", max(votos, key=votos.get))
    
    labels = {
        "feminino": "Feminino",
        "mais_feminino": "Mais Fem.",
        "unissex": "Unissex",
        "mais_masculino": "Mais Masc.",
        "masculino": "Masculino"
    }
    
    html = '<div class="gender-scale-container">\n'
    html += '  <div class="gender-line"></div>\n'
    for key, label in labels.items():
        active_class = "active" if key == mais_votada else ""
        vote_count = votos[key]
        html += f'  <div class="gender-point {active_class}">\n'
        html += '    <div class="gender-dot"></div>\n'
        html += f'    <span class="gender-label">{label}</span>\n'
        html += f'    <span class="gender-votes">{vote_count}v</span>\n'
        html += '  </div>\n'
    html += '</div>\n'
    return html

def obter_cor_de_relevo(perfume):
    cores_grife = {
        "AMOUAGE": "#B89C72",  # Dourado envelhecido
        "CREED": "#8C8475",     # Cinza elegante
        "ROJA PARFUMS": "#A89068", # Dourado envelhecido
        "BYREDO": "#5E5A54",    # Cinza escuro antracite
        "CHANEL": "#4D4D4D",    # Preto suave clássico
    }
    marca = perfume["marca"].upper()
    if marca in cores_grife:
        return cores_grife[marca]
        
    # Fallback dinâmico: pega a cor do primeiro acorde e atenua
    acordes = perfume.get("principais_acordes", [])
    if acordes:
        return acordes[0].get("cor", "#C5A880")
    return "#C5A880"

def extrair_cor_dominante(p_id, current_dir):
    fotos_dir = os.path.join(current_dir, "fotos")
    imagem_path = os.path.join(fotos_dir, f"{p_id}_real.jpg")
    
    if not os.path.exists(imagem_path):
        imagem_path = os.path.join(fotos_dir, f"{p_id}_real.png")
        
    if not os.path.exists(imagem_path):
        return "#B89C72"
        
    try:
        from PIL import Image
        img = Image.open(imagem_path)
        img = img.resize((50, 50))
        img = img.convert("RGBA")
        
        pixels = img.getdata()
        cores = []
        for r, g, b, a in pixels:
            if a < 50:
                continue
            # Ignora fundo branco/creme muito claro
            if r > 215 and g > 215 and b > 210:
                continue
            cores.append((r, g, b))
            
        if not cores:
            return "#B89C72"
            
        # Média dos pixels válidos
        r_total = sum(c[0] for c in cores)
        g_total = sum(c[1] for c in cores)
        b_total = sum(c[2] for c in cores)
        n = len(cores)
        
        return f"#{r_total//n:02x}{g_total//n:02x}{b_total//n:02x}"
    except Exception:
        return "#B89C72"

def obter_estilo_moldura(perfume):
    # Usamos uma moldura dourada universal (#D4AF37 / RGB 212, 175, 55) correspondente à cor das estrelas
    # de avaliação para garantir consistência e harmonia com o tom quente e creme do card
    rgb_str = "212, 175, 55"
            
    # Se for uma imagem de composição fotorrealista, desativa a mesclagem e mantém a moldura com cor do frasco
    if "composicao" in perfume.get("frasco_imagem", ""):
        return f"mix-blend-mode: normal; border: 1.5px solid rgba({rgb_str}, 0.85); border-radius: 24px; box-shadow: 0 15px 40px rgba(0,0,0,0.08);"

    marca = perfume["marca"].upper()
    ESTILOS_CURADORIA = {
        "MINIMALISTA": ["BYREDO", "DIPTYQUE", "MAISON FRANCIS KURKDJIAN", "CHANEL", "TOM FORD", "REPLICA", "BVLGARI LE GEMME"],
        "CURIOSIDADES": ["XERJOFF", "CASAMORATI", "MAISON CRIVELLI", "GUERLAIN", "NISHANE", "PARFUMS DE MARLY", "KILIAN"]
    }
    
    # 1. ESTILO MINIMALISTA (Contorno ultra fino e discreto cinza/neutro)
    if any(m in marca for m in ESTILOS_CURADORIA["MINIMALISTA"]):
        return f"border: 1px solid rgba({rgb_str}, 0.35); border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.03);"
        
    # 2. ESTILO GABINETE DE CURIOSIDADES (Borda terrosa/orgânica fina e shadow médio)
    elif any(m in marca for m in ESTILOS_CURADORIA["CURIOSIDADES"]):
        return f"border: 1.5px solid rgba({rgb_str}, 0.55); border-radius: 24px; box-shadow: 0 12px 30px rgba(0,0,0,0.06);"
        
    # 3. ESTILO PASSEPAROUT BELAS ARTES (Contorno dourado envelhecido fino e shadow de papel)
    else:
        return f"border: 1.5px solid rgba({rgb_str}, 0.85); border-radius: 24px; box-shadow: 0 15px 40px rgba(0,0,0,0.08);"

def render_perfume_images():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "perfumes_data.json")
    template_path = os.path.join(current_dir, "profile_template.html")
    output_dir = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\Identidadevisual\fotos\nuvemshop"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    if not os.path.exists(json_path):
        print(f"[ERRO] O arquivo {json_path} não foi encontrado.")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        perfumes = json.load(f)
        
    # Filtrar por perfume específico se fornecido via argumento
    if "--perfume" in sys.argv:
        try:
            perfume_idx = sys.argv.index("--perfume")
            target_id = sys.argv[perfume_idx + 1]
            perfumes = [p for p in perfumes if p.get("id") == target_id]
            print(f"[FOCADO] Renderizando apenas o perfume com ID: {target_id} ({len(perfumes)} encontrado(s))")
        except IndexError:
            print("[AVISO] ID do perfume não especificado após --perfume.")
            
    if "--limit" in sys.argv:
        try:
            limit_idx = sys.argv.index("--limit")
            limit_val = int(sys.argv[limit_idx + 1])
            perfumes = perfumes[:limit_val]
            print(f"[LIMITADO] Renderizando apenas os primeiros {limit_val} perfumes.")
        except (IndexError, ValueError):
            pass
            
    if not os.path.exists(template_path):
        print(f"[ERRO] O arquivo {template_path} não foi encontrado.")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    print("\n[INFO] Inicializando o renderizador de imagens...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 1380})
        
        for perfume in perfumes:
            p_id = perfume.get("id", "temp_perfume")
            print(f"-> Processando: {perfume['nome']} ({perfume['marca']})...")
            
            # Popula as tags
            html_content = template_content
            html_content = html_content.replace("{{ nome }}", perfume["nome"])
            html_content = html_content.replace("{{ marca }}", perfume["marca"])
            html_content = html_content.replace("{{ concentracao }}", perfume["concentracao"])
            html_content = html_content.replace("{{ descricao }}", build_description(perfume))
            html_content = html_content.replace("{{ slogan }}", perfume["slogan"])
            html_content = html_content.replace("{{ nota_avaliacao }}", str(perfume["nota_avaliacao"]))
            html_content = html_content.replace("{{ votos_avaliacao }}", str(perfume["votos_avaliacao"]))
            # Adiciona o caminho da subpasta fotos se for um frasco real baixado
            frasco_img_path = perfume["frasco_imagem"]
            if not frasco_img_path.startswith("fotos/") and not frasco_img_path.startswith("http"):
                frasco_img_path = "fotos/" + frasco_img_path
            html_content = html_content.replace("{{ frasco_imagem }}", frasco_img_path)
            
            # Converte estruturas complexas em HTML
            html_content = html_content.replace("{{ principais_acordes }}", build_accords_html(perfume["principais_acordes"]))
            html_content = html_content.replace("{{ notas_topo }}", build_notes_html(perfume["notas"]["topo"], current_dir))
            html_content = html_content.replace("{{ notas_coracao }}", build_notes_html(perfume["notas"]["coracao"], current_dir))
            html_content = html_content.replace("{{ notas_base }}", build_notes_html(perfume["notas"]["base"], current_dir))
            html_content = html_content.replace("{{ estacoes }}", build_seasons_html(perfume["estacoes"]))
            html_content = html_content.replace("{{ perfumistas_detalhes }}", build_perfumistas_html(perfume.get("perfumistas_detalhes", []), current_dir))
            html_content = html_content.replace("{{ percepcao_genero }}", build_gender_html(perfume["percepcao_genero"]))
            
            # Performance
            html_content = html_content.replace("{{ longevidade_texto }}", perfume["perfil_olfativo"]["longevidade_texto"])
            html_content = html_content.replace("{{ longevidade_horas }}", perfume["perfil_olfativo"]["longevidade_horas"])
            html_content = html_content.replace("{{ rastro_texto }}", perfume["perfil_olfativo"]["rastro_texto"])
            
            # Turnos
            html_content = html_content.replace("{{ turnos }}", build_turnos_html(perfume["diurno_votos"]))
            
            # Sem decantes complexos no HTML
            
            # Injetar o estilo de moldura calculado pela competência de curadoria
            html_content = html_content.replace("{{ bottle_img_style }}", obter_estilo_moldura(perfume))
            
            # Salva o arquivo temporário populado
            temp_html_path = os.path.join(current_dir, f"temp_{p_id}.html")
            with open(temp_html_path, "w", encoding="utf-8") as f_temp:
                f_temp.write(html_content)
                
            # Renderizar no navegador headless
            file_url = f"file:///{temp_html_path.replace(os.sep, '/')}"
            page.goto(file_url)
            
            # Espera carregar fontes do Google e imagens
            page.wait_for_timeout(2500)
            
            # Tira o print e salva na pasta de output
            sku = get_sku_2ml(perfume["marca"], perfume["nome"])
            output_image_path = os.path.join(output_dir, f"{sku}_2.jpeg")
            page.screenshot(path=output_image_path, type="jpeg", quality=92, full_page=False)
            
            # Injetar validacao de qualidade visual do card de perfil renderizado (Quality Gate)
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                print(f"   [*] Iniciando Quality Gate na imagem de perfil renderizada (Foto 2) para '{p_id}'...")
                try:
                    from google import genai
                    from google.genai import types
                    from PIL import Image as PILImage
                    
                    client = genai.Client(api_key=api_key)
                    img_profile = PILImage.open(output_image_path)
                    
                    prompt_validador = f"""
Role: Hard-nosed, high-end commercial luxury art director and product quality controller.
Task: Analyze the rendered perfume profile card image (Foto 2) to ensure it was formatted and captured correctly.

Checks:
1. No Raw Placeholders: Ensure there are no raw unrendered brackets like '{{{{' or '}}}}' visible in the texts of the card.
2. Layout Alignment: Confirm that the text does not overlap, the layout is clean, and the bottle image is visible.
3. No Broken Images: Ensure that the bottle image is present and not displaying a broken image icon.

Respond strictly in JSON format:
{{
  "score": 10,
  "approved": true,
  "identified_flaws": []
}}
"""
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[img_profile, prompt_validador],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.1
                        )
                    )
                    
                    res_json = json.loads(response.text.strip())
                    score = res_json.get("score", 10)
                    approved = res_json.get("approved", True)
                    flaws = res_json.get("identified_flaws", [])
                    
                    if not approved:
                        print(f"\n   [!!! CARD REPROVADO PELO QUALITY GATE (NOTA {score}/10) !!!]")
                        print(f"   Falhas na renderizacao do card:")
                        for f in flaws:
                            print(f"    - {f}")
                        print("   Deletando card de perfil nao-conforme do disco.")
                        if os.path.exists(output_image_path):
                            os.remove(output_image_path)
                    else:
                        print(f"   [OK Quality Gate] Card de perfil aprovado! Nota: {score}/10")
                except Exception as e_ia:
                    print(f"   [AVISO Quality Gate] Falha ao rodar validacao multimodal no card: {e_ia}")
            else:
                print("   [INFO Quality Gate] GEMINI_API_KEY nao encontrada no ambiente. Pulando a validacao de IA.")
            
            if os.path.exists(output_image_path):
                print(f"   [OK] Imagem salva em: {output_image_path}")
            
            # Limpar arquivo temporário
            try:
                os.remove(temp_html_path)
            except OSError:
                pass
            
        browser.close()
    print("\n[SUCESSO] Renderização em lote finalizada com sucesso!")

if __name__ == "__main__":
    render_perfume_images()
