import { StrictMode, useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { PdfPreview } from './PdfPreview'
import { ReviewPanel, type Review, type SavedReceipt } from './ReviewPanel'
import { HistoryPanel } from './HistoryPanel'
import { DashboardPanel } from './DashboardPanel'
import { apiUrl } from './api'
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
  review: Review
  categories: string[]
}

const CATEGORIES = [
  'Meat & Poultry', 'Seafood', 'Vegetables', 'Fruit', 'Dairy', 'Eggs',
  'Rice & Grains', 'Bread & Bakery', 'Drinks', 'Snacks', 'Frozen Food',
  'Canned / Packaged Food', 'Condiments', 'Household', 'Personal Care', 'Other',
]

function manualExtraction(candidateId: string): ExtractionData {
  return { candidate_id: candidateId, extraction_method: 'embedded_text', extraction_status: 'no_data',
    receipt: { store_name: null, receipt_date: null, receipt_number: null, payment_method: null,
      subtotal: null, discount_total: null, tax_total: null, final_total: null, currency: 'MYR' },
    items: [], categories: CATEGORIES,
    review: { receipt: { store_name: null, receipt_date: null, receipt_number: null, payment_method: null,
      subtotal: null, discount_total: null, tax_total: null, final_total: null, currency: 'MYR' }, items: [] } }
}

function App() {
  const [view, setView] = useState<'intake' | 'history' | 'dashboard'>('intake')
  const [historyTarget, setHistoryTarget] = useState<string | null>(null)
  const [backend, setBackend] = useState<HealthState>('checking')
  const [postgres, setPostgres] = useState<HealthState>('checking')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [working, setWorking] = useState(false)
  const [error, setError] = useState('')
  const [extraction, setExtraction] = useState<ExtractionData | null>(null)
  const [extracting, setExtracting] = useState(false)
  const [extractionError, setExtractionError] = useState('')
  const [savedReceipt, setSavedReceipt] = useState<SavedReceipt | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)
  const activeCandidateId = useRef<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function check(path: string, update: (state: HealthState) => void) {
      try {
        const response = await fetch(apiUrl(path), { signal: controller.signal })
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
    setExtraction(null)
    try {
      const response = await fetch(apiUrl(`/api/candidates/${candidateId}/extract`), { method: 'POST' })
      if (!response.ok) throw new Error(response.status === 404 ? 'The temporary candidate expired. Upload the PDF again.' : 'Extraction failed. Enter the receipt details manually while checking the original PDF.')
      const result: ExtractionData = await response.json()
      if (activeCandidateId.current === candidateId) setExtraction(result)
    } catch (cause) {
      if (activeCandidateId.current === candidateId) {
        setExtractionError(cause instanceof Error ? cause.message : 'Extraction failed.')
        if (!(cause instanceof Error) || !cause.message.includes('expired')) setExtraction(manualExtraction(candidateId))
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
      const response = await fetch(apiUrl('/api/candidates'), { method: 'POST', body })
      if (!response.ok) {
        const result: { detail?: string } = await response.json()
        throw new Error(result.detail ?? 'The PDF could not be accepted.')
      }
      const next: Candidate = await response.json()
      setSavedReceipt(null)
      activeCandidateId.current = next.id
      setCandidate(next)
      setExtraction(null)
      void extract(next.id)
      if (candidate) {
        void fetch(apiUrl(`/api/candidates/${candidate.id}`), { method: 'DELETE' }).catch(() => {})
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
      await fetch(apiUrl(`/api/candidates/${candidate.id}`), { method: 'DELETE' })
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

  function handleSaved(result: SavedReceipt) {
    setSavedReceipt(result)
    setCandidate(null)
    activeCandidateId.current = null
    setExtraction(null)
    setSelectedFile(null)
    if (fileInput.current) fileInput.current.value = ''
  }

  return (
    <main className="shell">
      <header>
        <p className="eyebrow">Project BEKAL · V0.1 receipt review</p>
        <h1>Receipt data, under your control.</h1>
        <p className="intro">
          {view === 'intake' ? 'Select a PDF receipt, compare its extracted details with the original, and correct a temporary candidate. Nothing is saved until you confirm.' : view === 'history' ? 'Review saved receipts, compare their details with the original PDFs, and explicitly save changes or confirm deletion.' : 'See a simple monthly overview of permanently saved receipts.'}
        </p>
      </header>

      <nav className="main-nav" aria-label="Main navigation"><button type="button" className={view === 'intake' ? '' : 'secondary'} onClick={() => setView('intake')}>Receipt intake</button><button type="button" className={view === 'history' ? '' : 'secondary'} onClick={() => { setHistoryTarget(null); setView('history') }}>Receipt History</button><button type="button" className={view === 'dashboard' ? '' : 'secondary'} onClick={() => setView('dashboard')}>Dashboard</button></nav>

      {view === 'dashboard' ? <DashboardPanel onOpenReceipt={id => { setHistoryTarget(id); setView('history') }} /> : view === 'history' ? <HistoryPanel openReceiptId={historyTarget} /> : <>

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
        {savedReceipt && <div className="saved-result" role="status"><strong>Receipt saved privately.</strong><p>ID: <code>{savedReceipt.id}</code></p><p>{savedReceipt.store_name ?? 'Unknown store'} · {savedReceipt.receipt_date ?? 'Date unknown'} · {savedReceipt.item_count} item(s) · Total: {savedReceipt.final_total === null ? 'Unknown' : `MYR ${savedReceipt.final_total.toFixed(2)}`}</p></div>}
        {candidate && (
          <div className="candidate">
            <p><strong>Temporary receipt ID:</strong> <code>{candidate.id}</code></p>
            <p>Expires {new Date(candidate.expires_at).toLocaleString()} or when the backend restarts.</p>
            <button type="button" className="secondary" disabled={extracting || working} onClick={() => void extract(candidate.id)}>
              {extracting ? 'Extracting…' : 'Extract again'}
            </button>
            <div className="candidate-content">
              <PdfPreview url={apiUrl(candidate.preview_url)} />
              <section className="extraction-panel" aria-label="Extracted candidate data" aria-live="polite">
                {extracting && <p>Extracting receipt text…</p>}
                {extractionError && <p role="alert" className="error">{extractionError}</p>}
                {extraction && <ReviewPanel review={extraction.review} categories={extraction.categories} method={extraction.extraction_status === 'no_data' ? 'manual' : extraction.extraction_method} candidateId={candidate.id} onSaved={handleSaved} />}
              </section>
            </div>
          </div>
        )}
      </section>
      </>}

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
