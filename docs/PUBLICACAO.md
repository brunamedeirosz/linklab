# Apresentação e publicação do LinkLab

## Como apresentar o projeto

**Nome do repositório:** `linklab`

**Descrição para o campo About do GitHub:**

> Encurtador de URLs Full Stack com Django REST Framework e React. Interface responsiva, validação de URLs, testes automatizados e configuração Docker com PostgreSQL.

**Topics sugeridos:** `python`, `django`, `django-rest-framework`, `react`, `vite`, `javascript`, `url-shortener`, `sqlite`, `postgresql`, `docker`, `portfolio`.

**Resumo para apresentar no portfólio:**

> O LinkLab transforma URLs em links com códigos únicos, com uma interface focada em criar e copiar. Desenvolvi a integração React/Django, validação HTTP/HTTPS, tratamento de colisões e redirecionamento com persistência SQL. O projeto inclui testes de API e do cliente JavaScript, além de um teste de integração com os dois servidores. A execução local usa SQLite, com uma configuração alternativa de Docker e PostgreSQL que ainda precisa ser validada.

O projeto tem execução local. Não apresentar os links como compartilháveis publicamente, nem anunciar Docker, PostgreSQL ou CI como verificados antes dos testes nesses ambientes.

## Imagens para o README

O README inclui capturas reais da aplicação:

1. Tela inicial com a interface final clara, o título e o formulário.
2. Resultado de um endereço longo de exemplo, com o botão de cópia.
3. Tela inicial em viewport de celular de 390 × 844.

As imagens estão em `docs/screenshots/inicio.png`, `docs/screenshots/resultado.png` e `docs/screenshots/celular.png`, vinculadas ao README. Foram capturadas no Chrome com banco temporário e dados de exemplo, sem abas, credenciais ou informações pessoais. Para atualizar, usar a interface real e preservar a mesma identidade visual e proporções.

## Organização proposta dos commits

A sequência abaixo organiza o histórico inicial na branch `main` por responsabilidade. Os commits ainda não foram criados: a gravação do índice Git pelo agente foi bloqueada pelo controle de permissões. Não é necessário simular uma cronologia de implementação ou alterar datas de commits.

| Ordem | Mensagem | Arquivos |
| --- | --- | --- |
| 1 | `feat(api): implementa encurtamento e redirecionamento de links` | `.gitignore` e código Django em `backend/`, incluindo modelo, migração, validação, throttles, estatísticas, testes e `requirements.txt`; exceto arquivos Docker |
| 2 | `feat(frontend): adiciona interface responsiva para encurtar links` | Código e configuração em `frontend/`, incluindo testes JavaScript, exemplos de ambiente, assets e lockfile; exceto `Dockerfile`, `.dockerignore` e `README.md` |
| 3 | `build(docker): configura ambiente local com PostgreSQL` | `compose.yaml`, `.env.example` da raiz, Dockerfiles, arquivos `.dockerignore` e `backend/requirements-docker.txt` |
| 4 | `ci: adiciona verificações automáticas e teste de integração` | `.github/workflows/ci.yml` e `scripts/smoke_test.py` |
| 5 | `docs: documenta instalação, arquitetura e validação do projeto` | `README.md`, `frontend/README.md`, `docs/` e capturas, quando disponíveis |

As mensagens seguem `tipo(escopo): descrição`. Para os próximos trabalhos, usar `fix` para correções, `feat` para funcionalidades e `docs` para documentação. Cada commit deve reunir uma mudança compreensível; não precisa haver um commit para cada arquivo ou ajuste de cor.

Os commits locais foram autorizados pela autora. A publicação no GitHub é uma etapa separada.

### Refer?ncia dos comandos usados

Execute na raiz `C:\Users\bruna\linklab`, um grupo por vez. Confira o resumo antes de cada commit e pare se algum comando falhar. Esses comandos incluem somente os arquivos previstos para cada grupo; não publicam nada no GitHub.

**1. API e regras de exclusão:**

```powershell
git add -- .gitignore backend/manage.py backend/config backend/links backend/requirements.txt
git diff --cached --stat
git commit -m "feat(api): implementa encurtamento e redirecionamento de links"
```

**2. Interface e testes JavaScript:**

```powershell
git add -- frontend/.env.example frontend/.gitignore frontend/.oxlintrc.json frontend/index.html frontend/package.json frontend/package-lock.json frontend/vite.config.js frontend/src frontend/public
git diff --cached --stat
git commit -m "feat(frontend): adiciona interface responsiva para encurtar links"
```

**3. Ambiente Docker:**

```powershell
git add -- .env.example compose.yaml backend/Dockerfile backend/.dockerignore backend/requirements-docker.txt frontend/Dockerfile frontend/.dockerignore
git diff --cached --stat
git commit -m "build(docker): configura ambiente local com PostgreSQL"
```

**4. Verificações automáticas:**

```powershell
git add -- .github/workflows/ci.yml scripts/smoke_test.py
git diff --cached --stat
git commit -m "ci: adiciona verificações automáticas e teste de integração"
```

**5. Documentação:**

```powershell
git add -- README.md frontend/README.md docs
git diff --cached --stat
git commit -m "docs: documenta instalação, arquitetura e validação do projeto"
git status --short
git log -5 --oneline
```

## Revisão antes dos commits

- Reexecutar testes, lint, build e integração usando os comandos do README.
- Conferir se os exemplos `.env.example` e o lockfile aparecem entre os arquivos a incluir.
- Conferir se `.env`, bancos, `.venv`, `node_modules`, caches e builds estão ignorados.
- Verificar a identidade Git usada para autoria e escolher conscientemente o endereço de e-mail que aparecerá nos commits. É possível usar o endereço privado fornecido pelo GitHub nas configurações da conta.
- Revisar os arquivos selecionados antes de cada commit com `git diff --cached --stat` e `git diff --cached`.
- Decidir a licença antes de apresentar o projeto como open source. Nenhuma licença foi aplicada.

## Publicação após autorização

1. Criar os commits locais conforme a divisão revisada.
2. Criar um repositório vazio chamado `linklab` na conta escolhida. Como os arquivos locais já existem, não inicializar outro README, `.gitignore` ou licença pelo formulário do GitHub.
3. Configurar o remoto para o repositório escolhido e enviar `main`.
4. Conferir se os arquivos privados ficaram de fora, revisar o README renderizado e acompanhar o GitHub Actions.
5. Preencher About e topics. Se o projeto continuar sem hospedagem, deixar o campo de site vazio.

Os comandos abaixo são referência para essa etapa futura. Substituir `SEU_USUARIO`; eles não foram executados:

```powershell
git remote add origin https://github.com/SEU_USUARIO/linklab.git
git push -u origin main
```

Se a verificação com PostgreSQL ou o build no GitHub falhar, corrigir a causa e registrar um commit de correção. Não alterar o histórico publicado apenas para esconder falhas da primeira execução.

## Licença

A MIT é uma opção a avaliar para permitir reutilização com preservação dos avisos de autoria e licença. A aplicação depende de confirmação explícita da autora. A escolha e o texto estão discutidos no [README](../README.md#licença).
