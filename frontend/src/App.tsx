import { useEffect, useState } from 'react'
import './App.css'

type HealthStatus = 'checking' | 'ok' | 'unreachable'

function App() {
  const [status, setStatus] = useState<HealthStatus>('checking')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then((data: { status: string }) => setStatus(data.status === 'ok' ? 'ok' : 'unreachable'))
      .catch(() => setStatus('unreachable'))
  }, [])

  return (
    <main className="shell">
      <h1>TaskFlow</h1>
      <p>
        Backend status: <strong className={`status status-${status}`}>{status}</strong>
      </p>
    </main>
  )
}

export default App
