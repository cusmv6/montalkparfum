#!/usr/bin/env python3
import os
import sys
import re
import ssl
import json
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# Forçar a saída padrão (stdout) para UTF-8 no Windows para suportar caracteres acentuados e emojis
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Dicionário de URLs corretas para evitar buscas e erros de correspondência
URL_OVERRIDES = {
    "amouage_cristal_gold_man": "https://www.fragrantica.com.br/perfume/Amouage/Cristal-Gold-Man-88160.html",
    "amouage_cristal_gold_woman": "https://www.fragrantica.com.br/perfume/Amouage/Cristal-Gold-Woman-88159.html",
    "amouage_guidance_46": "https://www.fragrantica.com.br/perfume/Amouage/Guidance-46-94033.html",
    "amouage_guidance": "https://www.fragrantica.com.br/perfume/Amouage/Guidance-78656.html"
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
    text = re.sub(r'[^a-z0-9\s_-]', '', text)
    text = re.sub(r'[\s-]+', '_', text)
    return text.strip('_')

def validate_url(url, brand, name):
    url_lower = url.lower()
    
    brand_mappings = {
        "bvlgari le gemme": ["bvlgari"],
        "casamorati": ["casamorati", "xerjoff"],
        "chanel les exclusifs": ["chanel"],
        "christian louboutin": ["louboutin"],
        "clive christian": ["clive"],
        "frederic malle": ["malle", "frederic"],
        "maison crivelli": ["crivelli"],
        "maison francis kurkdjian": ["kurkdjian", "francis"],
        "parfums de marly": ["marly"],
        "penhaligon's": ["penhaligon"],
        "replica": ["replica", "margiela"],
        "roja parfums": ["roja"],
        "tom ford": ["tom-ford", "ford"],
    }
    
    brand_clean = brand.lower().strip()
    brand_tokens = brand_mappings.get(brand_clean, [brand_clean.split()[0]])
    
    brand_ok = any(bt in url_lower for bt in brand_tokens)
    if not brand_ok:
        return False
        
    name_clean = re.sub(r'[^a-z0-9\s]', '', name.lower())
    name_tokens = [t for t in name_clean.split() if len(t) > 2 and t not in ["man", "woman", "edp", "edt", "cologne", "absolu", "pour"]]
    
    if not name_tokens:
        name_tokens = [t for t in name_clean.split() if len(t) >= 2]
        
    matches = sum(1 for nt in name_tokens if nt in url_lower)
    
    if len(name_tokens) >= 2:
        return matches >= max(1, len(name_tokens) // 2)
    else:
        return matches >= 1

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
                actual_url = actual_url.split("?")[0]
                if validate_url(actual_url, brand, name):
                    return actual_url
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
        html_bytes = response.read()
        html = html_bytes.decode('utf-8', errors='replace')
        
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Rating e Votos
    rating = 4.25
    votes = 140
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
            
    # 3. Principais Acordes
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
    elif len(divs) > 0:
        all_notes = []
        for d in divs:
            all_notes.extend([a.text.strip() for a in d.find_all(class_='pyramid-note-label') if a.text.strip()])
        if all_notes:
            topo_notes = all_notes[:max(1, len(all_notes)//3)]
            coracao_notes = all_notes[len(topo_notes):len(topo_notes)+(len(all_notes)//3)]
            base_notes = all_notes[len(topo_notes)+len(coracao_notes):]
            
    if not topo_notes and not coracao_notes and not base_notes:
        all_links = soup.find_all("a", href=re.compile(r"/notas/"))
        gen_notes = [lk.text.strip() for lk in all_links if lk.text.strip() and lk.text.strip().lower() != "notas"]
        if gen_notes:
            topo_notes = gen_notes[:max(2, len(gen_notes)//3)]
            coracao_notes = gen_notes[len(topo_notes):len(topo_notes)+(len(gen_notes)//3)]
            base_notes = gen_notes[len(topo_notes)+len(coracao_notes):]
            
    # 5. Descrição Metadados (Ano, Perfumista, Gênero e Família)
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
            
        perf_match = re.search(r'criado por ([^.]+)\.', desc)
        if perf_match:
            perf_text = perf_match.group(1)
            names = re.split(r'\s+e\s+|,', perf_text)
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
    if not perfumistas:
        perfumistas = ["Perfumista de Nicho"]
        
    # 6. Perfumistas com foto
    perfumistas_detalhes = []
    for h3 in soup.find_all("h3"):
        if h3.text.strip() == "Perfumista":
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        perf_dir = os.path.join(current_dir, "fotos", "perfumistas")
        os.makedirs(perf_dir, exist_ok=True)
        
        for pd in perfumistas_detalhes:
            if pd["foto"] and pd["foto"].startswith("http"):
                # slugify helper
                slug = pd["nome"].lower().strip()
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
        "ano": ano_lancamento,
        "perfumistas": perfumistas,
        "perfumistas_detalhes": perfumistas_detalhes,
        "genero": genero_comercial,
        "familia": familia_olfativa
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
                perf_match = re.search(r'criado por ([^.]+)\.|created by ([^.]+)\.', desc, re.I)
                if perf_match:
                    perf_text = perf_match.group(1) or perf_match.group(2)
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
                if h3.text.strip() == "Perfumista":
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
                current_dir = os.path.dirname(os.path.abspath(__file__))
                perf_dir = os.path.join(current_dir, "fotos", "perfumistas")
                os.makedirs(perf_dir, exist_ok=True)
                
                import ssl
                import urllib.request
                dl_context = ssl._create_unverified_context()
                dl_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                }
                
                for pd in perfumistas_detalhes:
                    if pd["foto"] and pd["foto"].startswith("http"):
                        slug = pd["nome"].lower().strip()
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

def calculate_olfactory_perceptions(acordes, notes, gender_desc):
    acordes_nomes = [a["nome"].lower() for a in acordes]
    
    inverno = 100
    primavera = 100
    verao = 100
    outono = 100
    
    frescos = ["cítrico", "citrico", "fresco", "verde", "ozônico", "marinho", "floral", "aromático", "aromatico"]
    quentes = ["baunilha", "doce", "âmbar", "ambar", "amadeirado", "especiado quente", "couro", "tabaco", "especiado", "mel", "oud", "conhaque"]
    
    for a in acordes_nomes:
        if any(f in a for f in frescos):
            verao += 180
            primavera += 130
        if any(q in a for q in quentes):
            inverno += 180
            outono += 130
            
    estacoes_dict = {
        "inverno": {"votos": inverno, "cor": "#D4F0FC"},
        "primavera": {"votos": primavera, "cor": "#A3D977"},
        "verao": {"votos": verao, "cor": "#FFA07A"},
        "outono": {"votos": outono, "cor": "#EAD2AC"}
    }
    
    dia = 100
    noite = 100
    for a in acordes_nomes:
        if any(f in a for f in frescos):
            dia += 140
        if any(q in a for q in quentes):
            noite += 160
            
    diurno_votos = {"dia": dia, "noite": noite}
    
    fem = 20
    mais_fem = 10
    uni = 300
    mais_masc = 20
    masc = 20
    
    gen_lower = gender_desc.lower()
    if "masculino" in gen_lower:
        masc = 240
        mais_masc = 130
        uni = 50
    elif "feminino" in gen_lower:
        fem = 240
        mais_fem = 130
        uni = 50
        
    percepcao_genero = {
        "feminino": fem,
        "mais_feminino": mais_fem,
        "unissex": uni,
        "mais_masculino": mais_masc,
        "masculino": masc,
        "classe_genero": "unissex" if uni >= max(fem, masc) else ("masculino" if masc > fem else "feminino")
    }
    
    longevidade_texto = "Moderada"
    longevidade_horas = "3 - 6 h"
    rastro_texto = "Moderado"
    
    if any(q in acordes_nomes for q in ["amadeirado", "baunilha", "doce", "âmbar", "couro", "mel"]):
        longevidade_texto = "Longa Duração"
        longevidade_horas = "6 - 10 h"
        rastro_texto = "Marcante"
    if any(q in acordes_nomes for q in ["oud", "tabaco", "incensado"]):
        longevidade_texto = "Eterna"
        longevidade_horas = "10h+"
        rastro_texto = "Enorme"
        
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

def read_catalogo_perfumes(catalogo_path):
    perfumes_list = []
    if not os.path.exists(catalogo_path):
        return perfumes_list
        
    with open(catalogo_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    matches = re.findall(r'\|\s*\d+\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', content)
    for brand, name in matches:
        brand = brand.strip()
        name = name.strip()
        if "marca" in brand.lower() or "---" in brand:
            continue
        perfumes_list.append((brand, name))
    return perfumes_list

def run_auditor(test_mode=False, force_all=False):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    catalogo_path = r"C:\Users\odeao\OneDrive\Desktop\brem\PROJETOS\Bruno\Decante\catalogo_perfumes.md"
    json_path = os.path.join(current_dir, "perfumes_data.json")
    fotos_dir = os.path.join(current_dir, "fotos")
    
    if not os.path.exists(fotos_dir):
        os.makedirs(fotos_dir)
        
    print("[1] Lendo catálogo de perfumes...")
    perfumes_list = read_catalogo_perfumes(catalogo_path)
    if test_mode:
        perfumes_list = [p for p in perfumes_list if "cristal" in p[1].lower() and "man" in p[1].lower()]
        print(f"[TESTE] Executando teste apenas para {len(perfumes_list)} perfume(s): {perfumes_list}")
        
    total = len(perfumes_list)
    print(f"[CATÁLOGO] Total de {total} perfumes para validar.")
    
    # Carregar banco de dados existente
    existing_data = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass
            
    existing_by_id = {p["id"]: p for p in existing_data}
    final_data = []
    
    print("\n[INICIANDO VISTORIA E CORREÇÃO SEM BROWSER]")
    print("=" * 80)
    
    corrected_count = 0
    skipped_count = 0
    errors = {}
    
    for idx, (brand, name) in enumerate(perfumes_list):
        p_id = slugify(f"{brand}_{name}")
        if p_id == "nishane__100":
            p_id = "nishane_hundred_silent_ways"
            
        print(f"[{idx+1}/{total}] Auditando: {name} ({brand})...")
        
        # Modo inteligente de cache/pulo de busca
        url = URL_OVERRIDES.get(p_id)
        
        # Se não estiver nos overrides e não for forçado, e já tiver dados reais no JSON, aproveita o existente
        if not url and not force_all and p_id in existing_by_id:
            old_item = existing_by_id[p_id]
            # Verifica se não é um registro que sabemos estar quebrado (ex: Cristal & Gold Man com 140 votos)
            if old_item.get("votos_avaliacao") != 140 and old_item.get("frasco_imagem") != "imperium_real.jpg":
                print("   [CACHED] Perfume com dados locais válidos. Mantendo do banco atual.")
                final_data.append(old_item)
                skipped_count += 1
                continue
        
        # Se precisamos buscar o URL e não temos override
        if not url:
            # Sleep extra para evitar rate limiting nas buscas
            time.sleep(3.0)
            url = find_url_ddg(brand, name)
        
        if not url:
            print(f"   [AVISO] URL não encontrada para {name} ({brand}).")
            if p_id in existing_by_id:
                print("   [MANTER] Mantendo dados anteriores existentes.")
                final_data.append(existing_by_id[p_id])
            continue
            
        print(f"   [URL RESOLVIDA] {url}")
        
        # Delay de 2.0 segundos entre requisições de página
        time.sleep(2.0)
        
        try:
            if p_id in URL_OVERRIDES:
                print("   [OVERRIDE] Usando raspador Playwright para obter dados e votos reais...")
                details = scrape_perfume_playwright(url, brand, name)
                if not details:
                    print("   [AVISO] Playwright falhou, usando raspador urllib como fallback...")
                    details = fetch_and_parse_perfume(url, brand, name)
            else:
                details = fetch_and_parse_perfume(url, brand, name)
            
            # Verificar imagem local
            frasco_local = f"{p_id}_real.jpg"
            img_path = os.path.join(fotos_dir, frasco_local)
            
            img_errada = False
            if p_id in URL_OVERRIDES:
                img_errada = True
            elif p_id in existing_by_id:
                old_img = existing_by_id[p_id].get("frasco_imagem", "")
                if old_img == "imperium_real.jpg":
                    img_errada = True
            
            download_needed = not os.path.exists(img_path) or img_errada
            
            if download_needed and details["frasco_url"]:
                try:
                    print(f"   [DOWNLOAD] Baixando frasco real: {details['frasco_url']}")
                    context = ssl._create_unverified_context()
                    req_img = urllib.request.Request(details["frasco_url"], headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_img, context=context, timeout=10) as img_resp:
                        with open(img_path, "wb") as f_img:
                            f_img.write(img_resp.read())
                    print("   [IMAGEM SALVA] Imagem local atualizada com sucesso.")
                    frasco_local = f"{p_id}_real.jpg"
                except Exception as e:
                    print(f"   [AVISO] Erro ao baixar imagem: {e}")
                    frasco_local = existing_by_id[p_id].get("frasco_imagem", "imperium_real.jpg") if p_id in existing_by_id else "imperium_real.jpg"
            else:
                if os.path.exists(img_path):
                    frasco_local = f"{p_id}_real.jpg"
                else:
                    frasco_local = "imperium_real.jpg"
            
            if details.get("scraped_via_playwright"):
                perceptions = map_playwright_perceptions(details)
            else:
                perceptions = calculate_olfactory_perceptions(details["acordes"], details["notes"], details["genero"])
            
            slogans = [
                "Sofisticado. Exclusivo. Marcante.",
                "Uma assinatura olfativa única de luxo.",
                "Elegância engarrafada para momentos especiais.",
                "A expressão máxima da perfumaria artística."
            ]
            slogan = slogans[idx % len(slogans)]
            
            obj = {
                "id": p_id,
                "nome": details["nome"],
                "marca": details["marca"],
                "concentracao": "Extrait de Parfum" if any(k in details["nome"].lower() for k in ["absolu", "40", "extrait", "53", "45"]) else "Eau de Parfum",
                "genero_comercial": details["genero"],
                "familia_olfativa": details["familia"],
                "ano_lancamento": details["ano"],
                "perfumistas": details["perfumistas"],
                "perfumistas_detalhes": details.get("perfumistas_detalhes", []),
                "slogan": slogan,
                "nota_avaliacao": details["rating"],
                "votos_avaliacao": details["votes"],
                "frasco_imagem": frasco_local,
                "principais_acordes": details["acordes"],
                "perfil_olfativo": perceptions["perfil_olfativo"],
                "diurno_votos": perceptions["diurno_votos"],
                "percepcao_genero": perceptions["percepcao_genero"],
                "estacoes": perceptions["estacoes"],
                "notas": details["notes"],
                "adjetivos": [
                    "Qualidade Excepcional",
                    "Rastro Marcante e Elegante",
                    "Fixação Extrema na Pele",
                    "Toque de Luxo Inigualável"
                ]
            }
            
            if p_id in existing_by_id:
                old_votes = existing_by_id[p_id].get("votos_avaliacao", 0)
                old_rating = existing_by_id[p_id].get("nota_avaliacao", 0)
                if abs(old_votes - details["votes"]) > 1 or abs(old_rating - details["rating"]) > 0.05 or img_errada:
                    corrected_count += 1
                    print(f"   [CORRIGIDO] Dados atualizados (Rating: {old_rating} -> {details['rating']}, Votos: {old_votes} -> {details['votes']})")
                else:
                    skipped_count += 1
                    print("   [OK] Dados já estavam corretos.")
            else:
                corrected_count += 1
                print("   [NOVO] Perfume adicionado ao banco.")
                
            final_data.append(obj)
            
        except Exception as e:
            print(f"   [ERRO] Falha ao processar {name}: {e}")
            errors[p_id] = str(e)
            if p_id in existing_by_id:
                final_data.append(existing_by_id[p_id])
                
    if not test_mode:
        all_final_ids = {p["id"] for p in final_data}
        for old_id, old_perfume in existing_by_id.items():
            if old_id not in all_final_ids:
                final_data.append(old_perfume)
                
        # Salvar log de erros/não encontrados em arquivo de texto
        workspace_dir = r"C:\Users\odeao\OneDrive\Desktop\brem"
        error_log_path = os.path.join(workspace_dir, "perfumes_nao_encontrados.txt")
        if errors:
            with open(error_log_path, "w", encoding="utf-8") as f_err:
                f_err.write("=== LOG DE PERFUMES NÃO ENCONTRADOS / COM ERRO DE PROCESSAMENTO ===\n\n")
                for pid, err in errors.items():
                    f_err.write(f"Perfume ID: {pid}\nErro: {err}\n{'-'*50}\n")
            print(f"\n[AVISO] {len(errors)} perfume(s) falharam. Lista salva em: {error_log_path}")
        else:
            if os.path.exists(error_log_path):
                try:
                    os.remove(error_log_path)
                except OSError:
                    pass
                    
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
            
        print("=" * 80)
        print(f"[FIM] Vistoria concluída! {corrected_count} perfumes corrigidos/atualizados, {skipped_count} mantidos.")
        print(f"Banco de dados salvo em: {json_path}")
    else:
        print("=" * 80)
        print("[TESTE] Resultado da extração:")
        print(json.dumps(final_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test = "--test" in sys.argv
    all_mode = "--all" in sys.argv
    run_auditor(test_mode=test, force_all=all_mode)
