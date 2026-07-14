import os
import sys
import json
import re
import urllib.request
import urllib.parse
import ssl
import argparse
import subprocess
import time
import shutil
from bs4 import BeautifulSoup

# Importa a função de retoque local
try:
    from draw_perfect_text import process_image as retouch_creed_bottle
except ImportError:
    retouch_creed_bottle = None

# Paths relative to workspace root
WORKSPACE_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem"
VISCATEGORIA_DIR = os.path.join(WORKSPACE_DIR, "PROJETOS", "Bruno", "Identidadevisual", "fotos", "viscategoria")
JSON_PATH = r"C:\Users\odeao\OneDrive\Desktop\brem\PROJETOS\Bruno\produtos\catalogo.json"
RENDER_SCRIPT = os.path.join(VISCATEGORIA_DIR, "render_profiles.py")

URL_OVERRIDES = {
    "amouage_cristal_gold_man": "https://www.fragrantica.com.br/perfume/Amouage/Cristal-Gold-Man-88160.html",
    "amouage_cristal_gold_woman": "https://www.fragrantica.com.br/perfume/Amouage/Cristal-Gold-Woman-88159.html",
    "amouage_guidance_46": "https://www.fragrantica.com.br/perfume/Amouage/Guidance-46-94033.html",
    "amouage_guidance": "https://www.fragrantica.com.br/perfume/Amouage/Guidance-78656.html",
    "amouage_interlude_53": "https://www.fragrantica.com.br/perfume/Amouage/Interlude-53-Man-64153.html",
    "byredo_vanille_antique": "https://www.fragrantica.com.br/perfume/Byredo/Vanille-Antique-73438.html",
    "creed_green_irish_tweed": "https://www.fragrantica.com.br/perfume/Creed/Green-Irish-Tweed-474.html"
}

PERFUMISTA_OVERRIDES = {
    "byredo_vanille_antique": ["Jérôme Epinette"],
    "byredo_mojave_ghost": ["Jérôme Epinette"],
    "byredo_gypsy_water": ["Jérôme Epinette"],
    "byredo_bal_dafrique_absolu": ["Jérôme Epinette"],
    "byredo_bal_dafrique": ["Jérôme Epinette"]
}

def slugify_local(text):
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

def find_url_ddg(brand, name):
    query = f"site:fragrantica.com.br {brand} {name}"
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }
    
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=context, timeout=10) as response:
            html = response.read().decode('utf-8', errors='replace')
            
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        
        candidates = []
        for link in links:
            href = link.get("href", "")
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            actual_url = qs.get("uddg", [None])[0]
            
            if not actual_url and "uddg=" in href:
                match = re.search(r'uddg=(https%3A%2F%2Fwww\.fragrantica\.com\.br%2Fperfume%2F[^&]+)', href)
                if match:
                    actual_url = urllib.parse.unquote(match.group(1))
            
            if not actual_url and "fragrantica.com.br/perfume/" in href:
                actual_url = href
                
            if actual_url and "fragrantica.com.br/perfume/" in actual_url:
                clean_url = actual_url.split("?")[0]
                if clean_url not in candidates:
                    candidates.append(clean_url)
                    
        if not candidates:
            return None
            
        best_url = None
        best_score = -999
        
        brand_words = [w for w in slugify_local(brand).split("-") if len(w) > 2]
        name_words = [w for w in slugify_local(name).split("-") if len(w) > 2]
        
        for cand in candidates:
            cand_lower = cand.lower()
            score = 0
            
            # Match de palavras da Marca
            brand_match = False
            for word in brand_words:
                if word in cand_lower:
                    score += 10
                    brand_match = True
                    
            # Match de palavras do Nome
            matched_words = 0
            for word in name_words:
                if word in cand_lower:
                    score += 5
                    matched_words += 1
                    
            # Bônus de correspondência conjunta
            if brand_match and matched_words > 0:
                score += 20
                
            # Penalidade por palavras intrusas na URL (como edições variantes ou marcas erradas)
            match_seg = re.search(r'/perfume/([^/]+)/([^/]+)\.html', cand_lower)
            if match_seg:
                segment_text = f"{match_seg.group(1)}-{match_seg.group(2)}"
                segment_words = [w for w in segment_text.split("-") if len(w) > 2 and not w.isdigit()]
                for sw in segment_words:
                    if sw not in brand_words and sw not in name_words:
                        score -= 2
                        
            if score > best_score:
                best_score = score
                best_url = cand
                
        if best_score > 0:
            return best_url
            
    except Exception as e:
        print(f"   [AVISO] Erro na busca DuckDuckGo para {brand} {name}: {e}")
        
    return None

def fetch_and_parse_perfume(url, brand, name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }
    
    context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=context, timeout=15) as response:
        html = response.read().decode('utf-8', errors='replace')
        
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Rating e Votos
    rating = 4.0
    votes = 100
    rating_span = soup.find("span", {"itemprop": "ratingValue"})
    votes_span = soup.find("span", {"itemprop": "ratingCount"})
    if rating_span:
        try:
            rating = float(rating_span.text.replace(",", ".").strip())
        except ValueError:
            pass
    if votes_span:
        try:
            votes = int(re.sub(r'[^\d]', '', votes_span.text))
        except ValueError:
            pass
            
    # 2. Imagem do Frasco
    frasco_img_url = None
    img_el = soup.find("img", {"itemprop": "image"})
    if img_el:
        frasco_img_url = img_el.get("src")
    else:
        fimgs = soup.find_all("img", src=re.compile(r"fimgs\.net/images/perfume/o\.|fimgs\.net/images/perfume/375x500|fimgs\.net/mdimg/perfume-thumbs/375x500"))
        if fimgs:
            frasco_img_url = fimgs[0].get("src")
            
    # 3. Principais Acordes (com suporte Hex e RGB)
    acordes = []
    for div in soup.find_all("div", style=True):
        span = div.find("span", class_="truncate")
        if span and "background" in div["style"] and "width" in div["style"]:
            text = span.text.strip().title()
            style = div["style"]
            
            color = "#C5A880"
            hex_match = re.search(r'background(?:-color)?:\s*(#[0-9a-fA-F]{3,6})', style)
            if hex_match:
                color = hex_match.group(1)
            else:
                rgb_match = re.search(r'background(?:-color)?:\s*rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', style)
                if rgb_match:
                    color = f"#{int(rgb_match.group(1)):02x}{int(rgb_match.group(2)):02x}{int(rgb_match.group(3)):02x}"
                    
            width_match = re.search(r'width:\s*([0-9\.]+)%', style)
            width = float(width_match.group(1)) if width_match else 100.0
            
            text_color_match = re.search(r'color:\s*(#[0-9a-fA-F]+)', style)
            text_color = text_color_match.group(1) if text_color_match else "#000000"
            
            acordes.append({
                "nome": text,
                "intensidade": width,
                "cor": color,
                "texto_cor": text_color
            })
            
    # 4. Pirâmide Olfativa
    topo_notes = []
    coracao_notes = []
    base_notes = []
    
    divs = soup.find_all(class_='pyramid-level-container')
    if len(divs) == 3:
        topo_notes = [a.text.strip() for a in divs[0].find_all(class_='pyramid-note-label') if a.text.strip()]
        coracao_notes = [a.text.strip() for a in divs[1].find_all(class_='pyramid-note-label') if a.text.strip()]
        base_notes = [a.text.strip() for a in divs[2].find_all(class_='pyramid-note-label') if a.text.strip()]
        
    if not topo_notes and not coracao_notes and not base_notes:
        all_links = soup.find_all("a", href=re.compile(r"/notas/"))
        gen_notes = [lk.text.strip() for lk in all_links if lk.text.strip() and lk.text.strip().lower() != "notas"]
        if gen_notes:
            topo_notes = gen_notes[:max(2, len(gen_notes)//3)]
            coracao_notes = gen_notes[len(topo_notes):len(topo_notes)+(len(gen_notes)//3)]
            base_notes = gen_notes[len(topo_notes)+len(coracao_notes):]
            
    # 5. Metadados do Perfume
    familia_olfativa = "Compartilhável"
    genero_comercial = "Compartilhável (Unissex)"
    ano_lancamento = 2022
    perfumistas = []
    
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc:
        desc = meta_desc["content"]
        ano_match = re.search(r'lançado em (\d{4})', desc)
        if ano_match:
            ano_lancamento = int(ano_match.group(1))
            
        perf_match = re.search(r'criado por ([^.]+)\.|created by ([^.]+)\.|perfumista que assina esta fragr[âa]ncia [ée] ([^.]+)\.', desc, re.I)
        if perf_match:
            perf_text = perf_match.group(1) or perf_match.group(2) or perf_match.group(3)
            names = re.split(r'\s+e\s+|,|\s+and\s+', perf_text)
            perfumistas = [n.strip() for n in names if n.strip()]
            
        fam_match = re.search(r'é um perfume ([^.]+)\.', desc)
        if fam_match:
            fam_text = fam_match.group(1)
            if "feminino" in fam_text.lower():
                genero_comercial = "Feminino"
                familia_olfativa = fam_text.lower().replace("feminino", "").strip().title()
            elif "masculino" in fam_text.lower():
                genero_comercial = "Masculino"
                familia_olfativa = fam_text.lower().replace("masculino", "").strip().title()
            else:
                genero_comercial = "Compartilhável (Unissex)"
                familia_olfativa = fam_text.lower().replace("compartilhável", "").replace("compartilhavel", "").strip().title()
                
    if not topo_notes:
        topo_notes = ["Bergamota", "Tangerina"]
    if not coracao_notes:
        coracao_notes = ["Lavanda", "Jasmim"]
    if not base_notes:
        base_notes = ["Sândalo", "Almíscar"]
        
    # 6. Perfumistas com foto
    perfumistas_detalhes = []
    for h3 in soup.find_all("h3"):
        h3_text = h3.text.strip().lower()
        if "perfumista" in h3_text or "nariz" in h3_text or "perfumer" in h3_text:
            grandparent = h3.parent.parent
            for a in grandparent.find_all("a", href=re.compile(r"/narizes/")):
                img = a.find("img")
                img_url = img.get("src") if img else None
                p_name = a.text.strip()
                if not p_name and img:
                    p_name = img.get("alt", "").strip()
                if p_name:
                    perfumistas_detalhes.append({
                        "nome": p_name,
                        "foto": img_url
                    })
                    
    # Download das fotos localmente
    if perfumistas_detalhes:
        perf_dir = os.path.join(VISCATEGORIA_DIR, "fotos", "perfumistas")
        os.makedirs(perf_dir, exist_ok=True)
        
        for pd in perfumistas_detalhes:
            if pd["foto"] and pd["foto"].startswith("http"):
                # slugify helper
                import unicodedata
                nfkd_form = unicodedata.normalize('NFKD', pd["nome"].lower().strip())
                slug = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
                slug = re.sub(r"[^\w\s-]", "", slug)
                slug = re.sub(r"[-\s]+", "_", slug)
                local_name = f"{slug}.jpg"
                local_path = os.path.join(perf_dir, local_name)
                try:
                    req = urllib.request.Request(pd["foto"], headers=headers)
                    with urllib.request.urlopen(req, context=context, timeout=10) as img_resp:
                        with open(local_path, "wb") as img_file:
                            img_file.write(img_resp.read())
                    pd["foto"] = f"fotos/perfumistas/{local_name}"
                except Exception as e:
                    print(f"      [AVISO] Falha ao baixar foto do perfumista {pd['nome']}: {e}")
        
    return {
        "nome": name.upper(),
        "marca": brand.upper(),
        "rating": rating,
        "votes": votes,
        "frasco_url": frasco_img_url,
        "acordes": acordes,
        "notes": {
            "topo": topo_notes,
            "coracao": coracao_notes,
            "base": base_notes
        },
        "familia": familia_olfativa,
        "ano": ano_lancamento,
        "perfumistas": perfumistas,
        "perfumistas_detalhes": perfumistas_detalhes,
        "genero": genero_comercial
    }

def calculate_olfactory_perceptions(acordes, notes, genero):
    # Diurno/Noite
    noite_keywords = ["especiado", "âmbar", "couro", "defumado", "oud", "baunilha", "animal"]
    dia_keywords = ["fresco", "cítrico", "floral", "verde", "frutado", "ozônico", "aquático"]
    
    noite_score = sum(a["intensidade"] for a in acordes if any(k in a["nome"].lower() for k in noite_keywords))
    dia_score = sum(a["intensidade"] for a in acordes if any(k in a["nome"].lower() for k in dia_keywords))
    
    total = noite_score + dia_score
    if total == 0:
        dia_pct, noite_pct = 50, 50
    else:
        dia_pct = round((dia_score / total) * 100)
        noite_pct = 100 - dia_pct
        
    # Estações
    inverno_votos = 50
    primavera_votos = 50
    verao_votos = 50
    outono_votos = 50
    
    for a in acordes:
        name = a["nome"].lower()
        val = a["intensidade"]
        if any(k in name for k in ["especiado", "couro", "oud", "defumado"]):
            inverno_votos += val * 1.5
            outono_votos += val * 1.0
        elif any(k in name for k in ["cítrico", "verde", "fresco", "aquático"]):
            verao_votos += val * 1.5
            primavera_votos += val * 1.0
        elif any(k in name for k in ["floral", "frutado"]):
            primavera_votos += val * 1.5
            verao_votos += val * 1.0
            
    # Gênero
    g_fem, g_mfem, g_uni, g_mmasc, g_masc = 0, 0, 0, 0, 0
    if "feminino" in genero.lower():
        g_fem, g_mfem, g_uni = 70, 20, 10
    elif "masculino" in genero.lower():
        g_masc, g_mmasc, g_uni = 70, 20, 10
    else:
        g_uni, g_mfem, g_mmasc = 60, 20, 20
        
    # Rastro e Longevidade baseados na intensidade de acordes pesados
    heavy_score = sum(a["intensidade"] for a in acordes if any(k in a["nome"].lower() for k in ["âmbar", "couro", "defumado", "oud", "especiado quente"]))
    if heavy_score > 120:
        longevidade_texto = "Eterna"
        longevidade_horas = "10h+"
        rastro_texto = "Enorme"
    elif heavy_score > 60:
        longevidade_texto = "Longa Duração"
        longevidade_horas = "6 - 10 h"
        rastro_texto = "Marcante"
    else:
        longevidade_texto = "Moderada"
        longevidade_horas = "3 - 6 h"
        rastro_texto = "Moderado"
        
    return {
        "diurno_votos": {"dia": int(dia_pct), "noite": int(noite_pct)},
        "estacoes": {
            "inverno": {"votos": int(inverno_votos), "cor": "#D4F0FC"},
            "primavera": {"votos": int(primavera_votos), "cor": "#A3D977"},
            "verao": {"votos": int(verao_votos), "cor": "#FFA07A"},
            "outono": {"votos": int(outono_votos), "cor": "#EAD2AC"}
        },
        "percepcao_genero": {
            "feminino": int(g_fem),
            "mais_feminino": int(g_mfem),
            "unissex": int(g_uni),
            "mais_masculino": int(g_mmasc),
            "masculino": int(g_masc),
            "classe_genero": "masculino" if g_masc > g_fem and g_masc > g_uni else ("feminino" if g_fem > g_masc and g_fem > g_uni else "unissex")
        },
        "perfil_olfativo": {
            "longevidade_texto": longevidade_texto,
            "longevidade_horas": longevidade_horas,
            "rastro_texto": rastro_texto
        }
    }

def scrape_perfume_playwright(url, brand, name):
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
    import re

    print(f"   [PLAYWRIGHT] Inicializando navegador em segundo plano para: {name}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            locale="pt-BR"
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="commit", timeout=30000)
            page.wait_for_timeout(4000)
            
            # Rolar pagina lentamente para acionar lazy-loading
            for i in range(12):
                page.evaluate(f"window.scrollTo(0, {i * 800})")
                page.wait_for_timeout(250)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(4000)
            
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            [s.decompose() for s in soup(['script', 'style'])]
            
            # 1. Rating e Votos
            rating = 4.0
            votes = 100
            rating_span = soup.find("span", {"itemprop": "ratingValue"})
            votes_span = soup.find("span", {"itemprop": "ratingCount"})
            if rating_span:
                try:
                    rating = float(rating_span.text.replace(",", ".").strip())
                except ValueError:
                    pass
            if votes_span:
                try:
                    votes = int(re.sub(r'[^\d]', '', votes_span.text))
                except ValueError:
                    pass
            
            # 2. Imagem
            frasco_img_url = None
            img_el = soup.find("img", {"itemprop": "image"})
            if img_el:
                frasco_img_url = img_el.get("src")
            if not frasco_img_url:
                fimgs = soup.find_all("img", src=re.compile(r"fimgs\.net/images/perfume/o\.|fimgs\.net/images/perfume/375x500|fimgs\.net/mdimg/perfume-thumbs/375x500"))
                if fimgs:
                    frasco_img_url = fimgs[0].get("src")
            
            # 3. Acordes
            acordes = []
            for div in soup.find_all("div", style=True):
                span = div.find("span", class_="truncate")
                if span and "background" in div["style"] and "width" in div["style"]:
                    text = span.text.strip().title()
                    style = div["style"]
                    
                    color = "#C5A880"
                    hex_match = re.search(r'background(?:-color)?:\s*(#[0-9a-fA-F]{3,6})', style)
                    if hex_match:
                        color = hex_match.group(1)
                    else:
                        rgb_match = re.search(r'background(?:-color)?:\s*rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', style)
                        if rgb_match:
                            color = f"#{int(rgb_match.group(1)):02x}{int(rgb_match.group(2)):02x}{int(rgb_match.group(3)):02x}"
                            
                    width_match = re.search(r'width:\s*([0-9\.]+)%', style)
                    width = float(width_match.group(1)) if width_match else 100.0
                    
                    text_color_match = re.search(r'color:\s*(#[0-9a-fA-F]+)', style)
                    text_color = text_color_match.group(1) if text_color_match else "#000000"
                    
                    acordes.append({
                        "nome": text,
                        "intensidade": width,
                        "cor": color,
                        "texto_cor": text_color
                    })
            
            # 4. Piramide Olfativa
            topo_notes = []
            coracao_notes = []
            base_notes = []
            notes_sections = {
                "topo": ["Notas de Topo"],
                "coracao": ["Notas de Coração", "Notas de Cora"],
                "base": ["Notas de Base"]
            }
            for sect_key, names in notes_sections.items():
                found_list = []
                for name_variant in names:
                    header_span = soup.find("span", string=re.compile(rf"^\s*{name_variant}\s*$", re.I))
                    if header_span:
                        ggp = header_span.parent.parent.parent
                        labels = [a.text.strip() for a in ggp.find_all(class_="pyramid-note-label") if a.text.strip()]
                        if labels:
                            found_list = labels
                            break
                if sect_key == "topo":
                    topo_notes = found_list
                elif sect_key == "coracao":
                    coracao_notes = found_list
                elif sect_key == "base":
                    base_notes = found_list
            
            if not topo_notes and not coracao_notes and not base_notes:
                all_links = soup.find_all("a", href=re.compile(r"/notas/"))
                gen_notes = [lk.text.strip() for lk in all_links if lk.text.strip() and lk.text.strip().lower() != "notas"]
                if gen_notes:
                    topo_notes = gen_notes[:max(2, len(gen_notes)//3)]
                    coracao_notes = gen_notes[len(topo_notes):len(topo_notes)+(len(gen_notes)//3)]
                    base_notes = gen_notes[len(topo_notes)+len(coracao_notes):]
            
            # 5. Metadados
            familia_olfativa = "Compartilhável"
            genero_comercial = "Compartilhável (Unissex)"
            ano_lancamento = 2022
            perfumistas = []
            meta_desc = soup.find("meta", {"name": "description"})
            if meta_desc:
                desc = meta_desc["content"]
                ano_match = re.search(r'lançado em (\d{4})|released in (\d{4})', desc, re.I)
                if ano_match:
                    val = ano_match.group(1) or ano_match.group(2)
                    ano_lancamento = int(val)
                perf_match = re.search(r'criado por ([^.]+)\.|created by ([^.]+)\.|perfumista que assina esta fragr[âa]ncia [ée] ([^.]+)\.', desc, re.I)
                if perf_match:
                    perf_text = perf_match.group(1) or perf_match.group(2) or perf_match.group(3)
                    names = re.split(r'\s+e\s+|,|\s+and\s+', perf_text)
                    perfumistas = [n.strip() for n in names if n.strip()]
                fam_match = re.search(r'é um perfume ([^.]+)\.|is a ([^.]+)\.', desc, re.I)
                if fam_match:
                    fam_text = fam_match.group(1) or fam_match.group(2)
                    if "feminino" in fam_text.lower() or "female" in fam_text.lower():
                        genero_comercial = "Feminino"
                        familia_olfativa = fam_text.lower().replace("feminino", "").replace("female", "").strip().title()
                    elif "masculino" in fam_text.lower() or "male" in fam_text.lower():
                        genero_comercial = "Masculino"
                        familia_olfativa = fam_text.lower().replace("masculino", "").replace("male", "").strip().title()
                    else:
                        genero_comercial = "Compartilhável (Unissex)"
                        familia_olfativa = fam_text.lower().replace("compartilhável", "").replace("compartilhavel", "").replace("unisex", "").strip().title()
            
            # 6. Estacoes e Dia/Noite
            seasons_votes = {"inverno": 0, "primavera": 0, "verao": 0, "outono": 0}
            day_night_votes = {"dia": 0, "noite": 0}
            inverno_el = soup.find(string=re.compile(r"^\s*Inverno\s*$", re.I))
            if inverno_el:
                parent_l3 = inverno_el.parent.parent.parent
                block_text = parent_l3.text.strip().replace("\xa0", " ")
                inverno_m = re.search(r'Inverno\s*([\d\.,]+k?)', block_text, re.I)
                primavera_m = re.search(r'Primavera\s*([\d\.,]+k?)', block_text, re.I)
                verao_m = re.search(r'Ver(?:ã|a)o\s*([\d\.,]+k?)', block_text, re.I)
                outono_m = re.search(r'Outono\s*([\d\.,]+k?)', block_text, re.I)
                dia_m = re.search(r'Dia\s*([\d\.,]+k?)', block_text, re.I)
                noite_m = re.search(r'Noite\s*([\d\.,]+k?)', block_text, re.I)
                
                def parse_clean_num(match):
                    if match:
                        val_str = match.group(1).lower()
                        if 'k' in val_str:
                            cleaned = re.sub(r'[^\d\.]', '', val_str.replace(',', '.'))
                            return int(float(cleaned) * 1000) if cleaned else 0
                        else:
                            cleaned = re.sub(r'[^\d]', '', val_str)
                            return int(cleaned) if cleaned else 0
                    return 0
                
                seasons_votes["inverno"] = parse_clean_num(inverno_m)
                seasons_votes["primavera"] = parse_clean_num(primavera_m)
                seasons_votes["verao"] = parse_clean_num(verao_m)
                seasons_votes["outono"] = parse_clean_num(outono_m)
                day_night_votes["dia"] = parse_clean_num(dia_m)
                day_night_votes["noite"] = parse_clean_num(noite_m)
            
            def parse_row_votes(label):
                el_rows = soup.find_all(string=re.compile(rf"^\s*{label}\s*$", re.I))
                for el_row in el_rows:
                    curr_p = el_row.parent
                    while curr_p and curr_p.name != "body":
                        classes = curr_p.get("class") or []
                        if any("flex" in c for c in classes) and any("items-center" in c for c in classes):
                            for span in curr_p.find_all("span"):
                                t_val = span.text.strip()
                                if re.match(r'^[\d\.,]+k?$', t_val, re.I):
                                    t_val_lower = t_val.lower()
                                    if 'k' in t_val_lower:
                                        cleaned = re.sub(r'[^\d\.]', '', t_val_lower.replace(',', '.'))
                                        return int(float(cleaned) * 1000) if cleaned else 0
                                    else:
                                        cleaned = re.sub(r'[^\d]', '', t_val_lower)
                                        return int(cleaned) if cleaned else 0
                            break
                        curr_p = curr_p.parent
                return 0
            
            # 7. Genero
            gender_votes = {
                "feminino": parse_row_votes("Feminino"),
                "mais_feminino": parse_row_votes("Mais Feminino"),
                "unissex": parse_row_votes("Unissex"),
                "mais_masculino": parse_row_votes("Mais Masculino"),
                "masculino": parse_row_votes("Masculino")
            }
            
            # 8. Longevidade
            longevity_votes = {
                "eterno": parse_row_votes("Eterno"),
                "longa_duracao": parse_row_votes("Longa Duração") or parse_row_votes("Longa Duraço"),
                "moderada": parse_row_votes("Moderada"),
                "fraco": parse_row_votes("Fraco"),
                "muito_fraco": parse_row_votes("Muito Fraco")
            }
            
            # 9. Sillage
            sillage_votes = {
                "enorme": parse_row_votes("Enorme"),
                "forte": parse_row_votes("Forte"),
                "moderada": parse_row_votes("Moderada"),
                "intimo": parse_row_votes("Íntimo") or parse_row_votes("Intimo")
            }
            moderada_elements = soup.find_all(string=re.compile(r"^\s*Moderada\s*$", re.I))
            if len(moderada_elements) > 1:
                try:
                    curr_p = moderada_elements[1].parent
                    while curr_p and curr_p.name != "body":
                        classes = curr_p.get("class") or []
                        if any("flex" in c for c in classes) and any("items-center" in c for c in classes):
                            for span in curr_p.find_all("span"):
                                t_val = span.text.strip()
                                if t_val.isdigit():
                                    sillage_votes["moderada"] = int(t_val)
                                    break
                            break
                        curr_p = curr_p.parent
                except Exception:
                    pass
            
            if not topo_notes: topo_notes = ["Bergamota"]
            if not coracao_notes: coracao_notes = ["Jasmim"]
            if not base_notes: base_notes = ["Almíscar"]
            if not perfumistas: perfumistas = ["Perfumista"]
            
            # 10. Perfumistas com foto
            perfumistas_detalhes = []
            for h3 in soup.find_all("h3"):
                h3_text = h3.text.strip().lower()
                if "perfumista" in h3_text or "nariz" in h3_text or "perfumer" in h3_text:
                    grandparent = h3.parent.parent
                    for a in grandparent.find_all("a", href=re.compile(r"/narizes/")):
                        img = a.find("img")
                        img_url = img.get("src") if img else None
                        p_name = a.text.strip()
                        if not p_name and img:
                            p_name = img.get("alt", "").strip()
                        if p_name:
                            perfumistas_detalhes.append({
                                "nome": p_name,
                                "foto": img_url
                            })
                            
            # Download das fotos localmente
            if perfumistas_detalhes:
                perf_dir = os.path.join(VISCATEGORIA_DIR, "fotos", "perfumistas")
                os.makedirs(perf_dir, exist_ok=True)
                
                import ssl
                import urllib.request
                dl_context = ssl._create_unverified_context()
                dl_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                }
                
                for pd in perfumistas_detalhes:
                    if pd["foto"] and pd["foto"].startswith("http"):
                        import unicodedata
                        nfkd_form = unicodedata.normalize('NFKD', pd["nome"].lower().strip())
                        slug = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
                        slug = re.sub(r"[^\w\s-]", "", slug)
                        slug = re.sub(r"[-\s]+", "_", slug)
                        local_name = f"{slug}.jpg"
                        local_path = os.path.join(perf_dir, local_name)
                        try:
                            req_dl = urllib.request.Request(pd["foto"], headers=dl_headers)
                            with urllib.request.urlopen(req_dl, context=dl_context, timeout=10) as img_resp:
                                with open(local_path, "wb") as img_file:
                                    img_file.write(img_resp.read())
                            pd["foto"] = f"fotos/perfumistas/{local_name}"
                        except Exception as e:
                            print(f"      [AVISO] Falha ao baixar foto do perfumista {pd['nome']}: {e}")
            
            return {
                "nome": name.upper(),
                "marca": brand.upper(),
                "rating": rating,
                "votes": votes,
                "frasco_url": frasco_img_url,
                "acordes": acordes,
                "notes": {
                    "topo": topo_notes,
                    "coracao": coracao_notes,
                    "base": base_notes
                },
                "ano": ano_lancamento,
                "perfumistas": perfumistas,
                "perfumistas_detalhes": perfumistas_detalhes,
                "genero": genero_comercial,
                "familia": familia_olfativa,
                "real_seasons": seasons_votes,
                "real_day_night": day_night_votes,
                "real_gender": gender_votes,
                "real_longevity": longevity_votes,
                "real_sillage": sillage_votes,
                "scraped_via_playwright": True
            }
            
        except Exception as e:
            print(f"   [ERRO PLAYWRIGHT] Falha ao raspar via Playwright: {e}")
            return None
        finally:
            browser.close()

def map_playwright_perceptions(details):
    # Seasons
    estacoes_dict = {
        "inverno": {"votos": details["real_seasons"]["inverno"], "cor": "#D4F0FC"},
        "primavera": {"votos": details["real_seasons"]["primavera"], "cor": "#A3D977"},
        "verao": {"votos": details["real_seasons"]["verao"], "cor": "#FFA07A"},
        "outono": {"votos": details["real_seasons"]["outono"], "cor": "#EAD2AC"}
    }
    
    # Day/Night
    diurno_votos = {
        "dia": details["real_day_night"]["dia"],
        "noite": details["real_day_night"]["noite"]
    }
    
    # Gender
    rg = details["real_gender"]
    fem = rg["feminino"]
    mais_fem = rg["mais_feminino"]
    uni = rg["unissex"]
    mais_masc = rg["mais_masculino"]
    masc = rg["masculino"]
    
    if fem == 0 and mais_fem == 0 and uni == 0 and mais_masc == 0 and masc == 0:
        classe_genero = "unissex"
    else:
        max_val = max(fem, mais_fem, uni, mais_masc, masc)
        if max_val == uni:
            classe_genero = "unissex"
        elif max_val == fem or max_val == mais_fem:
            classe_genero = "feminino"
        else:
            classe_genero = "masculino"
            
    percepcao_genero = {
        "feminino": fem,
        "mais_feminino": mais_fem,
        "unissex": uni,
        "mais_masculino": mais_masc,
        "masculino": masc,
        "classe_genero": classe_genero
    }
    
    # Longevity
    rl = details["real_longevity"]
    if rl["eterno"] == 0 and rl["longa_duracao"] == 0 and rl["moderada"] == 0 and rl["fraco"] == 0 and rl["muito_fraco"] == 0:
        longevidade_texto = "Moderada"
        longevidade_horas = "3 - 6 h"
    else:
        max_l = max(rl["eterno"], rl["longa_duracao"], rl["moderada"], rl["fraco"], rl["muito_fraco"])
        if max_l == rl["eterno"]:
            longevidade_texto = "Eterna"
            longevidade_horas = "10h+"
        elif max_l == rl["longa_duracao"]:
            longevidade_texto = "Longa Duração"
            longevidade_horas = "6 - 10 h"
        elif max_l == rl["moderada"]:
            longevidade_texto = "Moderada"
            longevidade_horas = "3 - 6 h"
        elif max_l == rl["fraco"]:
            longevidade_texto = "Fraco"
            longevidade_horas = "1 - 3 h"
        else:
            longevidade_texto = "Muito Fraco"
            longevidade_horas = "30 min - 1 h"
            
    # Sillage
    rs = details["real_sillage"]
    if rs["enorme"] == 0 and rs["forte"] == 0 and rs["moderada"] == 0 and rs["intimo"] == 0:
        rastro_texto = "Moderado"
    else:
        max_s = max(rs["enorme"], rs["forte"], rs["moderada"], rs["intimo"])
        if max_s == rs["enorme"]:
            rastro_texto = "Enorme"
        elif max_s == rs["forte"]:
            rastro_texto = "Marcante"
        elif max_s == rs["moderada"]:
            rastro_texto = "Moderado"
        else:
            rastro_texto = "Íntimo"
            
    return {
        "estacoes": estacoes_dict,
        "diurno_votos": diurno_votos,
        "percepcao_genero": percepcao_genero,
        "perfil_olfativo": {
            "longevidade_texto": longevidade_texto,
            "longevidade_horas": longevidade_horas,
            "rastro_texto": rastro_texto
        }
    }

def obter_concentracao(p_id, nome_perfume):
    EXTRAITS_CONHECIDOS = {
        "amouage_guidance_46",
        "amouage_interlude_53",
        "amouage_epic_56",
        "amouage_reflection_45",
        "amouage_dia_40",
        "amouage_jubilation_40",
        "amouage_honour_43",
        "byredo_vanille_antique"
    }
    if p_id in EXTRAITS_CONHECIDOS:
        return "Extrait de Parfum"
        
    nome_lower = nome_perfume.lower()
    if any(k in nome_lower for k in ["absolu", "extrait", "elixir", "concentre", "concentré"]):
        return "Extrait de Parfum"
        
    match_numero = re.search(r'\b(3[0-9]|4[0-9]|5[0-9]|6[0-9])\b', nome_lower)
    if match_numero:
        return "Extrait de Parfum"
        
    if "cologne" in nome_lower:
        return "Eau de Cologne"
    if "toilette" in nome_lower or " edt " in nome_lower or nome_lower.endswith(" edt"):
        return "Eau de Toilette"
        
    return "Eau de Parfum"

def obter_detalhes_perfumistas(perfumistas_nomes):
    detalhes = []
    perf_dir = os.path.join(VISCATEGORIA_DIR, "fotos", "perfumistas")
    os.makedirs(perf_dir, exist_ok=True)
    
    # Dicionário de cabeçalhos padrão para requisições urllib
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    context = ssl._create_unverified_context()
    
    for nome in perfumistas_nomes:
        if not nome or any(k in nome.lower() for k in ["perfumista", "membro", "exclusivo", "desconhecido"]):
            continue
            
        import unicodedata
        nfkd_form = unicodedata.normalize('NFKD', nome.lower().strip())
        slug = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "_", slug)
        local_name = f"{slug}.jpg"
        local_path = os.path.join(perf_dir, local_name)
        
        # 1. Se a foto já existe localmente, apenas adiciona e continua
        if os.path.exists(local_path):
            detalhes.append({
                "nome": nome,
                "foto": f"fotos/perfumistas/{local_name}"
            })
            continue
            
        # 2. Se não existe, tenta buscar a página do perfumista no Fragrantica para pegar a foto
        print(f"   [PERFUMISTA] Buscando foto para {nome} no Fragrantica...")
        url_perf = None
        # Tenta formatar URL direta (ex: https://www.fragrantica.com.br/narizes/Jerome_Epinette.html)
        nome_titulo = nome.title().replace(" ", "_")
        test_url = f"https://www.fragrantica.com.br/narizes/{nome_titulo}.html"
        try:
            req = urllib.request.Request(test_url, headers=headers)
            with urllib.request.urlopen(req, context=context, timeout=5) as response:
                if response.status == 200:
                    url_perf = test_url
        except Exception:
            pass
            
        # Se não deu na URL direta, busca no DuckDuckGo
        if not url_perf:
            query = f"site:fragrantica.com.br/narizes/ {nome}"
            encoded_query = urllib.parse.quote_plus(query)
            ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            try:
                req = urllib.request.Request(ddg_url, headers=headers)
                with urllib.request.urlopen(req, context=context, timeout=8) as response:
                    html = response.read().decode('utf-8', errors='replace')
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "")
                    if "fragrantica.com.br/narizes/" in href:
                        url_perf = href
                        break
            except Exception as e:
                print(f"      [AVISO] Erro ao buscar URL do perfumista no DuckDuckGo: {e}")
                
        # Se achou a URL da página do perfumista, acessa e baixa a foto principal
        if url_perf:
            try:
                print(f"   [PERFUMISTA] Acessando página do perfumista: {url_perf}")
                req = urllib.request.Request(url_perf, headers=headers)
                with urllib.request.urlopen(req, context=context, timeout=8) as response:
                    p_html = response.read().decode('utf-8', errors='replace')
                p_soup = BeautifulSoup(p_html, "html.parser")
                img_el = p_soup.find("img", src=re.compile(r"images/perfumer/|fimgs\.net/images/perfumer/"))
                if img_el:
                    img_url = img_el.get("src")
                    if img_url and img_url.startswith("http"):
                        req_img = urllib.request.Request(img_url, headers=headers)
                        with urllib.request.urlopen(req_img, context=context, timeout=8) as img_resp:
                            with open(local_path, "wb") as img_file:
                                img_file.write(img_resp.read())
                        print(f"      [OK] Foto do perfumista salva em {local_name}")
                        detalhes.append({
                            "nome": nome,
                            "foto": f"fotos/perfumistas/{local_name}"
                        })
                        continue
            except Exception as e:
                print(f"      [AVISO] Falha ao raspar foto do perfumista da página do Fragrantica: {e}")
                
        # Se tudo falhar, adicionamos sem foto (será usado o avatar padrão no HTML)
        detalhes.append({
            "nome": nome,
            "foto": None
        })
        
    return detalhes

def run_single(p_id, retries=3):
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"Banco de dados não encontrado em {JSON_PATH}")
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        database = json.load(f)
        
    perfumes_by_id = {p["id"]: p for p in database}
    if p_id not in perfumes_by_id:
        raise ValueError(f"Perfume com ID '{p_id}' não encontrado no banco de dados local.")
        
    perfume = perfumes_by_id[p_id]
    brand = perfume["marca"]
    name = perfume["nome"]
    
    url = URL_OVERRIDES.get(p_id)
    if not url:
        print(f"-> Buscando URL no DuckDuckGo para: {brand} {name}...")
        url = find_url_ddg(brand, name)
        if not url:
            raise ValueError(f"Não foi possível encontrar a URL do perfume '{brand} {name}' no Fragrantica.")
            
    details = None
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            # Sempre prioriza o Playwright para garantir votos e dados reais de JS
            if url:
                print(f"-> Acessando Fragrantica via Playwright para obter dados e votos reais (Tentativa {attempt}/{retries}): {url}...")
                details = scrape_perfume_playwright(url, brand, name)
                if not details:
                    print("   [AVISO] Playwright falhou, usando raspador urllib como fallback...")
                    details = fetch_and_parse_perfume(url, brand, name)
            else:
                print(f"-> Acessando Fragrantica via urllib (Tentativa {attempt}/{retries}): {url}...")
                details = fetch_and_parse_perfume(url, brand, name)
                
            if not details:
                raise ValueError("Falha ao raspar a página do Fragrantica.")
            break
        except Exception as e:
            last_error = e
            if attempt < retries:
                print(f"   [AVISO] Tentativa {attempt} falhou: {e}. Aguardando 2s para tentar novamente...")
                time.sleep(2)
            else:
                raise last_error
        
    # Mapeia/calcula percepções
    if details.get("scraped_via_playwright"):
        perceptions = map_playwright_perceptions(details)
    else:
        perceptions = calculate_olfactory_perceptions(details["acordes"], details["notes"], details["genero"])
        
    # Aplica override de perfumistas se aplicável
    if p_id in PERFUMISTA_OVERRIDES:
        details["perfumistas"] = PERFUMISTA_OVERRIDES[p_id]
        details["perfumistas_detalhes"] = []
        
    # Resgata fotos de perfumistas se não encontradas diretamente na página do perfume
    perfumistas_detalhes = details.get("perfumistas_detalhes", [])
    if (not perfumistas_detalhes or any(pd.get("nome") == "Perfumista" for pd in perfumistas_detalhes)) and details["perfumistas"]:
        perfumistas_detalhes = obter_detalhes_perfumistas(details["perfumistas"])
        
    # Se ainda estiver como "Perfumista" e tivermos uma lista com nomes válidos no details["perfumistas"]
    if details["perfumistas"] and not any(k in details["perfumistas"][0].lower() for k in ["perfumista", "membro", "exclusivo"]):
        # Garante que perfumistas está sincronizado com a lista de nomes válidos
        pass
    elif perfumistas_detalhes:
        details["perfumistas"] = [pd["nome"] for pd in perfumistas_detalhes]
    
    # Atualiza registro no JSON
    for idx, p in enumerate(database):
        if p["id"] == p_id:
            # Se existir imagem de composição no diretório fotos, prioriza-a
            composicao_file = f"{p_id}_composicao.png"
            if os.path.exists(os.path.join(VISCATEGORIA_DIR, "fotos", composicao_file)):
                frasco = composicao_file
            else:
                frasco = f"{p_id}_real.jpg"
            
            # Baixa/Atualiza a imagem do frasco se a URL estiver disponível
            if details.get("frasco_url"):
                img_dir = os.path.join(VISCATEGORIA_DIR, "fotos")
                os.makedirs(img_dir, exist_ok=True)
                img_path = os.path.join(img_dir, f"{p_id}_real.jpg")
                try:
                    print(f"   [DOWNLOAD] Baixando frasco real de {details['frasco_url']}...")
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
                    context = ssl._create_unverified_context()
                    req_img = urllib.request.Request(details["frasco_url"], headers=headers)
                    with urllib.request.urlopen(req_img, context=context, timeout=15) as img_resp:
                        with open(img_path, "wb") as f_img:
                            f_img.write(img_resp.read())
                    print("   [DOWNLOAD] Imagem do frasco atualizada com sucesso.")
                except Exception as e:
                    print(f"   [AVISO] Falha ao baixar imagem do frasco: {e}")
            
            slogan = p.get("slogan", "Sofisticado. Exclusivo. Marcante.")
            
            obj = {
                "id": p_id,
                "nome": details["nome"],
                "marca": details["marca"],
                "resenha_editorial": p.get("resenha_editorial"),
                "ocasioes_recomendadas": p.get("ocasioes_recomendadas"),
                "concentracao": obter_concentracao(p_id, details["nome"]),
                "genero_comercial": details["genero"],
                "familia_olfativa": details["familia"],
                "ano_lancamento": details["ano"],
                "perfumistas": details["perfumistas"],
                "perfumistas_detalhes": perfumistas_detalhes,
                "slogan": slogan,
                "nota_avaliacao": details["rating"],
                "votos_avaliacao": details["votes"],
                "frasco_imagem": frasco,
                "principais_acordes": details["acordes"],
                "perfil_olfativo": perceptions["perfil_olfativo"],
                "diurno_votos": perceptions["diurno_votos"],
                "percepcao_genero": perceptions["percepcao_genero"],
                "estacoes": perceptions["estacoes"],
                "notas": details["notes"],
                "adjetivos": p.get("adjetivos", [
                    "Qualidade Excepcional",
                    "Rastro Marcante e Elegante",
                    "Fixação Extrema na Pele",
                    "Toque de Luxo Inigualável"
                ])
            }
            database[idx] = obj
            break
            
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
        
    print(f"   [OK] Banco de dados updated para '{p_id}'!")
    
    # Chama o renderizador como subprocesso
    print(f"-> Chamando renderizador para '{p_id}'...")
    cmd = [sys.executable, RENDER_SCRIPT, "--perfume", p_id]
    subprocess.run(cmd, check=True)
    print(f"   [OK] Imagem do card regerada com sucesso!")


def run_batch(p_ids):
    success_count = 0
    errors = {}
    
    for idx, p_id in enumerate(p_ids):
        print(f"\n[{idx+1}/{len(p_ids)}] Processando: {p_id}...")
        try:
            run_single(p_id)
            success_count += 1
            if idx < len(p_ids) - 1:
                print("Aguardando 1 segundo para evitar limite de requisições...")
                time.sleep(1)
        except Exception as e:
            print(f"   [ERRO] Falha ao processar {p_id}: {e}")
            errors[p_id] = str(e)
            
    # Salvar log de erros/não encontrados em arquivo de texto
    error_log_path = os.path.join(WORKSPACE_DIR, "perfumes_nao_encontrados.txt")
    if errors:
        with open(error_log_path, "w", encoding="utf-8") as f_err:
            f_err.write("=== LOG DE PERFUMES NÃO ENCONTRADOS / COM ERRO DE PROCESSAMENTO ===\n\n")
            for pid, err in errors.items():
                f_err.write(f"Perfume ID: {pid}\nErro: {err}\n{'-'*50}\n")
        print(f"\n[AVISO] {len(errors)} perfume(s) falharam. Lista salva em: {error_log_path}")
    else:
        # Se todos derem certo, removemos o arquivo de erro antigo se existir
        if os.path.exists(error_log_path):
            try:
                os.remove(error_log_path)
            except OSError:
                pass
                
    print("\n" + "=" * 80)
    print(f"[FIM] Lote finalizado! Sucesso: {success_count}/{len(p_ids)}")
    if errors:
        print(f"\nSÍNTESE DOS ERROS ENCONTRADOS ({len(errors)}):")
        for failed_id, reason in errors.items():
            print(f" - Perfume: {failed_id}")
            print(f"   Motivo: {reason}")
        print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Skill 'trazfragrantica' - Busca dados do Fragrantica e gera cards de perfil.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    run_parser = subparsers.add_parser("run", help="Executa a extração e renderização.")
    run_parser.add_argument("--perfume", required=True, help="ID do perfume ou lista de IDs separados por vírgula.")
    
    status_parser = subparsers.add_parser("status", help="Verifica a situação de cores e dados no JSON.")
    status_parser.add_argument("--perfume", required=True, help="ID do perfume a ser verificado.")
    
    args = parser.parse_args()
    
    if args.command == "run":
        p_ids = [pid.strip() for pid in args.perfume.split(",") if pid.strip()]
        if len(p_ids) == 1:
            try:
                run_single(p_ids[0])
            except Exception as e:
                error_log_path = os.path.join(WORKSPACE_DIR, "perfumes_nao_encontrados.txt")
                with open(error_log_path, "w", encoding="utf-8") as f_err:
                    f_err.write("=== LOG DE PERFUMES NÃO ENCONTRADOS / COM ERRO DE PROCESSAMENTO ===\n\n")
                    f_err.write(f"Perfume ID: {p_ids[0]}\nErro: {e}\n{'-'*50}\n")
                print(f"[ERRO CRÍTICO] {e}. Log de erro salvo em: {error_log_path}")
                sys.exit(1)
        else:
            run_batch(p_ids)
            
    elif args.command == "status":
        p_id = args.perfume
        if not os.path.exists(JSON_PATH):
            print(f"[ERRO] Banco de dados não encontrado em: {JSON_PATH}")
            sys.exit(1)
            
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            database = json.load(f)
            
        perfume = next((p for p in database if p["id"] == p_id), None)
        if not perfume:
            print(f"[STATUS] Perfume '{p_id}' NÃO ENCONTRADO no banco de dados.")
            sys.exit(0)
            
        print(f"[STATUS] Perfume encontrado: {perfume['nome']} ({perfume['marca']})")
        print(f" - Avaliação: {perfume['nota_avaliacao']} ({perfume['votos_avaliacao']} votos)")
        
        default_colors = []
        custom_colors = []
        for a in perfume["principais_acordes"]:
            if a["cor"] == "#C5A880":
                default_colors.append(a["nome"])
            else:
                custom_colors.append(f"{a['nome']} ({a['cor']})")
                
        if default_colors:
            print(f" - Acordes com cor padrão (Dourada): {', '.join(default_colors)}")
        if custom_colors:
            print(f" - Acordes com cores personalizadas: {', '.join(custom_colors)}")
            
        if not default_colors:
            print(" - Diagnóstico: Cores dos acordes estão 100% atualizadas!")
        else:
            print(" - Diagnóstico: Necessário rodar a extração para obter as cores originais.")

if __name__ == "__main__":
    main()
