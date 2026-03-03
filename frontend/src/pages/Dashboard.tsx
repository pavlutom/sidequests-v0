import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Navigate } from 'react-router-dom';
import { API_BASE } from '../api';

interface Sidequest {
    id: string;
    title: string;
    description: string;
    reward_xp: number;
    created_at: string;
    completed_at: string | null;
}

interface GeneratedQuest {
    title: string;
    description: string;
    reward_xp: number;
    tags?: string[];
}

interface Preferences {
    categories: string[];
    estimated_cost: string;
    goal: string;
}

export default function Dashboard() {
    const { user, logout, token, refreshUser } = useAuth();
    const navigate = useNavigate();

    const [healthStatus, setHealthStatus] = useState<string>('Checking backend...');
    const [sidequests, setSidequests] = useState<Sidequest[]>([]);
    const [generatedQuest, setGeneratedQuest] = useState<GeneratedQuest | null>(null);
    const [loadingAction, setLoadingAction] = useState<boolean>(false);
    const [expandedQuestId, setExpandedQuestId] = useState<string | null>(null);
    const [preferences, setPreferences] = useState<Preferences>({
        categories: ['social'],
        estimated_cost: 'minimal',
        goal: 'fun'
    });
    const [generatorConfig, setGeneratorConfig] = useState<{ generator_type: string, openai_model?: string } | null>(null);

    const fetchSidequests = () => {
        if (!token) return;
        fetch(`${API_BASE}/sidequests`, {
            headers: { Authorization: `Bearer ${token}` }
        })
            .then(res => res.json())
            .then(data => setSidequests(data))
            .catch(err => console.error("Error fetching sidequests", err));
    };

    useEffect(() => {
        fetch(`${API_BASE}/health`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'ok') setHealthStatus('Backend OK, DB Connected');
                if (data.generator_config) setGeneratorConfig(data.generator_config);
            })
            .catch(() => setHealthStatus('Backend Unreachable'));

        fetchSidequests();
    }, [token, API_BASE]);

    if (!user) {
        return <Navigate to="/login" />;
    }

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const handleGenerate = async () => {
        setLoadingAction(true);
        try {
            const res = await fetch(`${API_BASE}/sidequests/generate`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            });
            const data = await res.json();
            setGeneratedQuest(data);
        } catch (e) {
            console.error(e);
        }
        setLoadingAction(false);
    };

    const handleAccept = async () => {
        if (!generatedQuest) return;
        setLoadingAction(true);
        try {
            await fetch(`${API_BASE}/sidequests/accept`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(generatedQuest)
            });
            setGeneratedQuest(null);
            fetchSidequests();
            refreshUser();
        } catch (e) {
            console.error(e);
        }
        setLoadingAction(false);
    };

    const handleComplete = async (id: string) => {
        try {
            await fetch(`${API_BASE}/sidequests/${id}/complete`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchSidequests();
            refreshUser();
        } catch (e) {
            console.error(e);
        }
    };

    const handleDiscard = async (id: string) => {
        try {
            await fetch(`${API_BASE}/sidequests/${id}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchSidequests();
        } catch (e) {
            console.error(e);
        }
    };

    const toggleQuestExpansion = (id: string) => {
        setExpandedQuestId((prev: string | null) => (prev === id ? null : id));
    };

    const activeQuests = sidequests.filter((q: Sidequest) => !q.completed_at);
    const completedQuests = sidequests.filter((q: Sidequest) => q.completed_at);

    return (
        <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '1rem', fontFamily: 'sans-serif' }}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e5e7eb', paddingBottom: '1rem' }}>
                <h1 style={{ margin: 0 }}>Sidequests Dashboard</h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.875rem', color: '#64748b' }}>Total XP Balance</div>
                        <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#b45309' }}>✨ {user.total_xp}</div>
                    </div>
                    <button
                        onClick={handleLogout}
                        style={{ padding: '0.5rem 1rem', background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        Logout
                    </button>
                </div>
            </header>

            <main style={{ marginTop: '2rem' }}>
                {/* Proposed Quest Section */}
                <div style={{ padding: '1.5rem', background: '#eff6ff', borderRadius: '8px', border: '1px solid #bfdbfe', marginBottom: '2rem', textAlign: 'center' }}>
                    {generatedQuest ? (
                        <>
                            <h2 style={{ marginTop: 0, color: '#1e3a8a' }}>{generatedQuest.title}</h2>
                            <div style={{ display: 'inline-block', background: '#fef3c7', color: '#92400e', padding: '0.25rem 0.75rem', borderRadius: '999px', fontSize: '0.875rem', fontWeight: 'bold', border: '1px solid #fde68a', marginBottom: '1rem' }}>
                                ✨ {generatedQuest.reward_xp} XP
                            </div>
                            <p style={{ color: '#1e40af', fontSize: '1.1rem', margin: '0 0 1.5rem 0' }}>{generatedQuest.description}</p>
                            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1.5rem' }}>
                                <button onClick={handleAccept} disabled={loadingAction} style={{ padding: '0.75rem 1.5rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                                    Accept Quest
                                </button>
                                <button onClick={handleGenerate} disabled={loadingAction} style={{ padding: '0.75rem 1.5rem', background: 'white', color: '#2563eb', border: '1px solid #2563eb', borderRadius: '4px', cursor: 'pointer' }}>
                                    Reroll
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <h2 style={{ marginTop: 0, color: '#1e3a8a' }}>What are you in the mood for?</h2>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem', textAlign: 'left' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 'bold', color: '#475569', marginBottom: '0.5rem' }}>Categories</label>
                                    <select
                                        multiple
                                        value={preferences.categories}
                                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setPreferences({
                                            ...preferences,
                                            categories: Array.from(e.target.selectedOptions, (option: HTMLOptionElement) => option.value)
                                        })}
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #cbd5e1' }}
                                    >
                                        <option value="social">Social</option>
                                        <option value="outdoors">Outdoors</option>
                                        <option value="family">Family Time</option>
                                        <option value="productivity">Productivity</option>
                                        <option value="health">Health & Wellness</option>
                                        <option value="learning">Skill Learning</option>
                                    </select>
                                    <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>Hold Ctrl/Cmd to select multiple</p>
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 'bold', color: '#475569', marginBottom: '0.5rem' }}>Estimated Cost</label>
                                    <select
                                        value={preferences.estimated_cost}
                                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setPreferences({ ...preferences, estimated_cost: e.target.value })}
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #cbd5e1' }}
                                    >
                                        <option value="minimal">Minimal ($0)</option>
                                        <option value="some">Some ($1-20)</option>
                                        <option value="significant">Significant ($20+)</option>
                                    </select>
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 'bold', color: '#475569', marginBottom: '0.5rem' }}>Primary Goal</label>
                                    <select
                                        value={preferences.goal}
                                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setPreferences({ ...preferences, goal: e.target.value })}
                                        style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #cbd5e1' }}
                                    >
                                        <option value="fun">Just Fun</option>
                                        <option value="growth">Personal Growth</option>
                                        <option value="learning">Learning</option>
                                    </select>
                                </div>
                            </div>

                            <button onClick={handleGenerate} disabled={loadingAction} style={{ padding: '0.75rem 1.5rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', marginTop: '0.5rem' }}>
                                {loadingAction ? 'Generating...' : 'Generate Sidequest'}
                            </button>
                        </>
                    )}
                </div>

                {/* Active Quests */}
                <h2 style={{ borderBottom: '2px solid #e5e7eb', paddingBottom: '0.5rem' }}>Active Quests ({activeQuests.length})</h2>
                {activeQuests.length === 0 ? (
                    <p style={{ color: '#6b7280', fontStyle: 'italic' }}>No active sidequests. Request one above!</p>
                ) : (
                    <div style={{ display: 'grid', gap: '1rem', marginBottom: '2rem' }}>
                        {activeQuests.map(quest => (
                            <div key={quest.id} style={{ padding: '1.25rem', border: '1px solid #e2e8f0', borderRadius: '8px', background: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                                    <h3 style={{ margin: 0 }}>{quest.title}</h3>
                                    <span style={{ background: '#fef3c7', color: '#92400e', padding: '0.2rem 0.6rem', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 'bold', border: '1px solid #fde68a', whiteSpace: 'nowrap' }}>
                                        {quest.reward_xp} XP
                                    </span>
                                </div>
                                <p style={{ margin: '0 0 1.5rem 0', color: '#475569' }}>{quest.description}</p>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button onClick={() => handleComplete(quest.id)} style={{ padding: '0.5rem 1rem', background: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                                        Complete
                                    </button>
                                    <button onClick={() => handleDiscard(quest.id)} style={{ padding: '0.5rem 1rem', background: 'white', color: '#ef4444', border: '1px solid #ef4444', borderRadius: '4px', cursor: 'pointer' }}>
                                        Discard
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Completed Quests */}
                <h2 style={{ borderBottom: '2px solid #e5e7eb', paddingBottom: '0.5rem', marginTop: '3rem' }}>Completed Quests ({completedQuests.length})</h2>
                {completedQuests.length === 0 ? (
                    <p style={{ color: '#6b7280', fontStyle: 'italic' }}>No completed sidequests yet. Finish one to see it here!</p>
                ) : (
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        {completedQuests.map(quest => {
                            const isExpanded = expandedQuestId === quest.id;
                            return (
                                <div
                                    key={quest.id}
                                    onClick={() => toggleQuestExpansion(quest.id)}
                                    style={{
                                        padding: '1rem',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        background: '#f8fafc',
                                        cursor: 'pointer',
                                        transition: 'background-color 0.2s',
                                        opacity: isExpanded ? 1 : 0.8
                                    }}
                                    onMouseOver={(e: React.MouseEvent<HTMLDivElement>) => (e.currentTarget.style.backgroundColor = '#f1f5f9')}
                                    onMouseOut={(e: React.MouseEvent<HTMLDivElement>) => (e.currentTarget.style.backgroundColor = '#f8fafc')}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                <h4 style={{ margin: 0, color: '#334155', textDecoration: 'line-through' }}>{quest.title}</h4>
                                                <span style={{ fontSize: '0.75rem', color: '#92400e', fontWeight: 'bold' }}>+{quest.reward_xp} XP</span>
                                            </div>
                                            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#64748b' }}>Completed on: {new Date(quest.completed_at!).toLocaleDateString()}</p>
                                        </div>
                                        <div style={{ color: '#94a3b8', fontSize: '1.25rem', transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>
                                            ▼
                                        </div>
                                    </div>
                                    {isExpanded && (
                                        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px dashed #cbd5e1', color: '#475569' }}>
                                            <p style={{ margin: 0 }}>{quest.description}</p>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* System Diagnostics */}
                <div style={{ padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '8px', marginTop: '4rem', fontSize: '0.875rem' }}>
                    <h3 style={{ marginTop: 0, fontSize: '1rem', color: '#64748b' }}>System Diagnostics</h3>
                    <p style={{ color: '#64748b', margin: '0.25rem 0' }}>User ID: <code>{user.id}</code></p>
                    <p style={{ color: '#64748b', margin: '0.25rem 0' }}>Backend API: {healthStatus}</p>
                    {generatorConfig && (
                        <p style={{ color: '#64748b', margin: '0.25rem 0' }}>
                            Generator: <code>{generatorConfig.generator_type}</code>
                            {generatorConfig.openai_model && <span> ({generatorConfig.openai_model})</span>}
                        </p>
                    )}
                </div>
            </main>
        </div>
    );
}
