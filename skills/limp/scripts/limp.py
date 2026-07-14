#!/usr/bin/env python3
import os
import sys
import argparse
import re
import shutil
import json
from datetime import datetime, timedelta

# Whitelist de nomes de arquivos e diretórios que NUNCA devem ser deletados
WHITELIST_PATTERNS = [
    r'^\.clinerules$',
    r'^\.cursorrules$',
    r'^\.git$',
    r'^desktop\.ini$',
    r'^ntuser\..*$',
    r'^\.gemini$',
]

def is_whitelisted(name):
    for pattern in WHITELIST_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return True
    return False

def parse_time_range(time_str):
    """
    Traduz strings de tempo flexíveis (ex: '2h', '1d', '30m') ou datetime
    para um objeto datetime representando o cutoff.
    """
    now = datetime.now()
    
    # Tenta padrão de tempo relativo: valor + unidade
    match = re.match(r'^(\d+)\s*(h|d|m|horas|dias|minutos)$', time_str.strip().lower())
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit in ('h', 'horas'):
            return now - timedelta(hours=value)
        elif unit in ('d', 'dias'):
            return now - timedelta(days=value)
        elif unit in ('m', 'minutos'):
            return now - timedelta(minutes=value)
            
    # Tenta parsing direto de ISO datetime
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y'):
        try:
            return datetime.strptime(time_str.strip(), fmt)
        except ValueError:
            continue
            
    raise ValueError(f"Não foi possível interpretar o intervalo de tempo: '{time_str}'")

def get_file_impact_and_remedy(path, error_msg):
    """
    Retorna uma descrição amigável do impacto do arquivo e como se livrar dele.
    """
    ext = os.path.splitext(path)[1].lower()
    name = os.path.basename(path).lower()
    
    impact = "Arquivo de dados ou log temporário."
    remedy = "Tente fechar os programas abertos e deletar o arquivo manualmente."
    
    if "program files" in path.lower():
        impact = "Arquivo de instalação/configuração em diretório protegido pelo sistema."
        remedy = "Este arquivo requer privilégios de Administrador. Execute a remoção como Admin ou exclua a pasta manualmente."
    elif ext in ('.sys', '.dll'):
        impact = "Driver de dispositivo ou biblioteca em uso pelo Windows."
        remedy = "O driver pode estar ativo na memória. Pode ser necessário desativar o dispositivo correspondente ou reiniciar o PC em Modo de Segurança para deletar."
    elif ext == '.log':
        impact = "Arquivo de log mantido aberto por um serviço ativo."
        remedy = "Verifique qual serviço (ex: Windows Update, NVIDIA Container) está escrevendo no log e pare-o temporariamente."
    elif ext == '.exe':
        impact = "Executável ou instalador que pode estar rodando ou bloqueado."
        remedy = "Abra o Gerenciador de Tarefas, encerre o processo correspondente e tente novamente."
        
    return {
        "impact": impact,
        "how_to_delete": remedy,
        "raw_error": str(error_msg)
    }

def clean_directory(dir_path, cutoff_time, dry_run, deleted_files, failed_files):
    if not os.path.exists(dir_path):
        return
        
    for root, dirs, files in os.walk(dir_path, topdown=False):
        # Filtrar diretórios na whitelist antes de prosseguir
        dirs[:] = [d for d in dirs if not is_whitelisted(d)]
        
        for file in files:
            if is_whitelisted(file):
                continue
                
            file_path = os.path.join(root, file)
            try:
                # Verificar data de criação (ctime) e modificação (mtime)
                stat = os.stat(file_path)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                ctime = datetime.fromtimestamp(stat.st_ctime)
                
                # Se foi criado ou modificado após o cutoff
                if mtime >= cutoff_time or ctime >= cutoff_time:
                    size = stat.st_size
                    if dry_run:
                        deleted_files.append({"path": file_path, "size": size, "dry_run": True})
                    else:
                        try:
                            os.remove(file_path)
                            deleted_files.append({"path": file_path, "size": size})
                        except Exception as e:
                            failed_files.append({
                                "path": file_path,
                                **get_file_impact_and_remedy(file_path, e)
                            })
            except Exception as e:
                failed_files.append({
                    "path": file_path,
                    "impact": "Falha ao obter metadados do arquivo.",
                    "how_to_delete": "Verifique as permissões de leitura do arquivo.",
                    "raw_error": str(e)
                })
                
        # Tentar remover diretórios que ficaram vazios se foram criados após o cutoff
        for d in dirs:
            dir_full_path = os.path.join(root, d)
            if is_whitelisted(d):
                continue
                
            try:
                # Se estiver vazio
                if not os.listdir(dir_full_path):
                    stat = os.stat(dir_full_path)
                    ctime = datetime.fromtimestamp(stat.st_ctime)
                    if ctime >= cutoff_time:
                        if dry_run:
                            deleted_files.append({"path": dir_full_path, "size": 0, "directory": True, "dry_run": True})
                        else:
                            os.rmdir(dir_full_path)
                            deleted_files.append({"path": dir_full_path, "size": 0, "directory": True})
            except Exception:
                # Falhas ao deletar pastas vazias são ignoradas silenciosamente
                pass

def main():
    parser = argparse.ArgumentParser(description="Limp - Limpeza seletiva por tempo.")
    parser.add_argument("-t", "--time", required=True, help="Intervalo de tempo a limpar (ex: '2h', '1d', '2026-06-22 19:45:00').")
    parser.add_argument("--dry-run", action="store_true", help="Apenas lista os arquivos sem deletar.")
    parser.add_argument("-o", "--output", help="Caminho do arquivo JSON para salvar o relatório.")
    parser.add_argument("--workspace", help="Caminho do diretório de projeto (brem).")
    
    args = parser.parse_args()
    
    try:
        cutoff_time = parse_time_range(args.time)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Iniciando varredura para arquivos criados/modificados após: {cutoff_time.strftime('%d/%m/%Y %H:%M:%S')}")
    if args.dry_run:
        print("[MODO DRY-RUN] Nenhum arquivo será realmente deletado.")
        
    # Mapear pastas de busca
    user_profile = os.path.expanduser('~')
    
    # Tentar encontrar a pasta Desktop (local ou via OneDrive)
    desktop_paths = [
        os.path.join(user_profile, "OneDrive", "Desktop"),
        os.path.join(user_profile, "Desktop"),
        os.path.join(os.environ.get("PUBLIC", "C:\\Users\\Public"), "Desktop")
    ]
    desktop_path = next((p for p in desktop_paths if os.path.exists(p)), None)
    
    downloads_path = os.path.join(user_profile, "Downloads")
    
    # Normalizar caminhos e remover duplicados/subpastas para evitar varredura dupla
    candidate_paths = []
    for p in [desktop_path, downloads_path, args.workspace]:
        if p and os.path.exists(p):
            abs_path = os.path.abspath(p)
            if abs_path not in candidate_paths:
                candidate_paths.append(abs_path)
                
    # Ordenar do caminho mais curto ao mais longo para simplificar a checagem de subpasta
    candidate_paths.sort(key=len)
    targets = []
    for path in candidate_paths:
        is_sub = False
        for parent in targets:
            try:
                # Se for a mesma pasta ou uma subpasta de um target já listado
                rel = os.path.relpath(path, parent)
                if not rel.startswith('..') and rel != '.':
                    is_sub = True
                    break
            except ValueError:
                pass
        if not is_sub:
            targets.append(path)
            
    print(f"Diretórios alvo monitorados (deduplicados): {targets}")
    
    deleted_files = []
    failed_files = []
    
    for target in targets:
        clean_directory(target, cutoff_time, args.dry_run, deleted_files, failed_files)
        
    # Exibir resumo na saída padrão
    print(f"\nVarredura concluída.")
    print(f"Arquivos identificados/removidos: {len(deleted_files)}")
    print(f"Falhas ao remover: {len(failed_files)}")
    
    if failed_files:
        print("\n--- ARQUIVOS QUE NÃO PUDERAM SER REMOVIDOS ---")
        for f in failed_files:
            print(f"\nCaminho: {f['path']}")
            print(f"Impacto: {f['impact']}")
            print(f"Solução: {f['how_to_delete']}")
            
    # Salvar relatório se solicitado
    report = {
        "cutoff_time": cutoff_time.isoformat(),
        "dry_run": args.dry_run,
        "deleted": deleted_files,
        "failed": failed_files
    }
    
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\nRelatório de limpeza salvo em: {args.output}")
        except Exception as e:
            print(f"Erro ao salvar relatório: {e}", file=sys.stderr)
            
if __name__ == "__main__":
    main()
