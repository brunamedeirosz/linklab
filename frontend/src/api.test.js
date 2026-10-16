import { test, afterEach, mock } from 'node:test'
import assert from 'node:assert/strict'
import { createLink, getStatistics } from './api.js'

const link = {
  original_url: 'https://example.com', short_code: 'abc1234',
  short_url: 'http://localhost:8000/abc1234/', click_count: 0,
  created_at: '2026-10-15T12:00:00Z',
}
afterEach(() => mock.restoreAll())

function respond(body, status = 200, headers = {}) {
  return mock.method(globalThis, 'fetch', async () => new Response(JSON.stringify(body), {
    status, headers: { 'Content-Type': 'application/json', ...headers },
  }))
}

test('cria link com JSON e rota centralizada', async () => {
  const fetch = respond(link, 201)
  assert.deepEqual(await createLink(link.original_url), link)
  const [url, options] = fetch.mock.calls[0].arguments
  assert.equal(url, '/api/links/')
  assert.equal(options.method, 'POST')
  assert.equal(options.headers['Content-Type'], 'application/json')
  assert.deepEqual(JSON.parse(options.body), { original_url: link.original_url })
})
test('consulta e atualiza estatísticas', async () => {
  const fetch = respond({ ...link, click_count: 12 })
  assert.equal((await getStatistics(link.short_code)).click_count, 12)
  assert.equal(fetch.mock.calls[0].arguments[0], '/api/links/abc1234/stats/')
})
test('codifica o código ao montar a rota', async () => {
  const fetch = respond(link)
  await getStatistics('a/b')
  assert.equal(fetch.mock.calls[0].arguments[0], '/api/links/a%2Fb/stats/')
})
test('apresenta erro de validação da API', async () => {
  respond({ original_url: ['URL inválida.'] }, 400)
  await assert.rejects(createLink('invalid'), /URL inválida/)
})
test('apresenta erro de código inexistente', async () => {
  respond({ detail: 'Link não encontrado.' }, 404)
  await assert.rejects(getStatistics('missing'), /Link não encontrado/)
})
test('apresenta tempo de espera no limite de requisições', async () => {
  respond({ detail: 'Throttled' }, 429, { 'Retry-After': '20' })
  await assert.rejects(createLink(link.original_url), /20 segundos/)
})
test('trata falha de conexão', async () => {
  mock.method(globalThis, 'fetch', async () => { throw new TypeError('Failed to fetch') })
  await assert.rejects(createLink(link.original_url), /backend está em execução/)
})
test('trata resposta HTML do proxy indisponível', async () => {
  mock.method(globalThis, 'fetch', async () => new Response('<html>Bad gateway</html>', { status: 502 }))
  await assert.rejects(createLink(link.original_url), /Não foi possível concluir/)
})
test('rejeita respostas malformadas e links com esquema perigoso', async () => {
  for (const body of [{}, { ...link, short_url: 'javascript:alert(1)' },
    { ...link, short_url: 'invalid' }, { ...link, click_count: '0' },
    { ...link, created_at: 'invalid' }]) {
    const fetch = respond(body)
    await assert.rejects(createLink(link.original_url), /resposta inesperada/)
    fetch.mock.restore()
  }
})
