import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import toast from 'react-hot-toast';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Mock logged-in worker ID — in production this comes from auth context
const WORKER_ID = 1;

export default function BidPage() {
    const { jobId } = useParams<{ jobId: string }>();
    const { t } = useTranslation();
    const navigate = useNavigate();

    const [amount, setAmount] = useState('');
    const [message, setMessage] = useState('');
    const [listening, setListening] = useState(false);
    const [jobTitle, setJobTitle] = useState('');
    const recognitionRef = useRef<SpeechRecognition | null>(null);

    useEffect(() => {
        if (jobId) {
            axios.get(`${API}/jobs/${jobId}`).then((r) => setJobTitle(r.data.title)).catch(console.error);
        }
    }, [jobId]);

    const handleSpeakPrice = () => {
        const SpeechRec =
            (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (!SpeechRec) {
            toast.error('Speech recognition not supported in this browser.');
            return;
        }

        const recognition: SpeechRecognition = new SpeechRec();
        recognition.lang = 'en-IN';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognitionRef.current = recognition;

        recognition.start();
        setListening(true);

        recognition.onresult = (event: SpeechRecognitionEvent) => {
            const transcript = event.results[0][0].transcript;
            // Extract first integer found in transcript
            const match = transcript.match(/\d[\d,]*/);
            if (match) {
                const price = match[0].replace(/,/g, '');
                setAmount(price);
                toast.success(`Captured: ₹${price}`);
            } else {
                toast.error(`Could not find a price in: "${transcript}"`);
            }
            setListening(false);
        };

        recognition.onerror = () => {
            toast.error('Speech recognition error. Please try again.');
            setListening(false);
        };

        recognition.onend = () => setListening(false);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!amount || isNaN(Number(amount))) {
            toast.error('Please enter a valid bid amount.');
            return;
        }
        try {
            await axios.post(`${API}/bids`, {
                job_id: Number(jobId),
                worker_id: WORKER_ID,
                amount: Number(amount),
                message,
            });
            toast.success('Bid submitted successfully!');
            navigate('/');
        } catch (err) {
            toast.error('Failed to submit bid. Please try again.');
        }
    };

    return (
        <div className="bid-page">
            <h2>{t('place_bid')}</h2>
            {jobTitle && <p className="bid-job-title">Job: <strong>{jobTitle}</strong></p>}

            <form onSubmit={handleSubmit} className="bid-form">
                <div className="form-group">
                    <label htmlFor="bid-amount">{t('your_price')}</label>
                    <div className="price-input-row">
                        <span className="currency-symbol">₹</span>
                        <input
                            id="bid-amount"
                            type="number"
                            min="1"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            placeholder="Enter your price"
                            required
                        />
                        <button
                            type="button"
                            className={`btn-speak ${listening ? 'listening' : ''}`}
                            onClick={handleSpeakPrice}
                        >
                            {listening ? '🔴 Listening…' : `🎤 ${t('speak_price')}`}
                        </button>
                    </div>
                    {listening && (
                        <p className="listening-hint">Say your price in numbers, e.g. "five hundred"</p>
                    )}
                </div>

                <div className="form-group">
                    <label htmlFor="bid-message">{t('message')}</label>
                    <textarea
                        id="bid-message"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        rows={4}
                        placeholder="Tell the client why you're the right person for this job…"
                    />
                </div>

                <button type="submit" className="btn-submit">{t('submit_bid')}</button>
            </form>
        </div>
    );
}
