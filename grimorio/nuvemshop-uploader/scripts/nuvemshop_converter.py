#!/usr/bin/env python3
import os
import sys
import csv
import re
import json
import argparse

# Import find_competitor_price from preco.py
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "preco", "scripts"))
    from preco import find_competitor_price
except ImportError:
    find_competitor_price = None

# Force stdout to UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def slugify(text):
    text = text.lower()
    # Substituir caracteres acentuados
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ã': 'a', 'õ': 'o', 'ç': 'c', 'ñ': 'n',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Remover caracteres especiais
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Substituir múltiplos espaços ou hifens por um único hífen
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def parse_markdown_table(file_path):
    perfumes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Procurar por linhas de tabela markdown (com colunas de custo opcionais)
        # Ex: | 57 | Nishane | Hacivat | 3746 | 500 | 100 |
        table_pattern = re.compile(r'^\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|(?:\s*([^|]*)\s*\|)?(?:\s*([^|]*)\s*\|)?(?:\s*([^|]*)\s*\|)?')
        for line in lines:
            match = table_pattern.match(line)
            if match:
                groups = match.groups()
                brand = groups[1].strip()
                name = groups[2].strip()
                # Pular o cabeçalho
                if 'marca' in brand.lower() or '---' in brand:
                    continue
                
                perfume = {
                    "brand": brand,
                    "name": name,
                    "volumes": {
                        "2ml": {"price": "", "cost": "", "stock": ""},
                        "5ml": {"price": "", "cost": "", "stock": ""},
                        "10ml": {"price": "", "cost": "", "stock": ""}
                    }
                }
                
                # Extrair colunas opcionais se fornecidas na tabela
                if len(groups) >= 6:
                    if groups[3] is not None and groups[3].strip():
                        try:
                            perfume["price_br"] = float(re.sub(r'[^\d\.,]', '', groups[3]).replace(',', '.'))
                        except ValueError:
                            pass
                    if groups[4] is not None and groups[4].strip():
                        try:
                            perfume["price_cn"] = float(re.sub(r'[^\d\.,]', '', groups[4]).replace(',', '.'))
                        except ValueError:
                            pass
                    if groups[5] is not None and groups[5].strip():
                        try:
                            perfume["volume_full"] = float(re.sub(r'[^\d\.,]', '', groups[5]).replace(',', '.'))
                        except ValueError:
                            pass
                            
                perfumes.append(perfume)
    except Exception as e:
        print(f"Erro ao ler tabela Markdown: {e}", file=sys.stderr)
    return perfumes

def parse_structured_text(file_path):
    perfumes = []
    current_perfume = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            # Divisor de perfumes ou início de novo bloco
            if line_str == "---" or line_str.startswith("==="):
                if current_perfume:
                    perfumes.append(current_perfume)
                    current_perfume = None
                continue
                
            # Chaves/Valores
            if ":" in line_str:
                key, val = line_str.split(":", 1)
                key = key.strip().lower()
                val = val.strip()
                
                if key in ["marca", "brand"]:
                    if current_perfume is None:
                        current_perfume = {
                            "brand": val, "name": "",
                            "price_br": None, "price_cn": None, "volume_full": None,
                            "volumes": {
                                "2ml": {"price": "", "cost": "", "stock": ""},
                                "5ml": {"price": "", "cost": "", "stock": ""},
                                "10ml": {"price": "", "cost": "", "stock": ""}
                            }
                        }
                    else:
                        if current_perfume["name"]: # Se já tiver nome e veio marca nova, salva o anterior
                            perfumes.append(current_perfume)
                            current_perfume = {
                                "brand": val, "name": "",
                                "price_br": None, "price_cn": None, "volume_full": None,
                                "volumes": {
                                    "2ml": {"price": "", "cost": "", "stock": ""},
                                    "5ml": {"price": "", "cost": "", "stock": ""},
                                    "10ml": {"price": "", "cost": "", "stock": ""}
                                }
                            }
                        else:
                            current_perfume["brand"] = val
                            
                elif key in ["nome", "name"]:
                    if current_perfume is None:
                        current_perfume = {
                            "brand": "Importado", "name": val,
                            "price_br": None, "price_cn": None, "volume_full": None,
                            "volumes": {
                                "2ml": {"price": "", "cost": "", "stock": ""},
                                "5ml": {"price": "", "cost": "", "stock": ""},
                                "10ml": {"price": "", "cost": "", "stock": ""}
                            }
                        }
                    else:
                        current_perfume["name"] = val
                
                elif "brasil" in key or "br_price" in key or "price_br" in key or "referencia" in key:
                    if current_perfume:
                        clean_val = re.sub(r'[^\d\.,]', '', val).replace(',', '.')
                        current_perfume["price_br"] = float(clean_val)
                        
                elif "china" in key or "cn_price" in key or "price_cn" in key or "custo_frasco" in key or "custo frasco" in key:
                    if current_perfume:
                        clean_val = re.sub(r'[^\d\.,]', '', val).replace(',', '.')
                        current_perfume["price_cn"] = float(clean_val)
                        
                elif "volume frasco" in key or "volume_frasco" in key or "volume cheio" in key or "volume_cheio" in key or "volume_full" in key or "volume_total" in key:
                    if current_perfume:
                        clean_val = re.sub(r'[^\d\.,]', '', val).replace(',', '.')
                        current_perfume["volume_full"] = float(clean_val)
                        
                elif "preço" in key or "preco" in key or "price" in key:
                    # Extrair volume (ex: preco 2ml: 45.00)
                    vol_match = re.search(r'(\d+ml|\d+\s*ml)', key)
                    if vol_match and current_perfume:
                        vol_key = vol_match.group(1).replace(" ", "")
                        if vol_key not in current_perfume["volumes"]:
                            current_perfume["volumes"][vol_key] = {"price": "", "cost": "", "stock": ""}
                        current_perfume["volumes"][vol_key]["price"] = val.replace("R$", "").strip()
                        
                elif "custo" in key or "cost" in key:
                    vol_match = re.search(r'(\d+ml|\d+\s*ml)', key)
                    if vol_match and current_perfume:
                        vol_key = vol_match.group(1).replace(" ", "")
                        if vol_key not in current_perfume["volumes"]:
                            current_perfume["volumes"][vol_key] = {"price": "", "cost": "", "stock": ""}
                        current_perfume["volumes"][vol_key]["cost"] = val.replace("R$", "").strip()
                        
                elif "estoque" in key or "stock" in key:
                    vol_match = re.search(r'(\d+ml|\d+\s*ml)', key)
                    if vol_match and current_perfume:
                        vol_key = vol_match.group(1).replace(" ", "")
                        if vol_key not in current_perfume["volumes"]:
                            current_perfume["volumes"][vol_key] = {"price": "", "cost": "", "stock": ""}
                        current_perfume["volumes"][vol_key]["stock"] = val
                    elif current_perfume:
                        # Se for estoque sem volumetria, aplica para todos
                        for v in current_perfume["volumes"]:
                            current_perfume["volumes"][v]["stock"] = val
        if current_perfume:
            perfumes.append(current_perfume)
    except Exception as e:
        print(f"Erro ao ler texto estruturado: {e}", file=sys.stderr)
    return perfumes

def generate_csv(perfumes, output_path, default_prices=None, default_costs=None, default_stock="5"):
    headers = [
        "Identificador URL", "Nome", "Categorias", 
        "Nome da variação 1", "Valor da variação 1", 
        "Nome da variação 2", "Valor da variação 2", 
        "Nome da variação 3", "Valor da variação 3", 
        "Preço", "Preço promocional", 
        "Peso (kg)", "Altura (cm)", "Largura (cm)", "Comprimento (cm)", 
        "Estoque", "SKU", "Código de barras", 
        "Exibir na loja", "Frete gratis", "Descrição", "Tags", 
        "Título para SEO", "Descrição para SEO", "Marca", 
        "Produto Físico", "MPN (Cód. Exclusivo Modelo Fabricante)", 
        "Sexo", "Faixa etária", "Custo"
    ]
    
    if default_prices is None:
        default_prices = {"2ml": "50.00", "5ml": "100.00", "10ml": "180.00"}
    if default_costs is None:
        default_costs = {"2ml": "", "5ml": "", "10ml": ""}
        
    # Dimensões e pesos padrão de decantes
    specs = {
        "2ml": {"weight": "0.02", "height": "2", "width": "11", "length": "16"},
        "5ml": {"weight": "0.03", "height": "3", "width": "11", "length": "16"},
        "10ml": {"weight": "0.05", "height": "5", "width": "11", "length": "16"}
    }
    
    # Carregar dados ricos do Fragrantica para descrições dinâmicas
    rich_data_path = r"C:\Users\odeao\OneDrive\Desktop\brem\PROJETOS\Bruno\produtos\catalogo.json"
    rich_perfumes = {}
    if os.path.exists(rich_data_path):
        try:
            with open(rich_data_path, "r", encoding="utf-8") as f_rich:
                data_list = json.load(f_rich)
                for item in data_list:
                    key = f"{item['marca'].lower().strip()}:{item['nome'].lower().strip()}"
                    rich_perfumes[key] = item
            print(f"[INFO Nuvemshop] Carregados dados ricos de {len(rich_perfumes)} perfumes para descrições dinâmicas.")
        except Exception as e:
            print(f"[Aviso] Erro ao ler perfumes_data.json: {e}", file=sys.stderr)

    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            
            for p in perfumes:
                brand = p["brand"]
                name = p["name"]
                
                # Slugify
                slug_brand = slugify(brand)
                slug_name = slugify(name)
                url_identifier = f"decante-{slug_brand}-{slug_name}"
                
                prod_name = f"Decante {name} - {brand}"
                categories = f"Decantes > {brand}"
                
                # Procurar dados ricos do Fragrantica no JSON carregado
                search_key = f"{brand.lower().strip()}:{name.lower().strip()}"
                rich_info = rich_perfumes.get(search_key)
                
                if rich_info:
                    perfumistas_list = [pd["nome"] for pd in rich_info.get("perfumistas_detalhes", [])]
                    if not perfumistas_list:
                        perfumistas_list = rich_info.get("perfumistas", [])
                    if len(perfumistas_list) > 1:
                        perfumistas_str = ", ".join(perfumistas_list[:-1]) + " e " + perfumistas_list[-1]
                        perf_qualifier = "Os perfumistas"
                        perf_verb = "assinam"
                        perf_pronoun = "são"
                    elif len(perfumistas_list) == 1:
                        perfumistas_str = perfumistas_list[0]
                        perf_qualifier = "O perfumista"
                        perf_verb = "assina"
                        perf_pronoun = "é"
                    else:
                        perfumistas_str = "um perfumista exclusivo"
                        perf_qualifier = "O perfumista"
                        perf_verb = "assina"
                        perf_pronoun = "é"
                        
                    topo_notes_italic = [f"<em>{n}</em>" for n in rich_info["notas"]["topo"]]
                    if len(topo_notes_italic) > 1:
                        topo_str = ", ".join(topo_notes_italic[:-1]) + " e " + topo_notes_italic[-1]
                    else:
                        topo_str = topo_notes_italic[0]
                        
                    coracao_notes_italic = [f"<em>{n}</em>" for n in rich_info["notas"]["coracao"]]
                    if len(coracao_notes_italic) > 1:
                        coracao_str = ", ".join(coracao_notes_italic[:-1]) + " e " + coracao_notes_italic[-1]
                    else:
                        coracao_str = coracao_notes_italic[0]
                        
                    base_notes_italic = [f"<em>{n}</em>" for n in rich_info["notas"]["base"]]
                    if len(base_notes_italic) > 1:
                        base_str = ", ".join(base_notes_italic[:-1]) + " e " + base_notes_italic[-1]
                    else:
                        base_str = base_notes_italic[0]
                        
                    fam_gen = f"{rich_info.get('familia_olfativa', 'Exclusivo')} {rich_info.get('genero_comercial', 'Compartilhável')}"
                    
                    resenha = rich_info.get("resenha_editorial")
                    ocasioes = rich_info.get("ocasioes_recomendadas")
                    
                    editorial_block = ""
                    if resenha and ocasioes:
                        editorial_block = (
                            f"<div style=\"background: #FAF9F6; padding: 22px; border-radius: 0 8px 8px 0; border-left: 4px solid #C5A880; margin-top: 15px; margin-bottom: 25px;\">"
                            f"<div style=\"font-family: 'Playfair Display', Georgia, serif; font-size: 17.5px; font-style: italic; font-weight: 600; color: #1A3B32; margin-bottom: 3px;\">\"A perspectiva de ÇaFleureBon...</div>"
                            f"<div style=\"font-family: 'Inter', sans-serif; font-size: 9px; text-transform: uppercase; letter-spacing: 0.8px; color: #7E786B; margin-bottom: 3px;\">PERSPECTIVA EDITORIAL DO BLOG CRÍTICO MAIS PREMIADO DA PERFUMARIA DE NICHO</div>"
                            f"<div style=\"font-family: 'Inter', sans-serif; font-size: 7.5px; font-style: italic; text-transform: uppercase; letter-spacing: 0.8px; color: #7E786B; opacity: 0.85; margin-bottom: 14px;\">(PERFUMED PLUME AWARDS, FRAGRANCE FOUNDATION AWARDS - FIFI, BASENOTES READER'S AWARDS)</div>"
                            f"<div style=\"font-style: italic; color: #4A4439; font-size: 13.5px; line-height: 1.75; margin-bottom: 15px;\">{resenha}</div>"
                            f"<div style=\"border-top: 1px solid #EAE6DB; padding-top: 12px; font-size: 13px; line-height: 1.6; color: #333333;\">"
                            f"<strong style=\"font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-size: 14.5px; color: #1A3B32; font-weight: 600;\">Ocasiões Recomendadas:</strong> <em>{ocasioes}<span style=\"font-family: 'Playfair Display', Georgia, serif; font-style: italic; font-weight: 600; font-size: 17.5px; color: #1A3B32; margin-left: 3px;\">\"</span></em>"
                            f"</div>"
                            f"</div>"
                        )
                    
                    description = (
                        f"<p><strong>{rich_info['nome']}</strong> de <strong>{rich_info['marca']}</strong> é um perfume <em>{fam_gen}</em> lançado em <strong>{rich_info.get('ano_lancamento', '2020')}</strong>. "
                        f"<em>{perf_qualifier}</em> que {perf_verb} esta fragrância {perf_pronoun} <strong>{perfumistas_str}</strong>.</p>"
                        f"{editorial_block}"
                        f"<div style=\"margin-top: 16px; margin-bottom: 25px; display: flex; flex-direction: column; gap: 10px; font-size: 14.5px; line-height: 1.7;\">"
                        f"<div style=\"position: relative; padding-left: 20px;\"><span style=\"color: #C5A880; font-weight: bold; font-size: 18px; position: absolute; left: 0; top: -1px;\">•</span><strong>Notas de Saída (5 a 15 min):</strong> {topo_str}</div>"
                        f"<div style=\"position: relative; padding-left: 20px;\"><span style=\"color: #C5A880; font-weight: bold; font-size: 18px; position: absolute; left: 0; top: -1px;\">•</span><strong>Notas de Corpo (2 a 6 h):</strong> {coracao_str}</div>"
                        f"<div style=\"position: relative; padding-left: 20px;\"><span style=\"color: #C5A880; font-weight: bold; font-size: 18px; position: absolute; left: 0; top: -1px;\">•</span><strong>Notas de Fundo (6 a 12h+):</strong> {base_str}</div>"
                        f"</div>"
                        f"<p style=\"font-family: 'Inter', sans-serif; font-style: italic; font-size: 12.5px; color: #7E786B; border-left: 1.5px solid #C5A880; padding-left: 16px; margin-top: 25px; line-height: 1.7; letter-spacing: 0.15px;\">"
                        f"Os decantes são uma excelente oportunidade para conhecer e testar fragrâncias exclusivas "
                        f"antes de investir em um frasco cheio. Nossos decantes são fracionados de forma profissional "
                        f"diretamente do frasco original em porta-perfumes de vidro com borrifador.</p>"
                    )
                else:
                    description = (
                        f"<p>Decante do perfume de nicho <strong>{name}</strong> da grife <strong>{brand}</strong>.</p>"
                        f"<p>Os decantes são uma excelente oportunidade para conhecer e testar fragrâncias exclusivas "
                        f"antes de investir em um frasco cheio. Nossos decantes são fracionados de forma profissional "
                        f"diretamente do frasco original em porta-perfumes de vidro com borrifador.</p>"
                    )
                    
                tags = f"decante, {brand}, {name}, importado, perfume"
                seo_title = f"Decante {name} - {brand} | Original Montalk"
                seo_desc = f"Compre decante original de {name} - {brand} fracionado em 2ml, 5ml ou 10ml na Montalk. Envio rápido para todo o Brasil."
                
                # Preços dinâmicos baseados na fórmula
                price_br = p.get("price_br")
                price_cn = p.get("price_cn")
                volume_full = p.get("volume_full")
                
                calculated_prices = {}
                calculated_costs = {}
                
                if price_br is not None and price_cn is not None and volume_full:
                    p_br = max(price_br, price_cn)
                    p_cn = min(price_br, price_cn)
                    
                    # 1. Valor Base Ponderado (8/2)
                    weighted_value = ((p_br * 8) + (p_cn * 2)) / 10.0
                    cost_per_ml = weighted_value / volume_full
                    cost_cn_per_ml = p_cn / volume_full
                    
                    # Calcular primeiro o preço de venda de 10ml (Âncora)
                    sell_price_10ml = (cost_per_ml * 10.0 * 1.07) + 30.00
                    
                    if find_competitor_price:
                        comp_info = find_competitor_price(name)
                        if comp_info:
                            p_king = comp_info["sell_price"]
                            limit_price_10ml = p_king * 0.84 # Pelo menos 16% mais barato
                            if sell_price_10ml > limit_price_10ml:
                                sell_price_10ml = limit_price_10ml
                                
                    # Arredondar preço âncora de 10ml para o par mais próximo
                    sell_price_10ml = float(int(sell_price_10ml / 2 + 0.5) * 2)
                    
                    for vol_str in ["2ml", "5ml", "10ml"]:
                        vol_ml = float(vol_str.replace("ml", ""))
                        
                        # Preço de Venda ancorado na proporção 50:100:180 com arredondamento para o par mais próximo
                        if vol_str == "10ml":
                            sell_price = sell_price_10ml
                        elif vol_str == "5ml":
                            sell_price = float(int((sell_price_10ml * (100.0 / 180.0)) / 2 + 0.5) * 2)
                        elif vol_str == "2ml":
                            sell_price = float(int((sell_price_10ml * (50.0 / 180.0)) / 2 + 0.5) * 2)
                        else:
                            sell_price = float(int((sell_price_10ml * (vol_ml / 10.0)) / 2 + 0.5) * 2)
                            
                        calculated_prices[vol_str] = f"{sell_price:.2f}"
                        
                        # Custo Real para o Bruno (calculado linearmente)
                        cost_price = (cost_cn_per_ml * vol_ml) + 30.00
                        calculated_costs[vol_str] = f"{cost_price:.2f}"
                
                is_first_row = True
                
                # Gerar linhas para cada volumetria
                for vol in ["2ml", "5ml", "10ml"]:
                    vol_data = p["volumes"].get(vol, {"price": "", "cost": "", "stock": ""})
                    
                    # Preço final
                    price = vol_data.get("price") or calculated_prices.get(vol) or default_prices.get(vol, "")
                    if not price:
                        price = "0.00"
                        
                    # Preço de custo
                    cost = vol_data.get("cost") or calculated_costs.get(vol) or default_costs.get(vol, "")
                    
                    # Estoque
                    stock = vol_data.get("stock") or default_stock
                    
                    # SKU
                    sku_clean_brand = slug_brand.upper()[:4]
                    sku_clean_name = slug_name.replace("-", "")[:12].upper()
                    sku = f"DEC-{sku_clean_brand}-{sku_clean_name}-{vol.upper()}"
                    
                    # Especificações físicas
                    vol_specs = specs.get(vol, {"weight": "0.05", "height": "5", "width": "11", "length": "16"})
                    
                    # Montar a linha
                    row = [
                        url_identifier,
                        prod_name if is_first_row else "",
                        categories if is_first_row else "",
                        "Volumetria", # Nome da variação 1
                        vol,          # Valor da variação 1
                        "",           # Nome da variação 2
                        "",           # Valor da variação 2
                        "",           # Nome da variação 3
                        "",           # Valor da variação 3
                        f"{float(price):.2f}" if price else "",
                        "",           # Preço promocional
                        vol_specs["weight"],
                        vol_specs["height"],
                        vol_specs["width"],
                        vol_specs["length"],
                        stock,
                        sku,
                        "",           # Código de barras
                        "SIM" if is_first_row else "", # Exibir na loja
                        "NÃO",        # Frete gratis
                        description if is_first_row else "",
                        tags if is_first_row else "",
                        seo_title if is_first_row else "",
                        seo_desc if is_first_row else "",
                        brand if is_first_row else "",
                        "SIM",        # Produto físico
                        "",           # MPN
                        "",           # Sexo
                        "",           # Faixa etária
                        f"{float(cost):.2f}" if cost else ""
                    ]
                    
                    writer.writerow(row)
                    is_first_row = False
                    
        print(f"Sucesso! Planilha gerada em: {output_path}")
    except Exception as e:
        print(f"Erro ao escrever arquivo CSV: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Conversor de lista de perfumes para importação em lote na Nuvemshop.")
    parser.add_argument("-i", "--input", required=True, help="Caminho do arquivo de entrada (txt ou md).")
    parser.add_argument("-o", "--output", required=True, help="Caminho do CSV de saída.")
    parser.add_argument("--price-2ml", default="50.00", help="Preço padrão para 2ml.")
    parser.add_argument("--price-5ml", default="100.00", help="Preço padrão para 5ml.")
    parser.add_argument("--price-10ml", default="180.00", help="Preço padrão para 10ml.")
    parser.add_argument("--stock", default="5", help="Estoque padrão das variações.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Erro: Arquivo de entrada não encontrado em {args.input}", file=sys.stderr)
        sys.exit(1)
        
    # Identificar formato com base no conteúdo
    is_markdown = args.input.endswith(".md")
    
    if is_markdown:
        print("Detectado arquivo Markdown. Tentando ler tabela...")
        perfumes = parse_markdown_table(args.input)
        if not perfumes:
            print("Nenhum perfume encontrado na tabela markdown. Tentando ler como texto estruturado...")
            perfumes = parse_structured_text(args.input)
    else:
        print("Lendo arquivo como texto estruturado...")
        perfumes = parse_structured_text(args.input)
        
    if not perfumes:
        # Tentar fallback simples: linha por linha "Marca - Perfume" ou "Marca: Perfume"
        print("Tentando parsing de texto livre...")
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                for line in f:
                    line_str = line.strip()
                    if not line_str or line_str.startswith("#") or line_str.startswith("-"):
                        continue
                    # Separador hífen ou dois pontos
                    parts = []
                    if " - " in line_str:
                        parts = line_str.split(" - ", 1)
                    elif ":" in line_str:
                        parts = line_str.split(":", 1)
                    
                    if len(parts) == 2:
                        perfumes.append({
                            "brand": parts[0].strip(),
                            "name": parts[1].strip(),
                            "volumes": {
                                "2ml": {"price": "", "cost": "", "stock": ""},
                                "5ml": {"price": "", "cost": "", "stock": ""},
                                "10ml": {"price": "", "cost": "", "stock": ""}
                            }
                        })
        except Exception as e:
            print(f"Erro no parsing de texto livre: {e}", file=sys.stderr)
            
    if not perfumes:
        print("Erro: Nenhum perfume pôde ser extraído do arquivo fornecido.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Carregados {len(perfumes)} perfumes.")
    
    default_prices = {
        "2ml": args.price_2ml,
        "5ml": args.price_5ml,
        "10ml": args.price_10ml
    }
    
    generate_csv(perfumes, args.output, default_prices=default_prices, default_stock=args.stock)

if __name__ == "__main__":
    main()
