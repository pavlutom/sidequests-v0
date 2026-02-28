import { useEffect, useState } from 'react'

function App() {
    const [status, setStatus] = useState<string>('Loading...')
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        // Rely on VITE_API_URL, which should be available via vite env
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

        fetch(`${apiUrl}/api/health`)
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok')
                return res.json()
            })
            .then(data => {
                if (data.status === 'ok') {
                    setStatus('Backend: ok')
                } else {
                    setStatus('Backend returned unknown status: ' + JSON.stringify(data))
                }
            })
            .catch(err => {
                setStatus('Error')
                setError(err.message)
            })
    }, [])

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '600px', margin: '0 auto' }}>
            <h1>Sidequests MVP</h1>
            <div style={{ padding: '1.5rem', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
                <h2 style={{ marginTop: 0 }}>System Status</h2>
                <div style={{
                    padding: '1rem',
                    backgroundColor: status === 'Backend: ok' ? '#dcfce7' : '#fef2f2',
                    color: status === 'Backend: ok' ? '#166534' : '#991b1b',
                    borderRadius: '4px',
                    fontWeight: 'bold'
                }}>
                    {status}
                </div>
                {error && (
                    <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#fef2f2', color: '#991b1b', borderRadius: '4px' }}>
                        <strong>Error details:</strong> {error}
                        <br /><br />
                        <small>Please check if the backend is running and accessible.</small>
                    </div>
                )}
            </div>
        </div>
    )
}

export default App
