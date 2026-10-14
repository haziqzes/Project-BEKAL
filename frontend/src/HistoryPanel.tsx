import { useEffect, useMemo, useState } from 'react'
import { PdfPreview } from './PdfPreview'
import type { Item, Receipt } from './ReviewPanel'

type Summary = { id: string; receipt_date: string | null; store_name: string | null; item_count: number; final_total: number | null; currency: 'MYR'; created_at: string }
type SavedItem = Item & { id?: string; review_flag: boolean }
type Detail = { id: string; receipt: Receipt; items: SavedItem[]; pdf_url: string }
type Row = SavedItem & { key: string }
const categories = ['Meat & Poultry', 'Seafood', 'Vegetables', 'Fruit', 'Dairy', 'Eggs', 'Rice & Grains', 'Bread & Bakery', 'Drinks', 'Snacks', 'Frozen Food', 'Canned / Packaged Food', 'Condiments', 'Household', 'Personal Care', 'Other']
const blank = (): Row => ({ key: crypto.randomUUID(), raw_name: '', display_name: '', quantity: null, unit: null, unit_price: null, line_total: null, category: 'Other', warnings: [], review_flag: true })
const money = (value: number | null) => value === null ? '—' : `MYR ${value.toFixed(2)}`
const numberValue = (text: string) => text.trim() ? Number(text) : null
const errorText = (detail: unknown, fallback: string) => typeof detail === 'string' ? detail : fallback

export function HistoryPanel({ openReceiptId }: { openReceiptId?: string | null }) {
  const [history, setHistory] = useState<Summary[]>([])
  const [selected, setSelected] = useState<Detail | null>(null)
  const [receipt, setReceipt] = useState<Receipt | null>(null)
  const [rows, setRows] = useState<Row[]>([])
  const [editingReceipt, setEditingReceipt] = useState(false)
  const [editingRow, setEditingRow] = useState<string | null>(null)
  const [draft, setDraft] = useState<Row>(blank())
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  async function loadHistory() {
    try {
      const response = await fetch('/api/receipts')
      if (!response.ok) throw new Error('Could not load receipt history.')
      setHistory(await response.json() as Summary[])
      setError('')
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not load receipt history.') }
  }
  useEffect(() => { void loadHistory() }, [])
  useEffect(() => { if (openReceiptId) void open(openReceiptId) }, [openReceiptId])

  async function open(id: string, edit = false) {
    setBusy(true); setError(''); setNotice('')
    try {
      const response = await fetch(`/api/receipts/${id}`)
      if (!response.ok) throw new Error('Could not load this receipt.')
      const result = await response.json() as Detail
      setSelected(result); setReceipt(result.receipt)
      setRows(result.items.map(item => ({ ...item, key: item.id ?? crypto.randomUUID() })))
      setEditingReceipt(edit); setEditingRow(null); setDeleteId(null)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not load this receipt.') }
    finally { setBusy(false) }
  }

  const reconciliation = useMemo(() => {
    if (!receipt) return ''
    if (!rows.length || rows.some(row => row.line_total === null)) return '⚠ Enter a line total for every item to compare totals.'
    const sum = rows.reduce((value, row) => value + Math.round((row.line_total ?? 0) * 100), 0)
    const reference = receipt.subtotal ?? receipt.final_total
    if (reference === null) return `⚠ Items: MYR ${(sum / 100).toFixed(2)}. Enter a subtotal or receipt total to compare.`
    const match = Math.abs(sum - Math.round(reference * 100)) <= 1
    if (!match) return `⚠ Items: MYR ${(sum / 100).toFixed(2)}; ${receipt.subtotal !== null ? 'subtotal' : 'receipt total'}: ${money(reference)}. Totals do not match.`
    if (receipt.subtotal !== null && receipt.final_total !== null && Math.abs(Math.round(receipt.subtotal * 100) - Math.round(receipt.final_total * 100)) > 1) {
      if (receipt.discount_total === null || receipt.tax_total === null) return '⚠ Items match subtotal; discount or tax is unknown. Check the original PDF.'
      const adjusted = receipt.subtotal - receipt.discount_total + receipt.tax_total
      return Math.abs(Math.round(adjusted * 100) - Math.round(receipt.final_total * 100)) <= 1 ? '✓ Items and receipt total reconcile.' : '⚠ Subtotal, discount, tax, and total do not reconcile.'
    }
    return '✓ Item totals reconcile.'
  }, [receipt, rows])

  function beginRow(row: Row) { setDraft({ ...row }); setEditingRow(row.key); setError('') }
  function saveRow() {
    if (!draft.display_name.trim()) { setError('Enter a product name.'); return }
    if (!categories.includes(draft.category)) { setError('Choose a predefined category.'); return }
    if ([draft.quantity, draft.unit_price, draft.line_total].some(value => value !== null && (!Number.isFinite(value) || value < 0))) { setError('Numbers must be zero or greater.'); return }
    setRows(current => current.map(row => row.key === editingRow ? { ...draft, display_name: draft.display_name.trim(), unit: draft.unit?.trim() || null } : row))
    setEditingRow(null); setError('')
  }
  async function saveReceipt() {
    if (!selected || !receipt || editingRow) return
    setBusy(true); setError(''); setNotice('')
    try {
      const response = await fetch(`/api/receipts/${selected.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ receipt, items: rows.map(row => ({ id: row.id ?? null, raw_name: row.raw_name || null, display_name: row.display_name, quantity: row.quantity,
          unit: row.unit, unit_price: row.unit_price, line_total: row.line_total, category: row.category, review_flag: row.review_flag })) }) })
      const result = await response.json()
      if (!response.ok) throw new Error(result.detail?.code === 'alias_conflict' ? 'This source name already belongs to another product. Review this correction.' : errorText(result.detail, 'Could not update the receipt. Saved data is unchanged.'))
      setSelected(result as Detail); setReceipt(result.receipt); setRows((result.items as SavedItem[]).map(item => ({ ...item, key: item.id ?? crypto.randomUUID() })))
      setEditingReceipt(false); setNotice('Receipt changes saved.'); await loadHistory()
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not update the receipt.') }
    finally { setBusy(false) }
  }
  async function remove(id: string) {
    setBusy(true); setError(''); setNotice('')
    try {
      const response = await fetch(`/api/receipts/${id}`, { method: 'DELETE' })
      const result = await response.json()
      if (!response.ok) throw new Error(errorText(result.detail, 'Could not delete the receipt.'))
      setSelected(null); setReceipt(null); setEditingReceipt(false); setDeleteId(null)
      setNotice(result.file_cleanup_pending ? 'Receipt deleted. Private file cleanup needs attention.' : result.pdf_missing ? 'Receipt deleted. Its original PDF was already missing.' : 'Receipt and original PDF deleted.')
      await loadHistory()
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not delete the receipt.') }
    finally { setBusy(false) }
  }
  const textField = (label: string, key: 'store_name' | 'receipt_date' | 'receipt_number' | 'payment_method', type = 'text') => <label className="field">{label}<input aria-label={label} type={type} disabled={!editingReceipt} value={receipt?.[key] ?? ''} onChange={event => setReceipt(current => current && ({ ...current, [key]: event.target.value || null }))} /></label>
  const amountField = (label: string, key: 'subtotal' | 'discount_total' | 'tax_total' | 'final_total') => <label className="field">{label}<input aria-label={label} type="number" min="0" step="0.01" disabled={!editingReceipt} value={receipt?.[key] ?? ''} onChange={event => setReceipt(current => current && ({ ...current, [key]: numberValue(event.target.value) }))} /></label>
  const rowNumber = (label: string, key: 'quantity' | 'unit_price' | 'line_total') => <label className="field">{label}<input aria-label={label} type="number" min="0" step={key === 'quantity' ? '0.001' : '0.01'} value={draft[key] ?? ''} onChange={event => setDraft(current => ({ ...current, [key]: numberValue(event.target.value) }))} /></label>

  return <section className="intake-panel" aria-label="Receipt History">
    <div className="section-heading"><h2>Receipt History</h2><button type="button" className="secondary" onClick={() => void loadHistory()}>Refresh</button></div>
    <div className="actions export-actions"><a className="download-link" href="/api/exports/receipts.csv" download="receipts.csv">Download receipts.csv</a><a className="download-link" href="/api/exports/items.csv" download="items.csv">Download items.csv</a></div>
    <p className="review-note">CSV downloads contain your saved receipt data. Keep them in private storage.</p>
    {notice && <p role="status" className="ready-state">{notice}</p>}{error && <p role="alert" className="error">{error}</p>}
    {!history.length ? <p>No saved receipts yet.</p> : <div className="table-scroll"><table><thead><tr><th>Date</th><th>Store</th><th>Items</th><th>Total</th><th>Actions</th></tr></thead><tbody>{history.map(row => <tr key={row.id}>
      <td>{row.receipt_date ?? 'Unknown'}</td><td>{row.store_name ?? 'Unknown'}</td><td>{row.item_count}</td><td>{money(row.final_total)}</td>
      <td className="row-actions"><button type="button" className="secondary" disabled={busy} onClick={() => void open(row.id)}>View</button><button type="button" className="secondary" disabled={busy} onClick={() => void open(row.id, true)}>Edit</button><button type="button" className="delete-button" disabled={busy} onClick={() => setDeleteId(row.id)}>Delete</button></td>
    </tr>)}</tbody></table></div>}
    {deleteId && <div className="confirm-panel" role="dialog" aria-label="Confirm receipt deletion"><p>Delete this saved receipt and its original PDF? This cannot be undone.</p><div className="actions"><button type="button" className="delete-button" disabled={busy} onClick={() => void remove(deleteId)}>Confirm delete</button><button type="button" className="secondary" onClick={() => setDeleteId(null)}>Cancel</button></div></div>}
    {selected && receipt && <div className="candidate">
      <div className="section-heading"><h3>Saved receipt</h3><div className="actions"><button type="button" className="secondary" onClick={() => { setSelected(null); setEditingReceipt(false) }}>Back to history</button>{!editingReceipt && <button type="button" onClick={() => setEditingReceipt(true)}>Edit receipt</button>}</div></div>
      <p className="review-note">Compare saved details with the original PDF. Changes remain in this form until you select Save changes.</p>
      <div className="candidate-content"><PdfPreview url={selected.pdf_url} /><section className="extraction-panel" aria-label="Saved receipt details"><h4>Receipt details</h4><div className="field-grid">{textField('Store', 'store_name')}{textField('Date', 'receipt_date', 'date')}{textField('Receipt number', 'receipt_number')}{textField('Payment method', 'payment_method')}{amountField('Subtotal (MYR)', 'subtotal')}{amountField('Discount (MYR)', 'discount_total')}{amountField('Tax (MYR)', 'tax_total')}{amountField('Receipt total (MYR)', 'final_total')}</div>
        <div className="section-heading"><h4>Items</h4>{editingReceipt && <button type="button" className="secondary" disabled={editingRow !== null} onClick={() => { const row = blank(); setRows(current => [...current, row]); beginRow(row) }}>Add missing item</button>}</div>
        <div className="table-scroll"><table><thead><tr><th>Review</th><th>Product</th><th>Category</th><th>Qty</th><th>Unit</th><th>Unit price</th><th>Line total</th>{editingReceipt && <th>Actions</th>}</tr></thead><tbody>{rows.map(row => <tr key={row.key}><td>{row.review_flag ? '⚠' : '✓'}</td><td>{row.display_name || 'New item'}{row.raw_name && row.raw_name !== row.display_name && <small className="raw-name">Source: {row.raw_name}</small>}</td><td>{row.category}</td><td>{row.quantity ?? '—'}</td><td>{row.unit ?? '—'}</td><td>{money(row.unit_price)}</td><td>{money(row.line_total)}</td>{editingReceipt && <td className="row-actions"><button type="button" className="icon-button" aria-label={`Edit ${row.display_name || 'new item'}`} disabled={editingRow !== null} onClick={() => beginRow(row)}>✎</button><button type="button" className="delete-button" aria-label={`Delete ${row.display_name || 'new item'}`} onClick={() => { setRows(current => current.filter(item => item.key !== row.key)); if (editingRow === row.key) setEditingRow(null) }}>Delete</button></td>}</tr>)}</tbody></table></div>
        {editingRow && <div className="row-editor" aria-label="Edit saved item row"><h5>Edit item</h5>{draft.raw_name && <p>Original item text: {draft.raw_name}</p>}<div className="field-grid"><label className="field">Product name<input aria-label="Product name" value={draft.display_name} onChange={event => setDraft(current => ({ ...current, display_name: event.target.value }))} /></label><label className="field">Category<select aria-label="Category" value={draft.category} onChange={event => setDraft(current => ({ ...current, category: event.target.value }))}>{categories.map(category => <option key={category}>{category}</option>)}</select></label>{rowNumber('Quantity', 'quantity')}<label className="field">Unit<input aria-label="Unit" value={draft.unit ?? ''} onChange={event => setDraft(current => ({ ...current, unit: event.target.value || null }))} /></label>{rowNumber('Unit price (MYR)', 'unit_price')}{rowNumber('Line total (MYR)', 'line_total')}<label className="field">Review state<select aria-label="Review state" value={draft.review_flag ? 'review' : 'checked'} onChange={event => setDraft(current => ({ ...current, review_flag: event.target.value === 'review' }))}><option value="review">Review recommended</option><option value="checked">Checked against PDF</option></select></label></div><div className="actions"><button type="button" onClick={saveRow}>Save row</button><button type="button" className="secondary" onClick={() => { if (!draft.id) setRows(current => current.filter(row => row.key !== draft.key)); setEditingRow(null); setError('') }}>Cancel</button></div></div>}
        <p className={reconciliation.startsWith('⚠') ? 'reconciliation warning' : 'reconciliation'} role="status">{reconciliation}</p>
        {editingReceipt && <div className="actions"><button type="button" disabled={busy || editingRow !== null || rows.length === 0} onClick={() => void saveReceipt()}>{busy ? 'Saving…' : 'Save changes'}</button><button type="button" className="secondary" onClick={() => void open(selected.id)}>Cancel changes</button></div>}
      </section></div>
    </div>}
  </section>
}
