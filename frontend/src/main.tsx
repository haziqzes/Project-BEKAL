import { StrictMode, useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { PdfPreview } from './PdfPreview'
import './style.css'

type HealthState = 'checking' | 'healthy' | 'unavailable'
type Candidate = { id: string; expires_at: string; preview_url: string }
type ReceiptData = {
  store_name: string | null
  receipt_date: string | null
  receipt_number: string | null
  payment_method: string | null
  subtotal: number | null
  discount_total: number | null
  tax_total: number | null
  final_total: number | null
  currency: 'MYR'
}
type ItemData = {
  display_name: string
  quantity: number | null
  unit: string | null
  unit_price: number | null
  line_total: number | null
}
type ExtractionData = {
  candidate_id: string
  extraction_method: 'embedded_text' | 'ocr'
  extraction_status: 'extracted' | 'no_data'
  receipt: ReceiptData
  items: ItemData[]
}

function money(value: number | null): string {
  return value === null ? '—' : value.toFixed(2)
}

function App() {
  const [backend, setBackend] = useState<HealthState>('checking')
  const [postgres, setPostgres] = useState<HealthState>('checking')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [working, setWorking] = useState(false)
  const [error, setError] = useState('')
  const [extraction, setExtraction] = useState<ExtractionData | null>(null)
  const [extracting, setExtracting] = useState(false)
  const [extractionError, setExtractionError] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)
  const activeCandidateId = useRef<string | null>(null)

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

  async function extract(candidateId: string) {
    setExtracting(true)
    setExtractionError('')
    try {
      const response = await fetch(`/api/candidates/${candidateId}/extract`, { method: 'POST' })
      if (!response.ok) throw new Error('Could not extract this receipt. The candidate may have expired.')
      const result: ExtractionData = await response.json()
      if (activeCandidateId.current === candidateId) setExtraction(result)
    } catch (cause) {
      if (activeCandidateId.current === candidateId) {
        setExtractionError(cause instanceof Error ? cause.message : 'Extraction failed.')
      }
    } finally {
      if (activeCandidateId.current === candidateId) setExtracting(false)
    }
  }

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
      activeCandidateId.current = next.id
      setCandidate(next)
      setExtraction(null)
      void extract(next.id)
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
      activeCandidateId.current = null
      setExtraction(null)
      setExtracting(false)
      setExtractionError('')
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
        <p className="eyebrow">Project BEKAL · V0.1 receipt extraction</p>
        <h1>Receipt data, under your control.</h1>
        <p className="intro">
          Select a PDF receipt to preview it and extract temporary candidate data. Nothing is saved as a receipt yet.
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
            <button type="button" className="secondary" disabled={extracting || working} onClick={() => void extract(candidate.id)}>
              {extracting ? 'Extracting…' : 'Extract again'}
            </button>
            <div className="candidate-content">
              <PdfPreview url={candidate.preview_url} />
              <section className="extraction-panel" aria-label="Extracted candidate data" aria-live="polite">
                <h3>Extracted candidate</h3>
                {extracting && <p>Extracting receipt text…</p>}
                {extractionError && <p role="alert" className="error">{extractionError}</p>}
                {extraction && (
                  <>
                    <p><strong>Method:</strong> {extraction.extraction_method === 'ocr' ? 'Local OCR' : 'Embedded text'}</p>
                    <p><strong>Status:</strong> {extraction.extraction_status === 'extracted' ? 'Candidate data found' : 'No structured data found'}</p>
                    <dl className="metadata">
                      <dt>Store</dt><dd>{extraction.receipt.store_name ?? '—'}</dd>
                      <dt>Date</dt><dd>{extraction.receipt.receipt_date ?? '—'}</dd>
                      <dt>Receipt number</dt><dd>{extraction.receipt.receipt_number ?? '—'}</dd>
                      <dt>Payment</dt><dd>{extraction.receipt.payment_method ?? '—'}</dd>
                      <dt>Subtotal (MYR)</dt><dd>{money(extraction.receipt.subtotal)}</dd>
                      <dt>Discount (MYR)</dt><dd>{money(extraction.receipt.discount_total)}</dd>
                      <dt>Tax (MYR)</dt><dd>{money(extraction.receipt.tax_total)}</dd>
                      <dt>Total (MYR)</dt><dd>{money(extraction.receipt.final_total)}</dd>
                    </dl>
                    <h4>Line items</h4>
                    {extraction.items.length === 0 ? <p>No line items identified.</p> : (
                      <div className="table-scroll">
                        <table>
                          <thead><tr><th>Item text</th><th>Qty</th><th>Unit</th><th>Unit price</th><th>Line total</th></tr></thead>
                          <tbody>{extraction.items.map((item, index) => (
                            <tr key={`${item.display_name}-${index}`}>
                              <td>{item.display_name}</td>
                              <td>{item.quantity ?? '—'}</td>
                              <td>{item.unit ?? '—'}</td>
                              <td>{money(item.unit_price)}</td>
                              <td>{money(item.line_total)}</td>
                            </tr>
                          ))}</tbody>
                        </table>
                      </div>
                    )}
                  </>
                )}
              </section>
            </div>
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
