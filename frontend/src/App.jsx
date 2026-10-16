import { useRef, useState } from 'react'
import { createLink } from './api'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [link, setLink] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const inputRef = useRef(null)
  const resultRef = useRef(null)

  async function handleSubmit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setLink(null)
    setCopied(false)

    try {
      const data = await createLink(url.trim())
      setLink(data)
      requestAnimationFrame(() => resultRef.current?.focus())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(link.short_url)
      setError('')
      setCopied(true)
    } catch {
      setError('Não foi possível copiar. Selecione o link e copie manualmente.')
    }
  }

  function reset() {
    setLink(null)
    setUrl('')
    setError('')
    setCopied(false)
    requestAnimationFrame(() => inputRef.current?.focus())
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#encurtador">Ir para o encurtador</a>
      <header className="header">
        <a className="logo" href="/" aria-label="LinkLab — início">
          Link<span className="logo-accent">Lab</span>
        </a>
      </header>

      <main>
        <section className="hero" aria-labelledby="title">
          <h1 id="title">Menos URL.<br /><span>Mais possibilidades.</span></h1>
          <p className="hero-description">Links mais simples, <mark>prontos para compartilhar</mark> no WhatsApp, Instagram, TikTok e onde você quiser de graça.</p>

          <section className="shortener" id="encurtador" aria-labelledby="form-title">
            <h2 id="form-title" className="sr-only">{link ? 'Seu link está pronto' : 'Encurte seu link'}</h2>
            {!link && <form onSubmit={handleSubmit} aria-busy={loading}>
              <label htmlFor="original-url" className="sr-only">URL original</label>
              <div className="input-row">
                <span className="input-icon" aria-hidden="true">↗</span>
                <input
                  ref={inputRef}
                  id="original-url"
                  name="original_url"
                  type="url"
                  placeholder="Cole seu link com https://"
                  value={url}
                  onChange={(event) => { setUrl(event.target.value); setError('') }}
                  disabled={loading}
                  maxLength={2048}
                  autoComplete="url"
                  autoCapitalize="none"
                  autoCorrect="off"
                  spellCheck={false}
                  inputMode="url"
                  enterKeyHint="go"
                  aria-describedby="url-help"
                  required
                />
                <button className="primary" type="submit" disabled={loading}>
                  {loading && <span className="spinner" aria-hidden="true" />}
                  {loading ? 'Encurtando...' : 'Encurtar link'}
                </button>
              </div>
              <p className="field-help" id="url-help">Sem cadastro, sem complicação.</p>
            </form>}
            <p className="sr-only" role="status">{loading ? 'Criando seu link.' : ''}</p>
            {error && <p className="error" role="alert">{error}</p>}
            {link && <section className="result" aria-labelledby="result-title">
              <div className="result-heading">
                <h3 id="result-title" tabIndex={-1} ref={resultRef}><span className="success-mark" aria-hidden="true">✓</span> Pronto para compartilhar.</h3>
              </div>
              <div className="short-link-row">
                <a href={link.short_url} target="_blank" rel="noreferrer">{link.short_url}</a>
                <button className={`copy-button${copied ? ' is-copied' : ''}`} type="button" onClick={handleCopy}>
                  <svg className="copy-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    {copied
                      ? <path d="m5 12 4 4L19 6" />
                      : <><rect x="8" y="8" width="12" height="12" rx="2" /><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3" /></>}
                  </svg>
                  {copied ? 'Copiado!' : 'Copiar link'}
                </button>
              </div>
              <span className="sr-only" role="status">{copied ? 'Link copiado para a área de transferência.' : ''}</span>
              <div className="result-actions">
                <button className="text-button" type="button" onClick={reset}>Encurtar outro <span aria-hidden="true">↗</span></button>
              </div>
            </section>}
          </section>

        </section>

      </main>

      <footer className="footer">
        <p><span className="footer-brand">LinkLab</span><span className="footer-divider" aria-hidden="true">·</span>Desenvolvido por <a href="https://github.com/brunamedeirosz" target="_blank" rel="noreferrer">Bruna Medeiros</a></p>
        <a className="footer-repository" href="https://github.com/brunamedeirosz/linklab" target="_blank" rel="noreferrer">Ver projeto no GitHub <span aria-hidden="true">↗</span></a>
      </footer>

    </div>
  )
}

export default App
