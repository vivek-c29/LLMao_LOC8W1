import React, { useState, useRef } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Mock client ID — replace with real auth
const CLIENT_ID = 2;

interface AIDiagnostic {
    summary: string;
    severity: string;
    parts_list: string[];
    estimated_cost_inr?: string;
}

const SEVERITY_COLOR: Record<string, string> = {
    high: '#ef4444', medium: '#f59e0b', low: '#4ade80',
};

export default function PostJob() {
    const navigate = useNavigate();
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [location, setLocation] = useState('');
    const [budget, setBudget] = useState('');
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [diagnostic, setDiagnostic] = useState<AIDiagnostic | null>(null);
    const [diagLoading, setDiagLoading] = useState(false);
    const [posting, setPosting] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setImageFile(file);
        setImagePreview(URL.createObjectURL(file));
        setDiagnostic(null);

        // Immediately run AI diagnostic
        setDiagLoading(true);
        try {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('description', description || 'Please analyze this image for any issues.');
            const res = await axios.post(`${API}/ai/analyze-problem`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setDiagnostic(res.data);
        } catch (err) {
            toast.error('AI analysis failed. You can still post the job manually.');
        } finally {
            setDiagLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setPosting(true);
        try {
            const jobPayload = {
                client_id: CLIENT_ID,
                title,
                description,
                location,
                budget: budget ? Number(budget) : undefined,
                ai_summary: diagnostic || undefined,
            };
            const res = await axios.post(`${API}/jobs`, jobPayload);
            toast.success('Job posted successfully!');
            navigate(`/jobs/${res.data.id}/bids`);
        } catch (err) {
            toast.error('Failed to post job. Please try again.');
        } finally {
            setPosting(false);
        }
    };

    return (
        <div className="post-job">
            <h2>Post a New Job</h2>

            <form onSubmit={handleSubmit} className="job-form">
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="job-title">Job Title <span className="required">*</span></label>
                        <input
                            id="job-title" type="text" value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="e.g. Fix leaking kitchen tap" required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="job-location">Location</label>
                        <input
                            id="job-location" type="text" value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            placeholder="e.g. Bandra West, Mumbai"
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="job-desc">Problem Description</label>
                    <textarea
                        id="job-desc" value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows={3}
                        placeholder="Describe the issue in detail…"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="job-budget">Budget (₹)</label>
                    <input
                        id="job-budget" type="number" min="1" value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                        placeholder="Optional budget"
                    />
                </div>

                {/* ── Image Upload ── */}
                <div className="form-group upload-zone" onClick={() => fileInputRef.current?.click()}>
                    <input
                        ref={fileInputRef} type="file"
                        accept="image/jpeg,image/png,image/webp"
                        style={{ display: 'none' }}
                        onChange={handleImageChange}
                    />
                    {imagePreview ? (
                        <img src={imagePreview} alt="Uploaded preview" className="image-preview" />
                    ) : (
                        <div className="upload-placeholder">
                            <span className="upload-icon">📷</span>
                            <p>Click to upload a photo of the problem</p>
                            <p className="upload-hint">AI will instantly diagnose the issue</p>
                        </div>
                    )}
                </div>

                {/* ── AI Diagnostic Card ── */}
                {diagLoading && (
                    <div className="ai-card loading-card">
                        <div className="ai-card-header">
                            <span>🤖 AI Diagnostic</span>
                            <div className="spinner" />
                        </div>
                        <p>Analyzing your image…</p>
                    </div>
                )}

                {diagnostic && !diagLoading && (
                    <div className="ai-card">
                        <div className="ai-card-header">
                            <span>🤖 AI Diagnostic</span>
                            <span
                                className="severity-pill"
                                style={{ background: SEVERITY_COLOR[diagnostic.severity] || '#666' }}
                            >
                                {diagnostic.severity.toUpperCase()}
                            </span>
                        </div>
                        <p className="ai-summary-text">{diagnostic.summary}</p>
                        {diagnostic.parts_list.length > 0 && (
                            <div className="parts-section">
                                <strong>Parts Needed:</strong>
                                <div className="parts-chips">
                                    {diagnostic.parts_list.map((part, i) => (
                                        <span key={i} className="part-chip">{part}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {diagnostic.estimated_cost_inr && (
                            <p className="cost-estimate">💰 Estimated Cost: <strong>{diagnostic.estimated_cost_inr}</strong></p>
                        )}
                    </div>
                )}

                <button type="submit" className="btn-post" disabled={posting}>
                    {posting ? 'Posting…' : '📢 Post Job'}
                </button>
            </form>
        </div>
    );
}
