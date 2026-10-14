import { useEffect, useState } from 'react'

type PricePoint = { receipt_id: string; receipt_date: string; store_name: string | null; unit_price: number }
type Dashboard = {
  month: string; currency: 'MYR'; receipt_count: number; total_spending: number | null
  missing_total_count: number
  top_categories: { category: string; known_item_spending: number }[]
  most_purchased: { product_name: string; purchase_count: number }[]
  recent_price_history: { product_name: string; unit: string; points: PricePoint[] }[]
  recent_receipts: { id: string; receipt_date: string; store_name: string | null; final_total: number | null }[]
}

const currentMonth = () => {
  const today = new Date()
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
}
const money = (amount: number | null) => amount === null ? 'Unknown' : `MYR ${amount.toFixed(2)}`

export function DashboardPanel({ onOpenReceipt }: { onOpenReceipt: (id: string) => void }) {
  const [month, setMonth] = useState(currentMonth)
  const [data, setData] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setError('')
    fetch(`/api/dashboard?month=${encodeURIComponent(month)}`, { signal: controller.signal })
      .then(async response => {
        if (!response.ok) throw new Error('Could not load the monthly dashboard.')
        return await response.json() as Dashboard
      })
      .then(result => { setData(result); setLoading(false) })
      .catch(cause => { if (!controller.signal.aborted) { setError(cause instanceof Error ? cause.message : 'Could not load the monthly dashboard.'); setLoading(false) } })
    return () => controller.abort()
  }, [month, revision])

  return <section className="intake-panel" aria-label="Monthly dashboard">
    <div className="section-heading"><h2>Monthly dashboard</h2><button type="button" className="secondary" onClick={() => setRevision(value => value + 1)}>Refresh</button></div>
    <label className="field month-selector">Calendar month<input aria-label="Calendar month" type="month" value={month} onChange={event => { if (event.target.value) setMonth(event.target.value) }} /></label>
    {loading && <p role="status">Loading saved receipt totals…</p>}
    {error && <p role="alert" className="error">{error}</p>}
    {!loading && data && <>
      <div className="dashboard-summary"><div><span>Total known spending</span><strong>{money(data.total_spending)}</strong></div><div><span>Saved receipts</span><strong>{data.receipt_count}</strong></div></div>
      {data.missing_total_count > 0 && <p className="warning" role="status">⚠ {data.missing_total_count} receipt(s) have no final total. Spending is incomplete.</p>}
      {data.receipt_count === 0 && <p>No saved receipts dated in this month.</p>}
      <div className="dashboard-grid">
        <section><h3>Top categories</h3><p className="review-note">Known item line totals; they may differ from receipt totals.</p>{data.top_categories.length ? <div className="table-scroll"><table><thead><tr><th>Category</th><th>Item spending</th></tr></thead><tbody>{data.top_categories.map(row => <tr key={row.category}><td>{row.category}</td><td>{money(row.known_item_spending)}</td></tr>)}</tbody></table></div> : <p>No priced items in this month.</p>}</section>
        <section><h3>Most purchased products</h3><p className="review-note">Counted by saved item rows.</p>{data.most_purchased.length ? <div className="table-scroll"><table><thead><tr><th>Product</th><th>Purchases</th></tr></thead><tbody>{data.most_purchased.map(row => <tr key={row.product_name}><td>{row.product_name}</td><td>{row.purchase_count}</td></tr>)}</tbody></table></div> : <p>No saved items in this month.</p>}</section>
      </div>
      <section className="dashboard-section"><h3>Recent comparable prices</h3><p className="review-note">Only checked items with a known positive quantity, unit, and unit price are shown. A product needs observations on at least two receipts in this month.</p>{data.recent_price_history.length ? data.recent_price_history.map(group => <div key={`${group.product_name}-${group.unit}`}><h4>{group.product_name} · {group.unit}</h4><div className="table-scroll"><table><thead><tr><th>Date</th><th>Store</th><th>Unit price</th><th></th></tr></thead><tbody>{group.points.map(point => <tr key={point.receipt_id}><td>{point.receipt_date}</td><td>{point.store_name ?? 'Unknown'}</td><td>{money(point.unit_price)}</td><td><button type="button" className="secondary" onClick={() => onOpenReceipt(point.receipt_id)}>View receipt</button></td></tr>)}</tbody></table></div></div>) : <p>No comparable price history for this month.</p>}</section>
      <section className="dashboard-section"><h3>Recent receipts</h3>{data.recent_receipts.length ? <div className="table-scroll"><table><thead><tr><th>Date</th><th>Store</th><th>Total</th><th></th></tr></thead><tbody>{data.recent_receipts.map(row => <tr key={row.id}><td>{row.receipt_date}</td><td>{row.store_name ?? 'Unknown'}</td><td>{money(row.final_total)}</td><td><button type="button" className="secondary" onClick={() => onOpenReceipt(row.id)}>View receipt</button></td></tr>)}</tbody></table></div> : <p>No recent receipts in this month.</p>}</section>
    </>}
  </section>
}
