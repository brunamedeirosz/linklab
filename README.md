# LinkLab

**Menos URL. Mais possibilidades.**

Encurtador de URLs com uma experiência direta: cole um endereço, gere seu link e copie para compartilhar. Uma interface leve, com fundo claro e identidade em índigo e verde-sálvia.

Projeto Full Stack de portfólio, desenvolvido com **Python, Django REST Framework e React**, conectando interface, API REST e persistência de dados.

![Tela inicial do LinkLab com conteúdo centralizado e rodapé](docs/screenshots/inicio.png?v=20261016)

## Uma experiência simples

- **Crie seu link:** um campo de URL e uma ação principal, sem cadastro.
- **Copie e compartilhe:** o resultado substitui o formulário, com confirmação visual ao copiar.
- **Comece de novo:** gere outro link sem recarregar a página.
- **Use no celular:** layout adaptável, botões com área de toque confortável e links longos com quebra de linha.

A interface também conta com indicador de carregamento, mensagens de erro, labels acessíveis e gerenciamento de foco entre o formulário e o resultado.

## O resultado

![Resultado do encurtamento, com opções de copiar e criar outro link](docs/screenshots/resultado.png?v=20261016)

<details>
<summary><strong>Veja a versão para celular</strong></summary>

<br />
<img src="docs/screenshots/celular.png?v=20261016" alt="Tela inicial do LinkLab em um celular, com conteúdo centralizado e rodapé" width="320" />

</details>

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Interface | React, JavaScript, Vite e CSS |
| API | Python, Django e Django REST Framework |
| Persistência | SQLite, com configuração alternativa para PostgreSQL |
| Ambiente | Docker e Docker Compose |
| Qualidade | Django Test Runner, Node Test Runner, Oxlint e GitHub Actions |

## Por trás dos links

Ao receber uma URL, a API valida o endereço, gera um código aleatório e salva a associação no banco. Quando esse código é acessado, o Django encontra o destino e responde com um redirecionamento HTTP 302.

```text
React → API Django → Banco de dados
                         ↓
Link gerado → Código → URL original
```

O backend inclui validação HTTP/HTTPS, unicidade de códigos com tratamento de colisões, proteção de rotas reservadas e limitação básica de requisições. A contagem de acessos usa atualização atômica no banco; estatísticas permanecem disponíveis pela API, enquanto a interface prioriza criar e copiar.

Os testes cobrem criação, validação, redirecionamentos, colisões e respostas de erro. O projeto também tem um teste de integração que inicia Django e Vite para verificar a comunicação entre os servidores.

## Sobre o projeto

O LinkLab reúne decisões de interface, integração entre frontend e backend e práticas de qualidade em uma aplicação pequena e com propósito definido.

A versão deste repositório é executada localmente. Os endereços exibidos nas capturas pertencem ao ambiente de demonstração; não representam um serviço público hospedado.

[Guia técnico: instalação, configuração, API e testes](docs/GUIA_TECNICO.md)

Desenvolvido por [@brunamedeirosz](https://github.com/brunamedeirosz).
