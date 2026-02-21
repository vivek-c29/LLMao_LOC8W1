import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Bid {
    id: number;
    worker_id: number;
    amount: number;
    message: string;
    is_accepted: boolean;
    created_at: string;
}

interface WorkerProfile {
    name: string;
    phone: string;
}

interface WorkerStats {
    total_jobs_completed: number;
    total_earnings: number;
}

interface WorkerReviewStats {
    average_rating: number;
    total_reviews: number;
}

interface EnrichedBid extends Bid {
    workerName: string;
    avgRating: number;
    totalReviews: number;
    jobsCompleted: number;
}

type SortKey = 'amount' | 'avgRating' | 'jobsCompleted';

export default function BidComparison() {
    const { jobId } = useParams<{ jobId: string }>();
    const [bids, setBids] = useState<EnrichedBid[]>([]);
    const [loading, setLoading] = useState(true);
    const [sortBy, setSortBy] = useState<SortKey>('amount');
    const [accepting, setAccepting] = useState<number | null>(null);

    useEffect(() => {
        const fetchBids = async () => {
            try {
                const bidsRes = await axios.get(`${API}/bids?job_id=${jobId}`);
                const rawBids: Bid[] = bidsRes.data;

                const enriched = await Promise.all(
                    rawBids.map(async (bid) => {
                        const [profileRes, statsRes, reviewRes] = await Promise.all([
                            axios.get(`${API}/users/${bid.worker_id}`).catch(() => ({ data: { name: 'Unknown', phone: '' } })),
                            axios.get(`${API}/bids/worker/${bid.worker_id}/stats`).catch(() => ({ data: { total_jobs_completed: 0 } })),
                            axios.get(`${API}/reviews/worker/${bid.worker_id}/stats`).catch(() => ({ data: { average_rating: 0, total_reviews: 0 } })),
                        ]);
                        return {
                            ...bid,
                            workerName: profileRes.data.name,
                            avgRating: reviewRes.data.average_rating,
                            totalReviews: reviewRes.data.total_reviews,
                            jobsCompleted: statsRes.data.total_jobs_completed,
                        };
                    })
                );
                setBids(enriched);
            } catch (err) {
                console.error(err);
                toast.error('Failed to load bids.');
            } finally {
                setLoading(false);
            }
        };
        fetchBids();
    }, [jobId]);

    const sortedBids = [...bids].sort((a, b) => {
        if (sortBy === 'amount') return a.amount - b.amount;
        if (sortBy === 'avgRating') return b.avgRating - a.avgRating;
        return b.jobsCompleted - a.jobsCompleted;
    });

    const handleAccept = async (bid: EnrichedBid) => {
        setAccepting(bid.id);
        try {
            await axios.post(`${API}/deals/accept`, {
                job_id: Number(jobId),
                worker_id: bid.worker_id,
                bid_id: bid.id,
            });
            toast.success(`Deal accepted with ${bid.workerName}! They've been notified.`);
            setBids((prev) => prev.map((b) => ({ ...b, is_accepted: b.id === bid.id })));
        } catch (err) {
            toast.error('Failed to accept bid. Please try again.');
        } finally {
            setAccepting(null);
        }
    };

    const renderStars = (rating: number) => {
        const full = Math.round(rating);
        return '★'.repeat(full) + '☆'.repeat(5 - full);
    };

    if (loading) return <div className="loading">Loading bids…</div>;

    return (
        <div className="bid-comparison">
            <h2>Compare Bids</h2>

            {bids.length === 0 ? (
                <p className="muted">No bids received yet for this job.</p>
            ) : (
                <>
                    <div className="sort-controls">
                        <span>Sort by:</span>
                        {(['amount', 'avgRating', 'jobsCompleted'] as SortKey[]).map((key) => (
                            <button
                                key={key}
                                className={`sort-btn ${sortBy === key ? 'active' : ''}`}
                                onClick={() => setSortBy(key)}
                            >
                                {key === 'amount' ? '💰 Lowest Price' : key === 'avgRating' ? '⭐ Best Rating' : '🔨 Most Jobs'}
                            </button>
                        ))}
                    </div>

                    <div className="bid-table">
                        <div className="bid-table-header">
                            <span>Worker</span>
                            <span>Bid Amount</span>
                            <span>Rating</span>
                            <span>Jobs Done</span>
                            <span>Message</span>
                            <span>Action</span>
                        </div>

                        {sortedBids.map((bid) => (
                            <div key={bid.id} className={`bid-row ${bid.is_accepted ? 'accepted' : ''}`}>
                                <div className="worker-cell">
                                    <div className="worker-avatar">{bid.workerName[0]?.toUpperCase()}</div>
                                    <span>{bid.workerName}</span>
                                </div>
                                <div className="amount-cell">₹{bid.amount.toLocaleString()}</div>
                                <div className="rating-cell">
                                    <span className="stars">{renderStars(bid.avgRating)}</span>
                                    <span className="rating-num">{bid.avgRating.toFixed(1)} ({bid.totalReviews})</span>
                                </div>
                                <div className="jobs-cell">{bid.jobsCompleted}</div>
                                <div className="message-cell">{bid.message || '—'}</div>
                                <div className="action-cell">
                                    {bid.is_accepted ? (
                                        <span className="accepted-badge">✅ Accepted</span>
                                    ) : (
                                        <button
                                            className="btn-accept"
                                            onClick={() => handleAccept(bid)}
                                            disabled={accepting === bid.id}
                                        >
                                            {accepting === bid.id ? 'Accepting…' : '🤝 Accept'}
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
