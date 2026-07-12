---
name: limp
description: >-
  Limpa seletivamente arquivos criados ou modificados dentro de um intervalo de tempo no Desktop, Downloads e na pasta do projeto (brem). Deve ser ativada sempre que o usuário solicitar deletar arquivos temporários, limpar diretórios de testes ou organizar o ambiente operacional após sessões de diagnóstico de hardware ou software.
---

# Habilidade Limp (Limpeza Seletiva)

## Overview
A habilidade `limp` permite varrer e apagar com segurança os arquivos criados ou modificados recentemente nos diretórios de usuário: **Área de Trabalho (Desktop)**, **Downloads** e **Workspace (brem)**. Ela aceita expressões de tempo dinâmicas (ex: "últimos 2 dias", "3 horas atrás") e mantém a integridade operacional do sistema não tocando em arquivos do núcleo do Windows ou em configurações essenciais do IDE.

## Dependencies
* Python 3
* `uv` (para execução do script de apoio de forma portável)

## Quick Start

### 1. Pré-visualizar arquivos criados/modificados nas últimas 2 horas
```bash
uv run C:\Users\odeao\.gemini\config\plugins\custom-helper\skills\limp\scripts\limp.py -t "2h" --dry-run
```

### 2. Executar a limpeza real dos arquivos criados no último dia
```bash
uv run C:\Users\odeao\.gemini\config\plugins\custom-helper\skills\limp\scripts\limp.py -t "1d" --workspace "c:\Users\odeao\OneDrive\Desktop\brem"
```

## Utility Scripts

O script `limp.py` gerencia o fluxo de busca, whitelist e deleção.

### Parâmetros Suportados

* `-t`, `--time` (Obrigatório): O intervalo de tempo para a pesquisa de arquivos.
  * *Valores relativos:* `Xh` (horas), `Xd` (dias), `Xm` (minutos).
  * *Valores absolutos:* Datetimes no formato `YYYY-MM-DD HH:MM:SS` ou `DD/MM/YYYY HH:MM:SS`.
* `--dry-run`: Executa a varredura e lista os candidatos a deleção sem realmente apagar nenhum arquivo.
* `-o`, `--output`: Caminho para gerar um relatório estruturado em formato JSON da limpeza.
* `--workspace`: Caminho opcional da pasta de desenvolvimento (ex: `brem`).

### Exemplo de Comando com Relatório
```bash
uv run C:\Users\odeao\.gemini\config\plugins\custom-helper\skills\limp\scripts\limp.py -t "3h" -o "c:\Users\odeao\OneDrive\Desktop\brem\relatorio_limpeza.json" --workspace "c:\Users\odeao\OneDrive\Desktop\brem"
```

## Proteções de Integridade (Whitelist)

O script **nunca** apagará arquivos que casem com os seguintes padrões:
* Arquivos de configuração de agente e IDE: `.clinerules`, `.cursorrules`
* Configurações de controle de versão: `.git` (repositório)
* Arquivos especiais do sistema operacional: `desktop.ini`, `ntuser.dat`
* Arquivos fora das pastas de usuário especificadas.

## Tratamento de Erros e Arquivos Bloqueados

Quando a deleção falha devido a privilégios insuficientes (UAC) ou arquivos abertos/travados por outros processos:
1. O script não para a execução, ele continua limpando os outros itens.
2. Ao final, ele gera uma lista detalhada dos arquivos que falharam, mapeando:
   * **Impacto:** O papel daquele arquivo no computador (ex: arquivo de log ativo, DLL de sistema).
   * **Solução recomendada:** Instrução passo a passo para que você possa se livrar dele manualmente ou obter permissão especial de Administrador.

## Common Mistakes
1. **Esquecer o `--dry-run` na primeira execução:** Execute sempre com `--dry-run` primeiro para confirmar se os arquivos a serem excluídos são realmente os desejados.
2. **Esperar a remoção de arquivos protegidos:** Tentar remover `.clinerules` ou arquivos do núcleo do Windows falhará por design para proteção do sistema.
3. **Não especificar o `--workspace`:** Se você quiser limpar a pasta do projeto além do Desktop e Downloads, precisa passar explicitamente o argumento `--workspace "C:\caminho\do\projeto"`.
