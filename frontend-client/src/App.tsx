import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import axios from 'axios';
import PostJob from './pages/PostJob';
import BidComparison from './pages/BidComparison';
import './App.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const CLIENT_ID = 2;

interface Job {
    id: number;
    title: string;
    status: string;
    created_at: string;
    budget?: number;
}

function MyJobs() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        axios.get(`${API}/jobs?client_id=${CLIENT_ID}`)
            .then((r) => setJobs(r.data))
            .catch(console.error);
    }, []);

    return (
        <div className="my-jobs">
            <h2>My Posted Jobs</h2>
            {jobs.length === 0 && <p className="muted">No jobs posted yet.</p>}
            <div className="jobs-list">
                {jobs.map((job) => (
                    <div key={job.id} className="job-item">
                        <div>
                            <h3>{job.title}</h3>
                            <span className={`status-tag ${job.status}`}>{job.status.replace('_', ' ')}</span>
                        </div>
                        <div className="job-item-actions">
                            {job.budget && <span className="budget-tag">₹{job.budget}</span>}
                            <button
                                className="btn-view-bids"
                                onClick={() => navigate(`/jobs/${job.id}/bids`)}
                            >
                                View Bids
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function App() {
    return (
        <BrowserRouter>
            <Toaster position="top-right" />
            <div className="app-shell">
                <nav className="topbar">
                    <div className="topbar-brand">
                        <span className="brand-icon">🏠</span>
                        <span className="brand-text">LoC ANTI Client</span>
                    </div>
                    <div className="topbar-nav">
                        <Link to="/">My Jobs</Link>
                        <Link to="/post" className="btn-post-nav">+ Post Job</Link>
                    </div>
                </nav>

                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<MyJobs />} />
                        <Route path="/post" element={<PostJob />} />
                        <Route path="/jobs/:jobId/bids" element={<BidComparison />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}
