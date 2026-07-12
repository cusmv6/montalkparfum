---
name: session-resumo
description: >
  Habilidade para salvar um resumo do estado da interação atual antes de sair (ou reiniciar)
  e ler/descartar o resumo ao iniciar uma nova interação neste projeto.
---

# Resumo de Sessão e Persistência de Estado

Esta habilidade orienta o agente a gerenciar o estado entre sessões (conversas ou após reinicializações).

## Regras de Execução

### 1. Inicialização da Sessão (Startup)
Toda vez que você for carregado para trabalhar no projeto (geralmente a primeira ação é ler o diretório raiz `c:\Users\odeao\OneDrive\Desktop\brem`):
- Verifique a presença de um arquivo chamado `resumo.md` ou `reboot_state.md`.
- Se encontrado, leia o arquivo imediatamente usando a ferramenta `view_file` para capturar todo o contexto da sessão anterior.
- Em seguida, delete o arquivo usando uma ferramenta de comando (ex: `powershell -Command "Remove-Item c:\Users\odeao\OneDrive\Desktop\brem\resumo.md -ErrorAction SilentlyContinue; Remove-Item c:\Users\odeao\OneDrive\Desktop\brem\reboot_state.md -ErrorAction SilentlyContinue"`) para garantir que resumos antigos não persistam e que a fila esteja sempre limpa.
- Informe ao usuário que você leu o resumo do estado anterior e está pronto para continuar os trabalhos descritos nele.

### 2. Encerramento da Sessão (Shutdown / Reboot)
Toda vez que você ou o usuário forem encerrar uma interação (por exemplo, quando o usuário disser que vai reiniciar o PC, ou no final do dia, ou quando a tarefa principal terminar):
- Crie um arquivo na raiz do projeto chamado `resumo.md`.
- Escreva um resumo completo contendo:
  1. O que foi feito e descoberto até o momento.
  2. Qualquer detalhe técnico importante (ex: caminhos de arquivos, portas, chaves, erros específicos).
  3. O estado atual exato do projeto.
  4. O próximo passo claro e imediato que a próxima iteração do assistente deve executar.
- Confirme ao usuário que o "resumo" foi salvo e que ele pode reiniciar ou encerrar a sessão com segurança.
