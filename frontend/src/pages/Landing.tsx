import { Link } from 'react-router-dom';

export default function Landing() {
    return (
        <div style={{ textAlign: 'center', marginTop: '4rem' }}>
            <h1>Welcome to Sidequests</h1>
            <p>Embark on your journey by logging in or registering.</p>
            <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                <Link
                    to="/login"
                    style={{ padding: '0.5rem 1rem', background: '#3b82f6', color: 'white', textDecoration: 'none', borderRadius: '4px' }}
                >
                    Log In
                </Link>
                <Link
                    to="/register"
                    style={{ padding: '0.5rem 1rem', background: '#e5e7eb', color: 'black', textDecoration: 'none', borderRadius: '4px' }}
                >
                    Register
                </Link>
            </div>
        </div>
    );
}
