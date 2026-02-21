import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Toaster } from 'react-hot-toast';
import '../src/i18n/index';
import Dashboard from './pages/Dashboard';
import JobList from './pages/JobList';
import BidPage from './pages/BidPage';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

// Mock logged-in worker — replace with real auth
const WORKER_ID = 1;

const LANGUAGES = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिंदी' },
    { code: 'mr', label: 'मराठी' },
    { code: 'te', label: 'తెలుగు' },
];

export default function App() {
    const { t, i18n } = useTranslation();
    useWebSocket(WORKER_ID);

    return (
        <BrowserRouter>
            <Toaster position="top-right" />
            <div className="app-shell">
                <nav className="sidebar">
                    <div className="sidebar-logo">
                        <span className="logo-icon">⚡</span>
                        <span className="logo-text">{t('app_name')}</span>
                    </div>
                    <ul className="sidebar-nav">
                        <li><Link to="/">{t('dashboard')}</Link></li>
                        <li><Link to="/jobs">{t('jobs')}</Link></li>
                    </ul>
                    <div className="lang-switcher">
                        <span>{t('language')}:</span>
                        {LANGUAGES.map((l) => (
                            <button
                                key={l.code}
                                className={`lang-btn ${i18n.language === l.code ? 'active' : ''}`}
                                onClick={() => i18n.changeLanguage(l.code)}
                            >
                                {l.label}
                            </button>
                        ))}
                    </div>
                </nav>

                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard workerId={WORKER_ID} />} />
                        <Route path="/jobs" element={<JobList />} />
                        <Route path="/bid/:jobId" element={<BidPage />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}
