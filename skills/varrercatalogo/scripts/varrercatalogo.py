#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess

WORKSPACE_DIR = r"C:\Users\odeao\OneDrive\Desktop\brem"
CATALOGO_JSON = os.path.join(WORKSPACE_DIR, "PROJETOS", "Bruno", "produtos", "catalogo.json")
TRAZFRAGRANTICA = os.path.join(WORKSPACE_DIR, "grimorio", "trazfragrantica", "scripts", "trazfragrantica.py")
OPIBLOG = os.path.join(WORKSPACE_DIR, "grimorio", "opiblog", "scripts", "opiblog.py")
ESTAGIARIOVISUAL = os.path.join(WORKSPACE_DIR, "SUMMONS", "estagiariovisual", "scripts", "estagiariovisual.py")
UPLOADER = os.path.join(WORKSPACE_DIR, "grimorio", "nuvemshop-uploader", "scripts", "nuvemshop_converter.py")
CATALOGO_MD = os.path.join(WORKSPACE_DIR, "PROJETOS", "Bruno", "Decante", "catalogo_perfumes.md")
IMPORTAR_CSV = os.path.join(WORKSPACE_DIR, "PROJETOS", "Bruno", "produtos", "importar_nuvemshop.csv")

def load_perfumes():
    if not os.path.exists(CATALOGO_JSON):
        print(f"Erro: O arquivo de catalogo não existe em: {CATALOGO_JSON}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(CATALOGO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler catalogo.json: {e}", file=sys.stderr)
        sys.exit(1)

def run_subprocess(cmd):
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar subprocesso: {e}", file=sys.stderr)
        raise e

def main():
    parser = argparse.ArgumentParser(description="Orquestrador Mestre de Varredura do Catálogo da Montalk.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--perfume", help="ID do perfume específico para processar.")
    group.add_argument("--limit", type=int, help="Processa os primeiros N perfumes do catálogo.")
    group.add_argument("--all", action="store_true", help="Processa todo o catálogo de perfumes.")
    
    args = parser.parse_args()
    
    perfumes_data = load_perfumes()
    
    if args.perfume:
        selected = [p for p in perfumes_data if p.get("id") == args.perfume]
        if not selected:
            print(f"Erro: Perfume com ID '{args.perfume}' não encontrado no catalogo.json.", file=sys.stderr)
            sys.exit(1)
    elif args.limit:
        selected = perfumes_data[:args.limit]
    else:
        selected = perfumes_data

    total = len(selected)
    print("=" * 80)
    print(f"[START] Iniciando pipeline de varredura para {total} perfume(s)...")
    print("=" * 80)
    
    for idx, p in enumerate(selected):
        p_id = p.get("id")
        p_nome = p.get("nome")
        p_marca = p.get("marca")
        
        print(f"\n>>> [{idx + 1}/{total}] PROCESSANDO: {p_nome} ({p_marca}) [ID: {p_id}] <<<")
        
        # Passo 1: trazfragrantica.py (Sincroniza acordes/votos/notas e renderiza card SKU base)
        print("\n--- PASSO 1/2: Sincronizando dados técnicos (Fragrantica) e renderizando Card ---")
        try:
            run_subprocess([sys.executable, TRAZFRAGRANTICA, "run", "--perfume", p_id])
        except Exception as e:
            print(f"   [AVISO] Falha no passo trazfragrantica para {p_id}: {e}. Continuando lote...")
            continue
            
        # Passo 2: opiblog.py (Enriquece com resenha e ocasiões do ÇaFleureBon)
        print("\n--- PASSO 2/3: Enriquecendo com Crítica Editorial (ÇaFleureBon) ---")
        try:
            run_subprocess([sys.executable, OPIBLOG, "--perfume", p_id])
        except Exception as e:
            print(f"   [AVISO] Falha no passo opiblog para {p_id}: {e}. Continuando lote...")
            continue
            
        # Passo 3: estagiariovisual.py (Orquestra e gera a grade visual de luxo - Fotos 1, 2 e 3)
        print("\n--- PASSO 3/3: Orquestrando grade de imagens (Fotos 1, 2 e 3) ---")
        try:
            run_subprocess([sys.executable, ESTAGIARIOVISUAL, "--perfume", p_id])
        except Exception as e:
            print(f"   [AVISO] Falha no passo estagiariovisual para {p_id}: {e}. Continuando lote...")
            continue
            
    # Passo 4: nuvemshop_converter.py (Exporta a planilha importar_nuvemshop.csv)
    print("\n" + "=" * 80)
    print("--- PASSO FINAL: Atualizando a Planilha de Importação Nuvemshop ---")
    print("=" * 80)
    try:
        run_subprocess([sys.executable, UPLOADER, "-i", CATALOGO_MD, "-o", IMPORTAR_CSV])
        print(f"[SUCESSO] Planilha de importação regerada em: {IMPORTAR_CSV}")
    except Exception as e:
        print(f"   [ERRO] Falha ao regerar a planilha de importação: {e}", file=sys.stderr)
        
    print("\n" + "=" * 80)
    print(f"[FIM] Pipeline de varredura finalizado com sucesso!")
    print("=" * 80)

if __name__ == "__main__":
    main()
