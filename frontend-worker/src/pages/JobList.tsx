import React, { useEffect, useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AISummary {
    summary: string;
    severity: string;
    parts_list: string[];
    estimated_cost_inr?: string;
}

interface Job {
    id: number;
    title: string;
    description: string;
    location: string;
    budget: number;
    ai_summary: AISummary | null;
    created_at: string;
}

const SEVERITY_COLOR: Record<string, string> = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#4ade80',
};

export default function JobList() {
    const { t, i18n } = useTranslation();
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const res = await axios.get(`${API}/jobs?status=open`, {
                    headers: { 'X-User-Language': i18n.language },
                });
                setJobs(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchJobs();
    }, [i18n.language]);

    const handleListen = (job: Job) => {
        if (!window.speechSynthesis) {
            alert('Text-to-speech is not supported in your browser.');
            return;
        }
        window.speechSynthesis.cancel();
        const text = job.ai_summary
            ? `${job.title}. ${job.ai_summary.summary}. Estimated cost: ${job.ai_summary.estimated_cost_inr || 'unknown'}.`
            : `${job.title}. ${job.description}`;

        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = i18n.language === 'hi' ? 'hi-IN' : i18n.language === 'mr' ? 'mr-IN' : i18n.language === 'te' ? 'te-IN' : 'en-IN';
        utter.rate = 0.9;
        utteranceRef.current = utter;
        window.speechSynthesis.speak(utter);
    };

    if (loading) return <div className="loading">Loading jobs…</div>;

    return (
        <div className="job-list">
            <h2>{t('jobs')}</h2>
            {jobs.length === 0 && <p className="muted">{t('no_jobs')}</p>}
            <div className="job-grid">
                {jobs.map((job) => (
                    <div key={job.id} className="job-card">
                        <div className="job-card-header">
                            <h3>{job.title}</h3>
                            {job.ai_summary && (
                                <span
                                    className="severity-badge"
                                    style={{ background: SEVERITY_COLOR[job.ai_summary.severity] || '#666' }}
                                >
                                    {job.ai_summary.severity.toUpperCase()}
                                </span>
                            )}
                        </div>

                        {job.location && <p className="job-location">📍 {job.location}</p>}
                        {job.budget && <p className="job-budget">💰 Budget: ₹{job.budget}</p>}

                        {job.ai_summary && (
                            <div className="ai-summary-box">
                                <p>{job.ai_summary.summary}</p>
                                {job.ai_summary.parts_list.length > 0 && (
                                    <div className="parts-list">
                                        <strong>Parts needed:</strong>
                                        <ul>
                                            {job.ai_summary.parts_list.map((part, i) => (
                                                <li key={i}>{part}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                {job.ai_summary.estimated_cost_inr && (
                                    <p className="cost-estimate">Est. cost: {job.ai_summary.estimated_cost_inr}</p>
                                )}
                            </div>
                        )}

                        <div className="job-card-actions">
                            <button className="btn-listen" onClick={() => handleListen(job)}>
                                🔊 {t('listen')}
                            </button>
                            <Link to={`/bid/${job.id}`} className="btn-bid">
                                {t('place_bid')}
                            </Link>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
