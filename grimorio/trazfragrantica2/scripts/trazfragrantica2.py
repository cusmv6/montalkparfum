import os
import json
import shutil
import sys
import argparse
import csv
import re
from playwright.sync_api import sync_playwright

# Configuração de caminhos e diretórios
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
VISCATEGORIA_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\Identidadevisual\fotos\viscategoria"
JSON_PATH = os.path.join(VISCATEGORIA_DIR, "perfumes_data.json")
FOTOS_DIR = os.path.join(VISCATEGORIA_DIR, "fotos")
OUTPUT_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\Identidadevisual\fotos\nuvemshop2"
TEMPLATE_PATH = os.path.join(SCRIPTS_DIR, "composition_template.html")
CSV_PRODUTOS_PATH = r"C:\Users\odeao\OneDrive\Desktop\brem\Bruno\produtos\importar_nuvemshop.csv"

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
    """
    Tenta ler o SKU correspondente à primeira variação (2ml) do perfume no CSV de importação.
    """
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
    """
    Gera o SKU dinamicamente como fallback caso o perfume não esteja no CSV de importação.
    """
    slug_brand = slugify(brand)
    slug_name = slugify(name)
    sku_clean_brand = slug_brand.upper()[:4]
    sku_clean_name = slug_name.replace("-", "")[:6].upper()
    return f"DEC-{sku_clean_brand}-{sku_clean_name}-2ML"

def obter_estilo_moldura(perfume):
    """
    Retorna o estilo CSS da moldura do frasco, correspondendo à grife do perfume.
    Calculado dinamicamente para manter consistência com o card de perfil original.
    """
    rgb_str = "212, 175, 55"
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

def process_perfumes(target_ids=None):
    if not os.path.exists(OUTPUT_DIR):
        print(f"[INFO] Criando pasta de saída: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR)
        
    if not os.path.exists(JSON_PATH):
        print(f"[ERRO] O banco de dados local {JSON_PATH} não foi encontrado.")
        sys.exit(1)
        
    if not os.path.exists(TEMPLATE_PATH):
        print(f"[ERRO] O template HTML {TEMPLATE_PATH} não foi encontrado.")
        sys.exit(1)
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        perfumes = json.load(f)
        
    # Filtrar perfumes se ID for especificado
    if target_ids:
        perfumes = [p for p in perfumes if p.get("id") in target_ids]
        
    if not perfumes:
        print("[AVISO] Nenhum perfume correspondente encontrado para processamento.")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Registro para rastrear SKUs processados nesta execução para alertar sobre colisões
    skus_processados = {}

    print(f"\n[INFO] Inicializando renderizador para {len(perfumes)} perfume(s)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 1380})
        
        for perfume in perfumes:
            p_id = perfume.get("id", "temp_perfume")
            brand = perfume.get("marca", "")
            name = perfume.get("nome", "")
            print(f"-> Processando: {name} ({brand})...")
            
            # Obter SKU correspondente
            sku = obter_sku_do_csv(p_id, brand, name)
            if sku:
                print(f"   [SKU ENCONTRADO NO CSV] SKU: {sku}")
            else:
                sku = gerar_sku_dinamico(brand, name)
                print(f"   [SKU GERADO DINAMICAMENTE (FALLBACK)] SKU: {sku}")
                
            # Verificar colisão de SKU
            if sku in skus_processados:
                outro_id = skus_processados[sku]
                print(f"\n   [!!! ALERTA DE COLISÃO DE SKU CRÍTICO !!!]")
                print(f"   O SKU '{sku}' já foi associado ao perfume '{outro_id}' anteriormente!")
                print(f"   A imagem atual para '{p_id}' SOBRESCREVERÁ a imagem gerada para '{outro_id}' no disco local!")
                print(f"   * Sugestão: Ajuste os SKUs no uploader ou CSV de produtos para que sejam únicos. *\n")
            else:
                skus_processados[sku] = p_id
            
            # Localizar imagem do frasco de composição com fallback para imagem real
            frasco_img_name = perfume.get("frasco_imagem", "")
            abs_img_path = os.path.join(FOTOS_DIR, frasco_img_name)
            
            if not frasco_img_name or not os.path.exists(abs_img_path):
                # Tenta fallback para _real.jpg
                fallback_name = f"{p_id}_real.jpg"
                abs_img_path_fallback = os.path.join(FOTOS_DIR, fallback_name)
                if os.path.exists(abs_img_path_fallback):
                    print(f"   [FALLBACK] Imagem de composição não encontrada. Usando imagem real: {fallback_name}")
                    abs_img_path = abs_img_path_fallback
                else:
                    print(f"   [AVISO] Nenhuma imagem de frasco encontrada para {p_id}.")
            
            # Formata caminho absoluto para URL de arquivo local do browser
            frasco_url = f"file:///{abs_img_path.replace(os.sep, '/')}"
            
            # Substitui placeholders no HTML
            html_content = template_content
            html_content = html_content.replace("{{ nome }}", name)
            html_content = html_content.replace("{{ marca }}", brand)
            html_content = html_content.replace("{{ concentracao }}", perfume["concentracao"])
            html_content = html_content.replace("{{ frasco_imagem }}", frasco_url)
            html_content = html_content.replace("{{ bottle_img_style }}", obter_estilo_moldura(perfume))
            
            # Salvar HTML temporário na pasta de scripts para carregar CSS corretamente
            temp_html_path = os.path.join(SCRIPTS_DIR, f"temp_comp_{p_id}.html")
            with open(temp_html_path, "w", encoding="utf-8") as f_temp:
                f_temp.write(html_content)
                
            try:
                # Navegar até o arquivo local temporário
                file_url = f"file:///{temp_html_path.replace(os.sep, '/')}"
                page.goto(file_url)
                
                # Aguardar carregamento de fontes do Google e imagem
                page.wait_for_timeout(2500)
                
                # Tirar print com as dimensões de 1280x1380
                output_image_path = os.path.join(OUTPUT_DIR, f"{sku}.jpeg")
                page.screenshot(path=output_image_path, type="jpeg", quality=92, full_page=False)
                
                # Injetar validação de fidelidade multimodal (Quality Gate)
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    print("   [*] Iniciando Quality Gate na imagem de composição (Foto 3)...")
                    try:
                        from google import genai
                        from google.genai import types
                        from PIL import Image as PILImage
                        
                        client = genai.Client(api_key=api_key)
                        img_comp = PILImage.open(output_image_path)
                        
                        prompt_validador = f"""
Role: Hard-nosed, high-end commercial luxury art director and product quality controller.
Task: Analyze the composition product card (Foto 3) to ensure absolute visual quality and alignment with perfume characteristics.

Brand: {brand}
Perfume Name: {name}
Expected Concentração: {perfume.get('concentracao', '')}

Checks:
1. Text Integrity: Verify if the text overlay of brand name '{brand}', perfume '{name}', and concentration is clean, readable, spelled correctly, and not overlapping with the bottle image or borders.
2. Pedestal & Setup: Is the bottle nicely framed inside its stylized border and does the design look balanced and luxury-focused?
3. Visual Artifacts: Are there any clipping or rendering distortions inside the frame?

Respond strictly in JSON format:
{{
  "score": 10, // Integer 1-10
  "approved": true, // Boolean (score >= 9)
  "identified_flaws": ["Details of flaws like overlapping texts, missing elements or wrong alignment"],
  "corrective_instructions": "Technical instructions to fix layout/HTML template parameters if needed"
}}
"""
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[img_comp, prompt_validador],
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
                            print(f"\n   [!!! REPROVADA PELO QUALITY GATE (NOTA {score}/10) !!!]")
                            print(f"   Falhas no layout / composicao:")
                            for f in flaws:
                                print(f"    - {f}")
                            print("   Deletando imagem nao-conforme do disco para evitar upload incorreto.")
                            if os.path.exists(output_image_path):
                                os.remove(output_image_path)
                        else:
                            print(f"   [OK Quality Gate] Imagem aprovada com sucesso! Nota: {score}/10")
                    except Exception as e_ia:
                        print(f"   [AVISO Quality Gate] Falha ao rodar validacao multimodal do Gemini: {e_ia}")
                else:
                    print("   [INFO Quality Gate] GEMINI_API_KEY nao encontrada no ambiente. Pulando a validacao de IA.")
                
                if os.path.exists(output_image_path):
                    print(f"   [OK] Imagem final salva com sucesso:")
                    print(f"        - {os.path.basename(output_image_path)}")
                
            except Exception as e:
                print(f"   [ERRO] Falha ao renderizar {p_id}: {e}")
                
            finally:
                # Sempre limpa o HTML temporário
                if os.path.exists(temp_html_path):
                    try:
                        os.remove(temp_html_path)
                    except OSError:
                        pass
                        
        browser.close()
    print("\n[SUCESSO] Processamento de composições finalizado com sucesso!")

def main():
    parser = argparse.ArgumentParser(description="Skill 'trazfragrantica2' - Gera cards de composição olfativa-visual (Foto 3) para e-commerce.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    run_parser = subparsers.add_parser("run", help="Executa a renderização dos cards de composição.")
    run_parser.add_argument("--perfume", required=True, help="ID do perfume ou lista de IDs separados por vírgula.")
    
    args = parser.parse_args()
    
    if args.command == "run":
        p_ids = [pid.strip() for pid in args.perfume.split(",") if pid.strip()]
        process_perfumes(p_ids)

if __name__ == "__main__":
    main()
