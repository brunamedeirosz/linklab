const API_BASE = (import.meta.env?.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

async function request(path, options) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, options)
  } catch {
    throw new Error('Não foi possível conectar à API. Verifique se o backend está em execução.')
  }
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status === 429) {
      const seconds = response.headers.get('Retry-After')
      throw new Error(`Muitas solicitações. ${seconds ? `Tente novamente em ${seconds} segundos.` : 'Aguarde um minuto e tente novamente.'}`)
    }
    throw new Error(data?.original_url?.[0] || data?.detail || 'Não foi possível concluir a solicitação. Tente novamente.')
  }
  let validUrl = false
  try {
    validUrl = ['http:', 'https:'].includes(new URL(data?.short_url).protocol)
  } catch { /* Respostas inválidas recebem a mesma mensagem abaixo. */ }
  if (!data?.short_code || !validUrl || !Number.isInteger(data.click_count) || !Number.isFinite(Date.parse(data.created_at))) {
    throw new Error('A API retornou uma resposta inesperada.')
  }
  return data
}

export function createLink(url) {
  return request('/links/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original_url: url }),
  })
}

export function getStatistics(code) {
  return request(`/links/${encodeURIComponent(code)}/stats/`)
}
