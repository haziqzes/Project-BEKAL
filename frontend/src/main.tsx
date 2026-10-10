import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './style.css'

type HealthState = 'checking' | 'healthy' | 'unavailable'

function App() {
  const [backend, setBackend] = useState<HealthState>('checking')
  const [postgres, setPostgres] = useState<HealthState>('checking')

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

  return (
    <main className="shell">
      <header>
        <p className="eyebrow">Project BEKAL · V0.1 foundation</p>
        <h1>Receipt data, under your control.</h1>
        <p className="intro">
          This is the local development foundation. Receipt intake and review are planned for later phases.
        </p>
      </header>

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
