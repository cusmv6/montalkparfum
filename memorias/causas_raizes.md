# Root Cause Registry (Memória Preventiva)

Este documento mapeia erros críticos do passado, suas causas raízes e restrições arquiteturais/técnicas. O Agente de IA deve obrigatoriamente ler este arquivo durante o Startup e verificar colisões de palavras-chaves antes de propor ou executar soluções.

## [CR-001] Python Interpreter Path Conflict (Windows Shims vs Program Files)
- **Keywords**: python, interpreter, settings.json, vscode, shim, WindowsApps, python.exe
- **Root Cause**: O Windows cria aliases de execução (shims) vazios em `C:\Users\odeao\AppData\Local\Microsoft\WindowsApps\python.exe` (ou `python3.exe`) que redirecionam para a Microsoft Store se o Python não for instalado por lá. Configurar este caminho no `python.defaultInterpreterPath` do VS Code gera erros de validação persistentes e falhas na execução de scripts no terminal se a instalação real tiver sido feita via instalador oficial do python.org.
- **Technical Decision**: O caminho do interpretador nas configurações do VS Code (`.vscode/settings.json`) deve apontar estritamente para o executável real da instalação (ex: `C:\Users\odeao\AppData\Local\Programs\Python\Python312\python.exe` ou equivalente) e NUNCA para a pasta `WindowsApps`.
- **Forbidden Actions**: Nunca alterne o caminho do interpretador de volta para a pasta `WindowsApps` e não sugira ao usuário baixar o Python da Windows Store se houver erros de ambiente.
