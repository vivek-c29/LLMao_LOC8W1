import { useEffect, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';

const API_WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export function useWebSocket(workerId: number | null) {
    const wsRef = useRef<WebSocket | null>(null);

    const connect = useCallback(() => {
        if (!workerId) return;
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const ws = new WebSocket(`${API_WS_URL}/ws/${workerId}`);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('[WS] Connected as worker', workerId);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'deal_done') {
                    toast.custom(
                        (t) => (
                            <div
                                style={{
                                    background: 'linear-gradient(135deg, #1a1a2e, #16213e)',
                                    color: '#fff',
                                    padding: '20px 28px',
                                    borderRadius: '16px',
                                    boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
                                    border: '1px solid #4ade80',
                                    maxWidth: '380px',
                                    opacity: t.visible ? 1 : 0,
                                    transition: 'opacity 0.3s ease',
                                }}
                            >
                                <h3 style={{ margin: '0 0 8px', color: '#4ade80', fontSize: '1.1rem' }}>🎉 Deal Done!</h3>
                                <p style={{ margin: 0, fontSize: '0.95rem', lineHeight: 1.5 }}>{data.message}</p>
                                <p style={{ margin: '8px 0 0', fontSize: '0.85rem', color: '#a3e635' }}>Bid Amount: ₹{data.amount}</p>
                            </div>
                        ),
                        { duration: 8000, position: 'top-right' }
                    );
                }
            } catch {
                // ignore non-JSON messages
            }
        };

        ws.onclose = () => {
            console.log('[WS] Disconnected — reconnecting in 3s...');
            setTimeout(connect, 3000);
        };

        ws.onerror = (err) => {
            console.error('[WS] Error', err);
            ws.close();
        };
    }, [workerId]);

    useEffect(() => {
        connect();
        return () => {
            wsRef.current?.close();
        };
    }, [connect]);
}
