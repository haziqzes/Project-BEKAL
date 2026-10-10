import { useEffect, useMemo, useState } from 'react'

export type Receipt = {
  store_name: string | null; receipt_date: string | null; receipt_number: string | null
  payment_method: string | null; subtotal: number | null; discount_total: number | null
  tax_total: number | null; final_total: number | null; currency: 'MYR'
}
export type Item = {
  raw_name: string; display_name: string; quantity: number | null; unit: string | null
  unit_price: number | null; line_total: number | null; category: string; warnings: string[]
}
export type Review = { receipt: Receipt; items: Item[] }
export type SavedReceipt = { status: 'stored'; id: string; store_name: string | null; receipt_date: string | null; item_count: number; final_total: number | null }
type Row = Item & { id: string; reviewed: boolean }
type NumericKey = 'subtotal' | 'discount_total' | 'tax_total' | 'final_total'

const emptyItem = (): Item => ({ raw_name: '', display_name: '', quantity: null, unit: null,
  unit_price: null, line_total: null, category: 'Other', warnings: [] })
const money = (value: number | null) => value === null ? '—' : value.toFixed(2)
const numberValue = (value: string) => value.trim() === '' ? null : Number(value)
const cents = (value: number) => Math.round((value + Number.EPSILON) * 100)

function itemWarnings(row: Row): string[] {
  const warnings: string[] = []
  if (!row.display_name.trim()) warnings.push('Product name needs review')
  if (row.category === 'Other' && !row.reviewed) warnings.push('Category needs review')
  if (row.quantity === null || !row.unit?.trim()) warnings.push('Quantity or unit is unknown')
  if (row.line_total === null) warnings.push('Line total is unknown')
  if (row.quantity !== null && row.unit_price !== null && row.line_total !== null &&
      Math.abs(cents(row.quantity * row.unit_price) - cents(row.line_total)) > 1) {
    warnings.push('Quantity × unit price differs from line total')
  }
  return warnings
}

export function ReviewPanel({ review, categories, method, candidateId, onSaved }: {
  review: Review; categories: string[]; method: string; candidateId: string; onSaved: (receipt: SavedReceipt) => void
}) {
  const [receipt, setReceipt] = useState<Receipt>(review.receipt)
  const [rows, setRows] = useState<Row[]>(() => review.items.map(item => ({ ...item, id: crypto.randomUUID(), reviewed: false })))
  const [editing, setEditing] = useState<string | null>(null)
  const [draft, setDraft] = useState<Item>(emptyItem())
  const [editError, setEditError] = useState('')
  const [acknowledged, setAcknowledged] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [duplicate, setDuplicate] = useState<'exact_file' | 'possible_receipt' | null>(null)

  useEffect(() => {
    setReceipt(review.receipt)
    setRows(review.items.map(item => ({ ...item, id: crypto.randomUUID(), reviewed: false })))
    setEditing(null)
    setEditError('')
    setAcknowledged(false)
    setSaveError('')
    setDuplicate(null)
  }, [review])

  useEffect(() => { setDuplicate(null) }, [receipt, rows])

  const reconciliation = useMemo(() => {
    if (rows.length === 0 || rows.some(row => row.line_total === null)) return { warning: true, text: 'Enter a line total for every item to compare totals.' }
    const sum = rows.reduce((total, row) => total + cents(row.line_total ?? 0), 0)
    const amount = (sum / 100).toFixed(2)
    if (receipt.subtotal !== null) {
      if (Math.abs(sum - cents(receipt.subtotal)) > 1) return { warning: true, text: `Items: MYR ${amount}; subtotal: MYR ${money(receipt.subtotal)}. Totals do not match.` }
      if (receipt.final_total === null || Math.abs(cents(receipt.subtotal) - cents(receipt.final_total)) <= 1) {
        return { warning: false, text: `Items: MYR ${amount}; subtotal: MYR ${money(receipt.subtotal)}. Totals match.` }
      }
      if (receipt.discount_total === null || receipt.tax_total === null) return { warning: true, text: 'Items match subtotal; receipt total needs review because discount or tax is unknown.' }
      const adjusted = cents(receipt.subtotal) - cents(receipt.discount_total) + cents(receipt.tax_total)
      const match = Math.abs(adjusted - cents(receipt.final_total)) <= 1
      return { warning: !match, text: match ? 'Items, subtotal, and receipt total reconcile.' : 'Subtotal, discount, tax, and receipt total do not reconcile.' }
    }
    if (receipt.final_total !== null) {
      const match = Math.abs(sum - cents(receipt.final_total)) <= 1
      return { warning: !match, text: `Items: MYR ${amount}; receipt total: MYR ${money(receipt.final_total)}. ${match ? 'Totals match directly.' : 'Totals do not match; check discounts and tax against the PDF.'}` }
    }
    return { warning: true, text: `Items: MYR ${amount}. Enter a receipt total or subtotal to compare.` }
  }, [rows, receipt])

  const rowWarningCount = rows.reduce((count, row) => count + (itemWarnings(row).length ? 1 : 0), 0)
  const metadataWarning = !receipt.store_name?.trim() || !receipt.receipt_date
  const ready = rows.length > 0 && !rowWarningCount && !metadataWarning && !reconciliation.warning

  function beginEdit(row: Row) {
    setDraft({ ...row })
    setEditing(row.id)
    setEditError('')
  }

  function addRow() {
    const id = crypto.randomUUID()
    setRows(current => [...current, { ...emptyItem(), id, reviewed: false }])
    setDraft(emptyItem())
    setEditing(id)
    setEditError('')
  }

  function saveRow() {
    if (!draft.display_name.trim()) { setEditError('Enter a product name.'); return }
    for (const value of [draft.quantity, draft.unit_price, draft.line_total]) {
      if (value !== null && (!Number.isFinite(value) || value < 0)) { setEditError('Numbers must be zero or greater.'); return }
    }
    if (!categories.includes(draft.category)) { setEditError('Choose a category from the list.'); return }
    const saved = { ...draft, display_name: draft.display_name.trim(), unit: draft.unit?.trim() || null }
    setRows(current => current.map(row => row.id === editing ? { ...saved, id: row.id, reviewed: true } : row))
    setEditing(null)
    setEditError('')
  }

  async function confirmSave(allowDuplicate: boolean) {
    if (!acknowledged || saving) return
    setSaving(true)
    setSaveError('')
    try {
      const response = await fetch(`/api/candidates/${candidateId}/confirm`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ receipt, items: rows.map(row => ({
          raw_name: row.raw_name || null, display_name: row.display_name, quantity: row.quantity,
          unit: row.unit, unit_price: row.unit_price, line_total: row.line_total,
          category: row.category, review_flag: itemWarnings(row).length > 0,
        })), allow_duplicate: allowDuplicate }),
      })
      const result = await response.json()
      if (response.status === 409 && result.detail?.code === 'possible_duplicate') {
        setDuplicate(result.detail.match_kind)
        return
      }
      if (!response.ok) {
        const detail = result.detail
        throw new Error(detail?.code === 'alias_conflict' ? `The source name “${detail.source_name}” already maps to a different product. Keep its existing name or revise this row.` : typeof detail === 'string' ? detail : 'Could not save. The temporary candidate is still available.')
      }
      onSaved(result as SavedReceipt)
    } catch (cause) {
      setSaveError(cause instanceof Error ? cause.message : 'Could not save. The temporary candidate is still available.')
    } finally {
      setSaving(false)
    }
  }

  const textField = (label: string, key: 'store_name' | 'receipt_date' | 'receipt_number' | 'payment_method', type = 'text') => (
    <label className="field">{label}<input aria-label={label} type={type} value={receipt[key] ?? ''}
      onChange={event => setReceipt(current => ({ ...current, [key]: event.target.value || null }))} /></label>
  )
  const moneyField = (label: string, key: NumericKey) => (
    <label className="field">{label}<input aria-label={label} type="number" min="0" step="0.01"
      value={receipt[key] ?? ''} onChange={event => setReceipt(current => ({ ...current, [key]: numberValue(event.target.value) }))} /></label>
  )
  const draftNumber = (label: string, key: 'quantity' | 'unit_price' | 'line_total') => (
    <label className="field">{label}<input aria-label={label} type="number" min="0" step={key === 'quantity' ? '0.001' : '0.01'}
      value={draft[key] ?? ''} onChange={event => setDraft(current => ({ ...current, [key]: numberValue(event.target.value) }))} /></label>
  )

  return <section className="review-panel" aria-label="Temporary structured candidate">
    <h3>Review candidate</h3>
    <p><strong>Extraction:</strong> {method === 'manual' ? 'Manual entry' : method === 'ocr' ? 'Local OCR' : 'Embedded text'}</p>
    {rows.length === 0 && <p role="status" className="warning">⚠ No usable item rows were extracted. Enter the receipt details and add items while checking the original PDF.</p>}
    <p className="review-note">Edits remain in this browser session and are not saved as receipts. Compare every field with the original PDF.</p>
    <h4>Receipt details</h4>
    <div className="field-grid">
      {textField('Store', 'store_name')}{textField('Date', 'receipt_date', 'date')}
      {textField('Receipt number', 'receipt_number')}{textField('Payment method', 'payment_method')}
      {moneyField('Subtotal (MYR)', 'subtotal')}{moneyField('Discount (MYR)', 'discount_total')}
      {moneyField('Tax (MYR)', 'tax_total')}{moneyField('Receipt total (MYR)', 'final_total')}
    </div>
    {metadataWarning && <p className="warning" role="status">⚠ Store or date needs review.</p>}
    <div className="section-heading"><h4>Items</h4><button type="button" className="secondary" onClick={addRow} disabled={editing !== null}>Add missing item</button></div>
    {rows.length === 0 ? <p>No item rows yet.</p> : <div className="table-scroll"><table>
      <thead><tr><th>Review</th><th>Product</th><th>Category</th><th>Qty</th><th>Unit</th><th>Unit price</th><th>Line total</th><th>Actions</th></tr></thead>
      <tbody>{rows.map(row => <tr key={row.id}>
        <td title={itemWarnings(row).join('; ')}>{itemWarnings(row).length ? '⚠' : '✓'}</td>
        <td>{row.display_name || '—'}{row.raw_name && row.raw_name !== row.display_name && <small className="raw-name">Source: {row.raw_name}</small>}{itemWarnings(row).length > 0 && <small className="row-warnings">{itemWarnings(row).join('; ')}</small>}</td>
        <td>{row.category}</td><td>{row.quantity ?? '—'}</td><td>{row.unit ?? '—'}</td>
        <td>{money(row.unit_price)}</td><td>{money(row.line_total)}</td>
        <td className="row-actions"><button type="button" className="icon-button" aria-label={`Edit ${row.display_name || 'new item'}`} title="Edit row" onClick={() => beginEdit(row)} disabled={editing !== null}>✎</button>
          <button type="button" className="delete-button" aria-label={`Delete ${row.display_name || 'new item'}`} onClick={() => { setRows(current => current.filter(item => item.id !== row.id)); if (editing === row.id) setEditing(null) }} >Delete</button></td>
      </tr>)}</tbody>
    </table></div>}
    {editing && <div className="row-editor" aria-label="Edit item row">
      <h5>Edit item</h5>
      {rows.find(row => row.id === editing)?.raw_name && <p>Original item text: {rows.find(row => row.id === editing)?.raw_name}</p>}
      <div className="field-grid">
        <label className="field">Product name<input aria-label="Product name" value={draft.display_name} onChange={event => setDraft(current => ({ ...current, display_name: event.target.value }))} /></label>
        <label className="field">Category<select aria-label="Category" value={draft.category} onChange={event => setDraft(current => ({ ...current, category: event.target.value }))}>{categories.map(category => <option key={category}>{category}</option>)}</select></label>
        {draftNumber('Quantity', 'quantity')}
        <label className="field">Unit<input aria-label="Unit" value={draft.unit ?? ''} onChange={event => setDraft(current => ({ ...current, unit: event.target.value || null }))} /></label>
        {draftNumber('Unit price (MYR)', 'unit_price')}{draftNumber('Line total (MYR)', 'line_total')}
      </div>
      {editError && <p role="alert" className="error">{editError}</p>}
      <div className="actions"><button type="button" onClick={saveRow}>Save row</button><button type="button" className="secondary" onClick={() => { if (rows.find(row => row.id === editing)?.raw_name === '' && !rows.find(row => row.id === editing)?.display_name) setRows(current => current.filter(row => row.id !== editing)); setEditing(null); setEditError('') }}>Cancel</button></div>
    </div>}
    <div className={reconciliation.warning ? 'reconciliation warning' : 'reconciliation'} role="status">{reconciliation.warning ? '⚠ ' : '✓ '}{reconciliation.text}</div>
    <p className={ready ? 'ready-state' : 'warning'} role="status">{ready ? '✓ Temporary candidate is ready to confirm and save.' : `⚠ Review needed: ${rowWarningCount} item row(s) flagged${metadataWarning ? ', metadata incomplete' : ''}${reconciliation.warning ? ', totals need review' : ''}.`}</p>
    <div className="confirm-panel">
      <label><input type="checkbox" checked={acknowledged} onChange={event => setAcknowledged(event.target.checked)} /> I compared this candidate with the original PDF and accept any remaining warnings.</label>
      <div className="actions"><button type="button" disabled={!acknowledged || saving || editing !== null || rows.length === 0} onClick={() => void confirmSave(false)}>{saving ? 'Saving…' : 'Confirm & Save'}</button></div>
      {duplicate && <div className="warning" role="alert"><p>⚠ {duplicate === 'exact_file' ? 'This exact PDF was saved before.' : 'A receipt with matching details may already be saved.'} Review the PDF before continuing.</p><button type="button" className="secondary" disabled={saving || !acknowledged} onClick={() => void confirmSave(true)}>Save anyway</button></div>}
      {saveError && <p role="alert" className="error">{saveError}</p>}
    </div>
  </section>
}
