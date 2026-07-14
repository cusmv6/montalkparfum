#!/usr/bin/env python3
import os
import sys
import argparse
import json
import urllib.request
import xml.etree.ElementTree as ET
import re

# Forçar a saída padrão (stdout) para utilizar UTF-8 no Windows para suportar emojis sem erro
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def fetch_and_save_sitemaps(output_path):
    sitemaps = [
        "https://www.kingofdecants.com.br/sitemap/product-1.xml",
        "https://www.kingofdecants.com.br/sitemap/product-2.xml",
        "https://www.kingofdecants.com.br/sitemap/product-3.xml"
    ]
    products = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for url in sitemaps:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
            root = ET.fromstring(xml_data)
            namespace = ""
            if root.tag.startswith("{"):
                namespace = root.tag.split("}")[0] + "}"
            loc_tag = f"{namespace}loc"
            for url_node in root.findall(f"{namespace}url"):
                loc_node = url_node.find(loc_tag)
                if loc_node is not None and loc_node.text:
                    loc = loc_node.text.strip()
                    if loc.startswith("https://www.kingofdecants.com.br/"):
                        slug = loc.replace("https://www.kingofdecants.com.br/", "")
                        if slug and not any(x in slug for x in ["sitemap", "busca", "carrinho", "conta"]):
                            name = slug.replace("-", " ").title()
                            products.append({
                                "name": name,
                                "url": loc,
                                "slug": slug
                            })
        except Exception:
            pass
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return products

def find_competitor_price(perfume_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "king_products.json")
    
    if not os.path.exists(json_path):
        products = fetch_and_save_sitemaps(json_path)
    else:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
        except Exception:
            products = fetch_and_save_sitemaps(json_path)
            
    if not products:
        return None
        
    tokens = [t.lower() for t in perfume_name.split() if len(t) > 2]
    if not tokens:
        return None
        
    matches = []
    for p in products:
        p_name_lower = p["name"].lower()
        p_slug_lower = p["slug"].lower()
        
        # Tokenizar o nome do produto para comparação precisa
        p_tokens = set(re.findall(r'\b\w+\b', p_name_lower))
        
        # Verificar se todos os tokens da busca estão no produto
        if all(t in p_name_lower or t in p_slug_lower for t in tokens):
            extra_tokens = len(p_tokens.difference(set(tokens)))
            matches.append((extra_tokens, p))
            
    # Se não encontrar com todos os tokens, tentar com o token mais longo (palavra-chave principal)
    if not matches and tokens:
        main_token = max(tokens, key=len)
        for p in products:
            p_name_lower = p["name"].lower()
            p_slug_lower = p["slug"].lower()
            if main_token in p_name_lower or main_token in p_slug_lower:
                p_tokens = set(re.findall(r'\b\w+\b', p_name_lower))
                extra_tokens = len(p_tokens.difference(set([main_token])))
                matches.append((extra_tokens, p))
                
    # Ordenar por menor quantidade de tokens extras (mais próximo do exato)
    matches.sort(key=lambda x: x[0])
    matches = [m[1] for m in matches]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Se ainda assim não encontrar nos sitemaps, buscar na categoria decants-nicho como fallback
    if not matches:
        try:
            niche_url = "https://www.kingofdecants.com.br/decants-nicho"
            req = urllib.request.Request(niche_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as r:
                niche_html = r.read().decode('utf-8')
            links = re.findall(r'href="https://www\.kingofdecants\.com\.br/([^"]+)"', niche_html)
            for slug in set(links):
                if not any(x in slug for x in ["sitemap", "busca", "carrinho", "conta", "decants-nicho"]):
                    name_from_slug = slug.replace("-", " ").title()
                    if all(t in name_from_slug.lower() for t in tokens):
                        matches.append({"name": name_from_slug, "url": f"https://www.kingofdecants.com.br/{slug}", "slug": slug})
        except Exception:
            pass
            
    for m in matches[:3]:  # Limitar a 3 requisições HTTP em tempo real
        url = m["url"]
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8')
                
            # Procurar pelo bloco SKU de 10ml
            for div_match in re.finditer(r'<div class="acoes-produto[^"]*SKU-[^"]*-10ml"[^>]*>', html, re.IGNORECASE):
                start = div_match.start()
                next_div = html.find('<div class="acoes-produto', start + 1)
                if next_div == -1:
                    next_div = start + 10000
                block = html[start:next_div]
                
                # Extrair preço de venda
                sell_price = None
                sell_match = re.search(r'data-sell-price="([^"]+)"', block)
                if sell_match:
                    sell_price = float(sell_match.group(1))
                else:
                    prom_match = re.search(r'class="preco-promocional[^>]*>\s*R\$\s*([\d\.,]+)', block)
                    if prom_match:
                        sell_price = float(prom_match.group(1).replace('.', '').replace(',', '.'))
                        
                pix_price = None
                pix_match = re.search(r'R\$\s*([\d\.,]+)</strong>\s*via\s+Pix', block, re.IGNORECASE)
                if pix_match:
                    pix_price = float(pix_match.group(1).replace('.', '').replace(',', '.'))
                    
                if sell_price:
                    return {
                        "name": m["name"],
                        "url": url,
                        "sell_price": sell_price,
                        "pix_price": pix_price
                    }
        except Exception:
            pass
            
    return None

def calculate_single(price_a, price_b, full_volume, chosen_volume, name=None):
    if full_volume <= 0:
        raise ValueError("O volume total do frasco original deve ser maior que zero.")
    if chosen_volume <= 0 or chosen_volume > full_volume:
        raise ValueError(f"O volume escolhido ({chosen_volume}ml) deve estar entre 0 e o volume total do frasco ({full_volume}ml).")
    if price_a < 0 or price_b < 0:
        raise ValueError("Os preços não podem ser negativos.")
        
    # Identificar o preço maior como Brasil (peso 8) e o menor como China (peso 2)
    price_br = max(price_a, price_b)
    price_cn = min(price_a, price_b)
    
    # 1. Valor Ponderado do Frasco Cheio (Regra 8/2)
    weighted_value = ((price_br * 8) + (price_cn * 2)) / 10.0
    
    # 2. Divisão de Custos: Frasco Físico (15% do valor base) e Líquido Total (100% do valor base)
    bottle_shell_value = weighted_value * 0.15
    liquid_value_total = weighted_value
    
    # 3. Custo do Líquido por ml
    cost_per_ml = liquid_value_total / full_volume
    cost_cn_per_ml = price_cn / full_volume
    
    # 4. Cálculo do Decante Âncora (10ml)
    liquid_cost_base_10ml = cost_per_ml * 10.0
    liquid_cost_convenience_10ml = liquid_cost_base_10ml * 1.07
    final_price_10ml = liquid_cost_convenience_10ml + 30.0
    
    original_final_price_10ml = final_price_10ml
    price_10ml_was_adjusted = False
    comp_info = None
    
    # Injetar Quality Gate Lógico com loop de auto-correção de até 5 tentativas
    tentativas = 5
    fator_reducao_concorrente = 0.84 # Pelo menos 16% mais barato
    
    for rodada in range(1, tentativas + 1):
        final_price_10ml = original_final_price_10ml
        price_10ml_was_adjusted = False
        
        if name:
            comp_info = find_competitor_price(name)
            if comp_info:
                p_king = comp_info["sell_price"]
                limit_price_10ml = p_king * fator_reducao_concorrente
                
                if final_price_10ml > limit_price_10ml:
                    final_price_10ml = limit_price_10ml
                    price_10ml_was_adjusted = True
        
        # Teste de conformidade: O preço de 10ml cobre os custos reais da China + insumo fixo (R$ 30.00)?
        custo_real_10ml = (cost_cn_per_ml * 10.0) + 30.0
        lucro_estimado = final_price_10ml - custo_real_10ml
        
        if lucro_estimado >= 0:
            # Passou no Quality Gate!
            break
        else:
            # Se der prejuízo devido ao cap do concorrente, recua 3% na redução (recalibra)
            print(f"   [AVISO Quality Gate Lógico] Tentativa {rodada}/{tentativas}: Preco capped no concorrente deu prejuizo de R$ {-lucro_estimado:.2f}. Recalibrando fator...")
            fator_reducao_concorrente += 0.03
            if fator_reducao_concorrente > 0.98:
                fator_reducao_concorrente = 0.98 # Capped maximo para nao ficar mais caro que concorrente
                
    # Arredondar preços de 10ml para o par mais próximo
    final_price_10ml = float(int(final_price_10ml / 2 + 0.5) * 2)
    original_final_price_10ml = float(int(original_final_price_10ml / 2 + 0.5) * 2)
                
    # 5. Escalar o preço para o volume escolhido com base nas proporções do Bruno
    if chosen_volume == 10.0:
        final_price = final_price_10ml
        original_final_price = original_final_price_10ml
        price_was_adjusted = price_10ml_was_adjusted
        if comp_info:
            p_king_ref = comp_info["sell_price"]
            limit_price = limit_price_10ml
    elif chosen_volume == 5.0:
        final_price = float(int((final_price_10ml * (100.0 / 180.0)) / 2 + 0.5) * 2)
        original_final_price = float(int((original_final_price_10ml * (100.0 / 180.0)) / 2 + 0.5) * 2)
        price_was_adjusted = price_10ml_was_adjusted
        if comp_info:
            p_king_ref = comp_info["sell_price"] * (100.0 / 180.0)
            limit_price = limit_price_10ml * (100.0 / 180.0)
    elif chosen_volume == 2.0:
        final_price = float(int((final_price_10ml * (50.0 / 180.0)) / 2 + 0.5) * 2)
        original_final_price = float(int((original_final_price_10ml * (50.0 / 180.0)) / 2 + 0.5) * 2)
        price_was_adjusted = price_10ml_was_adjusted
        if comp_info:
            p_king_ref = comp_info["sell_price"] * (50.0 / 180.0)
            limit_price = limit_price_10ml * (50.0 / 180.0)
    else:
        final_price = float(int((final_price_10ml * (chosen_volume / 10.0)) / 2 + 0.5) * 2)
        original_final_price = float(int((original_final_price_10ml * (chosen_volume / 10.0)) / 2 + 0.5) * 2)
        price_was_adjusted = price_10ml_was_adjusted
        if comp_info:
            p_king_ref = comp_info["sell_price"] * (chosen_volume / 10.0)
            limit_price = limit_price_10ml * (chosen_volume / 10.0)
            
    adjustment_discount = original_final_price - final_price
    
    # Lucro líquido estimado = Preço final de venda - (Custo real líquido na China + Custo Fixo de insumos/frete)
    real_liquid_cost_cn = cost_cn_per_ml * chosen_volume
    real_profit = final_price - (real_liquid_cost_cn + 30.0)
    
    liquid_cost_base = cost_per_ml * chosen_volume
    liquid_cost_convenience = liquid_cost_base * 1.07
    
    # 6. Calcular tabela comparativa para os volumes padrão (2ml, 5ml, 10ml)
    table_data = []
    for vol in [2.0, 5.0, 10.0]:
        if vol == 10.0:
            v_price = final_price_10ml
        elif vol == 5.0:
            v_price = float(int((final_price_10ml * (100.0 / 180.0)) / 2 + 0.5) * 2)
        elif vol == 2.0:
            v_price = float(int((final_price_10ml * (50.0 / 180.0)) / 2 + 0.5) * 2)
            
        v_cost = (cost_cn_per_ml * vol) + 30.0
        v_profit = v_price - v_cost
        v_margin = (v_profit / v_price) * 100 if v_price > 0 else 0
        table_data.append({
            "vol": f"{vol:.0f} ml",
            "price": f"R$ {v_price:.2f}",
            "price_ml": f"R$ {v_price/vol:.2f}/ml",
            "cost": f"R$ {v_cost:.2f}",
            "profit": f"R$ {v_profit:.2f}",
            "margin": f"{v_margin:.1f}%"
        })

    if name:
        print("=" * 81)
        print(f" 🌟 PERFUME: {name.upper()}")
    print("=" * 81)
    print(f" 📊 DADOS DE CUSTO DO FRASCO ORIGINAL:")
    print(f"   - Preço no Brasil (Referência): R$ {price_br:.2f}")
    print(f"   - Preço pago na China (Custo):   R$ {price_cn:.2f}")
    print(f"   - Volume original do frasco:   {full_volume:.0f} ml")
    print(f"   - Base do frasco (Regra 8/2):   R$ {weighted_value:.2f}")
    print(f"   - Custo base do líquido:        R$ {cost_per_ml:.2f} por ml")
    
    if comp_info:
        print("-" * 81)
        print(f" 🔍 CONSULTA AO CONCORRENTE (King of Decants 10ml):")
        print(f"   - Preço de 10ml no concorrente: R$ {comp_info['sell_price']:.2f} ({comp_info['name']})")
        if price_10ml_was_adjusted:
            print(f"   - AJUSTE DE PREÇO APLICADO: Capped em -16% (Original: R$ {original_final_price_10ml:.2f})")
            print(f"   - Preço âncora final de 10ml: R$ {final_price_10ml:.2f}")
        else:
            print(f"   - AJUSTE DE PREÇO: Não necessário (preço calculado já é competitivo)")
            
    print("-" * 81)
    print(" 🧪 TABELA COMPARATIVA DE PREÇOS E MARGENS (Decantes):")
    print("+" + "-"*9 + "+" + "-"*14 + "+" + "-"*14 + "+" + "-"*14 + "+" + "-"*24 + "+")
    print(f"| {'Volume':^9} | {'Preço Venda':^14} | {'Preço por ml':^14} | {'Custo Total':^14} | {'Lucro (Margem)':^24} |")
    print("+" + "-"*9 + "+" + "-"*14 + "+" + "-"*14 + "+" + "-"*14 + "+" + "-"*24 + "+")
    for row in table_data:
        profit_str = row["profit"]
        margin_str = row["margin"]
        profit_cell = f"{profit_str} ({margin_str})"
        print(f"| {row['vol']:^9} | {row['price']:^14} | {row['price_ml']:^14} | {row['cost']:^14} | {profit_cell:^24} |")
    print("+" + "-"*9 + "+" + "-"*14 + "+" + "-"*14 + "+" + "-"*14 + "+" + "-"*24 + "+")
    print(f" 👉 Nota: O 'Custo Total' inclui R$ 30,00 fixos por decante (frasco, borrifador e insumos).")
    print("=" * 81 + "\n")
    
    return {
        "br_price": price_br,
        "cn_price": price_cn,
        "weighted_bottle_value": round(weighted_value, 2),
        "bottle_shell_value": round(bottle_shell_value, 2),
        "cost_per_ml": round(cost_per_ml, 4),
        "liquid_cost_base": round(liquid_cost_base, 2),
        "liquid_cost_convenience": round(liquid_cost_convenience, 2),
        "fixed_cost": 30.0,
        "final_price": round(final_price, 2),
        "real_profit": round(real_profit, 2)
    }

def main():
    parser = argparse.ArgumentParser(description="Preco - Calculadora de precificação para decantes.")
    parser.add_argument("-vc", "--volume-chosen", type=float, default=10.0, help="Volume do decante em ml (padrão 10).")
    parser.add_argument("-vf", "--volume-full", type=float, help="Volume total em ml do frasco original cheio (ex: 100).")
    parser.add_argument("-p1", "--price1", type=float, help="Primeira referência de preço (BRL).")
    parser.add_argument("-p2", "--price2", type=float, help="Segunda referência de preço (BRL).")
    parser.add_argument("-l", "--list-file", help="Caminho para arquivo JSON contendo lista de perfumes para calcular em lote.")
    parser.add_argument("-n", "--name", help="Nome do perfume para pesquisar no concorrente King of Decants.")
    parser.add_argument("-o", "--output", help="Caminho opcional do arquivo JSON para salvar os resultados.")
    
    args = parser.parse_args()
    
    results = []
    
    if args.list_file:
        # Modo Processamento de Lista
        if not os.path.exists(args.list_file):
            print(f"Erro: Arquivo de lista não encontrado em: {args.list_file}", file=sys.stderr)
            sys.exit(1)
            
        try:
            with open(args.list_file, 'r', encoding='utf-8-sig') as f:
                items = json.load(f)
        except Exception as e:
            print(f"Erro ao ler arquivo JSON de lista: {e}", file=sys.stderr)
            sys.exit(1)
            
        if not isinstance(items, list):
            print("Erro: O arquivo de lista JSON deve conter um array/lista.", file=sys.stderr)
            sys.exit(1)
            
        print(f"Processando {len(items)} perfumes da lista...\n")
        for idx, item in enumerate(items):
            try:
                name = item.get("name", f"Perfume #{idx+1}")
                p1 = float(item["price1"])
                p2 = float(item["price2"])
                vf = float(item["volume_full"])
                vchosen = float(item.get("volume_chosen", args.volume_chosen))
                
                res = calculate_single(p1, p2, vf, vchosen, name)
                results.append({"name": name, **res})
            except KeyError as e:
                print(f"Erro no Perfume #{idx+1}: Chave obrigatória faltando {e}", file=sys.stderr)
            except Exception as e:
                print(f"Erro no Perfume #{idx+1}: {e}", file=sys.stderr)
    else:
        # Modo Individual
        if args.volume_full is None or args.price1 is None or args.price2 is None:
            print("Erro: Para cálculo individual, os argumentos -vf, -p1 e -p2 são obrigatórios.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
            
        try:
            res = calculate_single(args.price1, args.price2, args.volume_full, args.volume_chosen, args.name)
            results = res
        except Exception as e:
            print(f"Erro ao calcular precificação: {e}", file=sys.stderr)
            sys.exit(1)
            
    if args.output and results:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar arquivo de saída: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
