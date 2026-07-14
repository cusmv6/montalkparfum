# Root Cause Registry (Memória Preventiva)

Este documento mapeia erros críticos do passado, suas causas raízes e restrições arquiteturais/técnicas. O Agente de IA deve obrigatoriamente ler este arquivo durante o Startup e verificar colisões de palavras-chaves antes de propor ou executar soluções.

## [CR-001] Python Interpreter Path Conflict (Windows Shims vs Program Files)
- **Keywords**: python, interpreter, settings.json, vscode, shim, WindowsApps, python.exe
- **Root Cause**: O Windows cria aliases de execução (shims) vazios em `C:\Users\odeao\AppData\Local\Microsoft\WindowsApps\python.exe` (ou `python3.exe`) que redirecionam para a Microsoft Store se o Python não for instalado por lá. Configurar este caminho no `python.defaultInterpreterPath` do VS Code gera erros de validação persistentes e falhas na execução de scripts no terminal se a instalação real tiver sido feita via instalador oficial do python.org.
- **Technical Decision**: O caminho do interpretador nas configurações do VS Code (`.vscode/settings.json`) deve apontar estritamente para o executável real da instalação (ex: `C:\Users\odeao\AppData\Local\Programs\Python\Python312\python.exe` ou equivalente) e NUNCA para a pasta `WindowsApps`.
- **Forbidden Actions**: Nunca alterne o caminho do interpretador de volta para a pasta `WindowsApps` e não sugira ao usuário baixar o Python da Windows Store se houver erros de ambiente.

## [CR-002] Git Push/Pull Authentication Hanging in Background Console
- **Keywords**: git push, git pull, authentication, hang, credential manager, background, task, oauth
- **Root Cause**: Executar comandos Git que demandam autenticação interativa (como `git push` ou `git pull` pela primeira vez) dentro de tarefas de segundo plano (background tasks) do Agente de IA impede a exibição correta da janela gráfica do Git Credential Manager (GCM) no Windows ou trava a sessão aguardando entradas não-interativas. Isso deixa a tarefa suspensa indefinidamente.
- **Technical Decision**: Sempre que houver suspeita de que uma operação do Git acionará autenticação ou pop-ups de segurança, instrua o usuário a executar o respectivo comando (ex: `git push -u origin main`) diretamente no terminal integrado do VS Code.
- **Forbidden Actions**: Não execute comandos do Git interativos ou de autenticação pendente via tarefas de background do console do agente.

## [CR-003] DuckDuckGo Rate Limits in Batch URL Scraping
- **Keywords**: duckduckgo, rate limit, find_url_ddg, trazfragrantica, scrape, batch, url override
- **Root Cause**: Consultas repetitivas e automatizadas no DuckDuckGo (via HTTP simples com urllib) para descobrir URLs do Fragrantica em lote de múltiplos perfumes batem rapidamente no limite de taxa ou captcha do buscador. Isso retorna páginas de resultados em branco e gera erros críticos de URLs não encontradas.
- **Technical Decision**: Para execuções em lote no script `trazfragrantica.py`, mapeie preventivamente as URLs oficiais do Fragrantica no dicionário estático `URL_OVERRIDES` ou configure no banco de dados local `catalogo.json` a chave `"url_fragrantica"` para evitar pesquisas dinâmicas na web.
- **Forbidden Actions**: Evite disparar loops de scraping de pesquisa que façam requisições HTTP em massa ao DuckDuckGo sem overrides de URL ou delays de tempo elevados.

## [CR-004] AI Image Generation Branding Violations (Bottle and Cap Fidelity)
- **Keywords**: generate_image, prompt, amouage, cap, bottle, branding, quality gate, khanjar, civet, leather, textless
- **Root Cause**: Algoritmos de difusão de imagem (IA) tendem a cometer erros de branding em perfumaria de luxo, como misturar tampas de linhas (colocar tampas de cúpula em frascos errados, adicionar pedras alucinadas onde deveriam ser lisas), alucinar metadados/volumetrias, e renderizar notas animalíticas brutas de forma literal (desenhando civetas ou roedores físicos bizarros sobre a mesa). Além disso, a IA frequentemente ignora negações puras no prompt (como "NO text", "NO gemstones").
- **Technical Decision**: 
    1. **Superfície Positiva:** Descrever positivamente a ausência de texto/joias usando termos afirmativos de superfície lisa e limpa (ex: *"completely clean, blank gold metal surface, entirely free of any printed letters"*), em vez de negações simples.
    2. **Controle de Escrita (REGRAS_TEXTO_FRASCO):** Usar a tabela centralizada no script para ditar de forma binária se o frasco deve ter escrita (com a grafia exata especificada, como Creed) ou ser completamente sem texto.
    3. **Metáforas Animalíticas:** Mapear notas animalíticas (como civeta ou castóreo) para metáforas elegantes de alta-costura (como rolos de couro texturizado premium ou camurça), acompanhadas de negação biológica estrita no prompt (*"Absolutely NO live animals, NO rodents..."*).
    4. **Quality Gate Multimodal Rígido (Geral):** A IA do Gemini no Quality Gate deve fazer uma comparação 1:1 rigorosa e universal entre a imagem gerada e a referência real em termos de tampas (gemas alucinadas), escritos, translucidez e geometria.
- **Forbidden Actions**: Nunca entregue imagens promocionais de e-commerce que apresentem frascos desalinhados com a realidade física das garrafas de referência.
24: 
25: ## [CR-005] Gemini API Model Deprecation (2.5-flash 404 vs 3.5-flash)
26: - **Keywords**: gemini-2.5-flash, gemini-3.5-flash, 404 NOT_FOUND, API key, model deprecated
27: - **Root Cause**: O Google AI Studio descontinuou o acesso ao modelo `gemini-2.5-flash` na API pública para novos projetos e chaves de API, resultando em erros do tipo `404 NOT_FOUND` com a mensagem "is no longer available to new users". Apesar de o painel do AI Studio listar o modelo com limites de taxa, chamadas de código reais falham.
28: - **Technical Decision**: Todos os scripts do ecossistema Montalk (como `estagiariovisual.py`, `trazfragrantica2.py`, `trazfragrantica3.py`, `opiblog.py` e `render_profiles.py`) devem utilizar obrigatoriamente o modelo ativo `gemini-3.5-flash` para chamadas de IA.
29: - **Forbidden Actions**: Nunca utilize `gemini-2.5-flash` ou `gemini-2.5-flash-lite` para chamadas de API em novos scripts.
30: 
