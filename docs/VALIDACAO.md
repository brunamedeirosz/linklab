# Auditoria e validação do LinkLab

Registro em **15 de outubro de 2026**, no ambiente Windows/PowerShell da autora.

## Estado inicial e decisões

A estrutura real continha os projetos Django e React/Vite descritos na solicitação. Os endpoints de criação, estatísticas e redirecionamento já existiam, assim como o uso de `secrets`, cinco tentativas em colisões e incremento com `F()`. Esses comportamentos e a migração inicial foram preservados. O banco local existente não foi substituído.

Principais pontos encontrados e tratados:

| Achado | Alteração |
| --- | --- |
| Validação padrão de URL também permitia FTP | Validação explícita de HTTP/HTTPS no serializer |
| URLs podiam conter credenciais | Rejeição de usuário/senha no endereço |
| Ausência de proteção básica por frequência | Throttles separados para criação e estatísticas |
| Chave Django fixa no código | Variável de ambiente ou chave temporária em desenvolvimento |
| Qualquer IntegrityError era tratado como colisão | Nova tentativa apenas quando o código já existe; outras falhas são propagadas |
| Estatísticas não devolviam short_url | Representação única no serializer para criação e consulta |
| Redirecionamento aceitava métodos impróprios | GET/HEAD; apenas GET incrementa; resposta sem cache |
| Não havia proteção explícita de rotas reservadas | Rejeição de códigos reservados antes de gravar |
| Interface com acessibilidade incompleta | Labels, foco visível, cópia e confirmação acessíveis; estatísticas mantidas na API |
| Erros de rede e respostas inválidas pouco claros | Cliente da API centralizado com mensagens específicas |
| Testes Python eram apenas o arquivo padrão | Suíte de API e teste PostgreSQL de acessos simultâneos |
| Faltavam configuração reproduzível e documentação | Requirements, Dockerfiles, Compose, exemplos de ambiente e README |
| .gitignore passou a ignorar também os exemplos de ambiente | Exceção explícita para `.env.example` |

Não foram introduzidos login, autenticação de usuários da API, Redis, Celery, Nginx, TypeScript nem hospedagem. O admin e a estrutura padrão Django existentes foram preservados. Os arquivos de imagem do template que já existiam foram mantidos, embora não sejam utilizados pela interface atual.

A interface final prioriza colar, encurtar e copiar. Acessos e datas continuam dispon?veis na API, mas foram retirados da tela por escolha de produto. WhatsApp e QR Code n?o fazem parte do escopo. A identidade visual final usa fundo claro, ?ndigo e verde-s?lvia, com logo tipogr?fica.

## Arquivos principais criados ou modificados

- **Backend:** `config/settings.py`, `links/views.py`, `links/serializers.py`, `links/throttles.py`, `links/tests.py`, `requirements.txt`, `requirements-docker.txt`, `Dockerfile` e `.dockerignore`.
- **Frontend:** `src/App.jsx`, `src/App.css`, `src/index.css`, `src/api.js`, `src/api.test.js`, `index.html`, `public/favicon.svg`, `vite.config.js`, `package.json`, `package-lock.json`, `.env.example`, `README.md`, `Dockerfile` e `.dockerignore`.
- **Raiz e ferramentas:** `README.md`, `.gitignore`, `.env.example`, `compose.yaml`, `.github/workflows/ci.yml`, `scripts/smoke_test.py` e este registro.

## Verificações executadas

| Verificação | Resultado |
| --- | --- |
| Python | 3.14.8 |
| Django / DRF instalados | 6.1.2 / 3.18.3 |
| Node / npm | 24.22.0 / 11.19.1 |
| React / Vite instalados | 19.3.1 / 8.3.4 |
| `python -m pip check` | Sem incompatibilidades declaradas |
| `python manage.py check` | Nenhum problema identificado |
| `python manage.py makemigrations --check --dry-run` | Nenhuma migração pendente |
| `python manage.py test links` | 17 encontrados: 16 aprovados, 1 ignorado por exigir PostgreSQL |
| `npm test` | 9 aprovados |
| `npm run lint` | Concluído sem erros |
| `npm run build` | Bundle gerado com sucesso |
| `scripts/smoke_test.py` | Página Vite, criação pelo proxy, HTTP 302 e estatísticas com 1 acesso aprovados |
| Chrome com interface real | Criação por formulário, substituição pelo resultado, foco no título e reinício com foco no campo aprovados |
| Viewport de celular de 390 × 844 | Largura de conteúdo de 390 px, sem rolagem horizontal; captura inspecionada |
| Capturas de tela | Inicial e resultado em 1.440 × 900; celular em 390 × 844, com banco temporário e perfil de navegador isolado |
| Git | Git 2.56.0 disponível; nenhum arquivo versionado na revisão |
| Regras de exclusão do Git | SQLite, ambiente virtual, node_modules, dist, cache e resultados de teste ignorados; exemplos de ambiente e lockfile disponíveis para inclusão |

O teste de integração usa processos reais e banco temporário. Ele não executa JavaScript no navegador nem visita o endereço externo do link.

O download de bibliotecas adicionais de teste de interface foi recusado pelo controle de permissões. A alternativa implementada usa o executor nativo do Node, sem dependências adicionais. Os testes JavaScript verificam o cliente da API com respostas simuladas.

## Pendências de validação

- **Docker Compose e PostgreSQL:** Docker não está disponível no terminal. Dockerfiles, Compose e a conexão PostgreSQL foram preparados, mas não executados aqui. A aprovação dos testes com SQLite não valida PostgreSQL.
- **Concorrência real:** o teste usa vinte redirecionamentos com cinco threads e conexões independentes; só é executado com PostgreSQL. Execute `docker compose exec backend python manage.py test` quando o Compose estiver ativo.
- **GitHub Actions:** workflow publicado para SQLite, PostgreSQL e frontend; resultados remotos ainda não consultados nesta validação.
- **Navegador:** capturas reais inspecionadas em desktop e viewport de celular; criação, resultado, foco e reinício verificados no Chrome. A cópia para a área de transferência, navegação completa por teclado e dispositivos físicos ainda precisam de revisão manual.
- **Instalação limpa:** foram verificadas as dependências já instaladas e seus metadados; não foi feita uma reinstalação completa em uma máquina limpa.
- **Licença:** aguarda escolha da autora; nenhum arquivo `LICENSE` foi criado.

## Roteiro de revisão manual

1. Inicie backend e frontend conforme o [guia técnico](GUIA_TECNICO.md) e abra `http://localhost:5173`.
2. Crie um link para `https://example.com/caminho-de-exemplo` e confira que o resultado substitui o formulário e recebe foco.
3. Use o botão de cópia, cole o resultado em um campo de texto e confirme o endereço.
4. Abra o link curto em outra aba e confira o redirecionamento. O contador pode ser consultado pela API, conforme o guia técnico; não aparece na interface.
5. Use **Encurtar outro** e confirme que o formulário reaparece com campo vazio e foco para digitar.
6. Teste URL incompleta e `ftp://example.com`; a criação deve ser impedida ou retornar mensagem clara.
7. Pare o backend, tente criar um link e confira o tratamento da falha; depois reinicie-o.
8. Navegue com Tab e Shift+Tab; verifique labels, foco visível e mensagens. Teste Enter para enviar o formulário.
9. Confira a tela com aproximadamente 360 px e 1.280 px de largura, sem rolagem horizontal.
10. Execute o Compose, repita o fluxo e confira os testes com PostgreSQL. Use `docker compose down` para parar preservando o volume.

## Antes de publicar

Revise `git status --short --untracked-files=all` e confirme que nenhum arquivo privado aparece. O `.gitignore` não remove segredos de um histórico já existente. Nesta revisão, `git ls-files` estava vazio, e não foram feitos staging, commits, configuração de remoto ou push.

A publicação de atualizações e a aplicação de uma licença dependem da autorização da autora. As instruções de execução estão no [guia técnico](GUIA_TECNICO.md).
