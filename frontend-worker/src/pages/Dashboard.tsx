import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Bid {
    id: number;
    job_id: number;
    amount: number;
    created_at: string;
    is_accepted: boolean;
}

interface MonthData {
    month: string;
    earned: number;
}

export default function Dashboard({ workerId }: { workerId: number }) {
    const { t } = useTranslation();
    const [bids, setBids] = useState<Bid[]>([]);
    const [monthlyData, setMonthlyData] = useState<MonthData[]>([]);
    const [yearlyTotal, setYearlyTotal] = useState(0);
    const [stats, setStats] = useState({ total_jobs_completed: 0, total_earnings: 0 });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [bidsRes, statsRes] = await Promise.all([
                    axios.get(`${API}/bids?worker_id=${workerId}`),
                    axios.get(`${API}/bids/worker/${workerId}/stats`),
                ]);
                const allBids: Bid[] = bidsRes.data;
                setBids(allBids);
                setStats(statsRes.data);

                // Compute monthly earnings from accepted bids
                const monthMap: Record<string, number> = {};
                let yearly = 0;
                allBids
                    .filter((b) => b.is_accepted)
                    .forEach((b) => {
                        const d = new Date(b.created_at);
                        const key = d.toLocaleString('default', { month: 'short', year: '2-digit' });
                        monthMap[key] = (monthMap[key] || 0) + b.amount;
                        yearly += b.amount;
                    });

                setMonthlyData(
                    Object.entries(monthMap).map(([month, earned]) => ({ month, earned }))
                );
                setYearlyTotal(yearly);
            } catch (err) {
                console.error('Dashboard fetch error', err);
            }
        };
        fetchData();
    }, [workerId]);

    return (
        <div className="dashboard">
            <h2>{t('earnings_wallet')}</h2>

            <div className="stats-row">
                <div className="stat-card">
                    <span className="stat-label">💰 {t('total_earnings')}</span>
                    <span className="stat-value">₹{yearlyTotal.toLocaleString()}</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">🔨 {t('jobs_completed')}</span>
                    <span className="stat-value">{stats.total_jobs_completed}</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">📋 Total Bids</span>
                    <span className="stat-value">{bids.length}</span>
                </div>
            </div>

            <div className="chart-card">
                <h3>{t('monthly')} Earnings</h3>
                {monthlyData.length === 0 ? (
                    <p className="muted">No accepted bids yet.</p>
                ) : (
                    <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={monthlyData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
                            <XAxis dataKey="month" stroke="#8884d8" />
                            <YAxis stroke="#8884d8" tickFormatter={(v) => `₹${v}`} />
                            <Tooltip
                                formatter={(v: number) => [`₹${v}`, 'Earned']}
                                contentStyle={{ background: '#1a1a2e', border: '1px solid #4ade80', borderRadius: 8 }}
                                labelStyle={{ color: '#a3e635' }}
                            />
                            <Bar dataKey="earned" fill="#4ade80" radius={[6, 6, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
}
