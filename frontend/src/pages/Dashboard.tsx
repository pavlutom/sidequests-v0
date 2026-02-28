import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Navigate } from 'react-router-dom';

export default function Dashboard() {
    const { user, logout, token } = useAuth();
    const navigate = useNavigate();
    const [healthStatus, setHealthStatus] = useState<string>('Checking backend...');

    useEffect(() => {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        fetch(`${apiUrl}/api/health`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') {
                    setHealthStatus('Backend OK, DB Connected');
                }
            })
            .catch(() => setHealthStatus('Backend Unreachable'));
    }, []);

    if (!user) {
        return <Navigate to="/login" />;
    }

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '1rem', fontFamily: 'sans-serif' }}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e5e7eb', paddingBottom: '1rem' }}>
                <h1 style={{ margin: 0 }}>Sidequests Dashboard</h1>
                <button
                    onClick={handleLogout}
                    style={{ padding: '0.5rem 1rem', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: '4px', cursor: 'pointer' }}
                >
                    Logout
                </button>
            </header>

            <main style={{ marginTop: '2rem' }}>
                <div style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', marginBottom: '2rem' }}>
                    <h2 style={{ marginTop: 0 }}>Welcome, {user.email}</h2>
                    <p>Account ID: <code>{user.id}</code></p>
                    <p>Member Since: {new Date(user.created_at).toLocaleDateString()}</p>
                </div>

                <div style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                    <h3 style={{ marginTop: 0 }}>System Diagnostics</h3>
                    <p><strong>Raw Token Preview:</strong> {token?.substring(0, 20)}...</p>
                    <p><strong>Backend API:</strong> {healthStatus}</p>
                </div>
            </main>
        </div>
    );
}
