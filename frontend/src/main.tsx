import { StrictMode, useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { PdfPreview } from './PdfPreview'
import './style.css'

type HealthState = 'checking' | 'healthy' | 'unavailable'
type Candidate = { id: string; expires_at: string; preview_url: string }

function App() {
  const [backend, setBackend] = useState<HealthState>('checking')
  const [postgres, setPostgres] = useState<HealthState>('checking')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [working, setWorking] = useState(false)
  const [error, setError] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function check(path: string, update: (state: HealthState) => void) {
      try {
        const response = await fetch(path, { signal: controller.signal })
        update(response.ok ? 'healthy' : 'unavailable')
      } catch (error) {
        if (!controller.signal.aborted) {
          update('unavailable')
        }
      }
    }

    void check('/api/health', setBackend)
    void check('/api/health/db', setPostgres)
    return () => controller.abort()
  }, [])

  async function upload() {
    if (!selectedFile) return
    setError('')
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Choose a PDF file.')
      return
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('PDF must be 10 MiB or smaller.')
      return
    }

    setWorking(true)
    try {
      const body = new FormData()
      body.append('file', selectedFile)
      const response = await fetch('/api/candidates', { method: 'POST', body })
      if (!response.ok) {
        const result: { detail?: string } = await response.json()
        throw new Error(result.detail ?? 'The PDF could not be accepted.')
      }
      const next: Candidate = await response.json()
      setCandidate(next)
      if (candidate) {
        void fetch(`/api/candidates/${candidate.id}`, { method: 'DELETE' }).catch(() => {})
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'The PDF could not be accepted.')
    } finally {
      setWorking(false)
    }
  }

  async function discard() {
    if (!candidate) return
    setWorking(true)
    try {
      await fetch(`/api/candidates/${candidate.id}`, { method: 'DELETE' })
      setCandidate(null)
      setSelectedFile(null)
      if (fileInput.current) fileInput.current.value = ''
      setError('')
    } catch {
      setError('Could not discard the temporary PDF. It will expire automatically.')
    } finally {
      setWorking(false)
    }
  }

  return (
    <main className="shell">
      <header>
        <p className="eyebrow">Project BEKAL · V0.1 receipt intake</p>
        <h1>Receipt data, under your control.</h1>
        <p className="intro">
          Select a PDF receipt to validate and preview it. This temporary candidate is not saved as a receipt.
        </p>
      </header>

      <section aria-labelledby="intake-heading" className="intake-panel">
        <h2 id="intake-heading">Select a receipt PDF</h2>
        <label htmlFor="receipt-file">PDF file (10 MiB maximum)</label>
        <input
          id="receipt-file"
          ref={fileInput}
          type="file"
          accept=".pdf,application/pdf"
          onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
        />
        <div className="actions">
          <button type="button" onClick={() => void upload()} disabled={!selectedFile || working}>
            {working ? 'Working…' : 'Validate and preview'}
          </button>
          {candidate && <button type="button" className="secondary" onClick={() => void discard()} disabled={working}>Discard preview</button>}
        </div>
        {error && <p role="alert" className="error">{error}</p>}
        {candidate && (
          <div className="candidate">
            <p><strong>Temporary receipt ID:</strong> <code>{candidate.id}</code></p>
            <p>Expires {new Date(candidate.expires_at).toLocaleString()} or when the backend restarts.</p>
            <PdfPreview url={candidate.preview_url} />
          </div>
        )}
      </section>

      <section aria-labelledby="status-heading" className="status-panel">
        <h2 id="status-heading">Service status</h2>
        <div className="status-row"><span>Frontend</span><strong>healthy</strong></div>
        <div className="status-row"><span>Backend</span><strong>{backend}</strong></div>
        <div className="status-row"><span>PostgreSQL</span><strong>{postgres}</strong></div>
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
