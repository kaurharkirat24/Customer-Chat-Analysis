import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

const API = '/api';

const ReviewQueue = () => {
  const navigate = useNavigate();
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/review/queue`)
      .then(res => res.json())
      .then(data => { setQueue(data); setLoading(false); })
      .catch(err => { console.error(err); setLoading(false); });
  }, []);

  const formatDate = (iso) => {
    if (!iso) return '-';
    return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  if (loading) return <div style={{ padding: '64px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading review queue...</div>;

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: 'var(--text-main)' }}>Review Queue</h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
          {queue.length} interaction{queue.length !== 1 ? 's' : ''} awaiting human review. Sorted by priority.
        </p>
      </div>

      {queue.length === 0 ? (
        <div className="glass-panel" style={{ padding: '64px', textAlign: 'center' }}>
          <ShieldCheck size={40} color="var(--success)" style={{ marginBottom: '16px' }} />
          <h3 style={{ fontWeight: '600', marginBottom: '8px' }}>All clear!</h3>
          <p style={{ color: 'var(--text-muted)' }}>No interactions need human review right now.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {queue.map(item => (
            <div
              key={item.id}
              className="glass-panel table-row"
              style={{ padding: '24px', cursor: 'pointer', display: 'grid', gridTemplateColumns: '60px 1fr auto', gap: '20px', alignItems: 'start' }}
              onClick={() => navigate(`/interactions/${item.id}`)}
            >
              {/* Priority badge */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                <span style={{ fontWeight: '700', fontSize: '16px', color: item.priority === 'P0' || item.priority === 'P1' ? 'var(--danger)' : 'var(--text-muted)' }}>
                  {item.priority}
                </span>
                {(item.priority === 'P0' || item.priority === 'P1') && <AlertTriangle size={16} color="var(--danger)" />}
              </div>

              {/* Content */}
              <div>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontWeight: '600' }}>{item.customer_name}</span>
                  <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{item.customer_email}</span>
                  <span className="pill" style={{ background: '#F1F5F9', color: 'var(--primary)', border: '1px solid #E2E8F0' }}>{item.ai_intent}</span>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: '1.6', marginBottom: '10px' }}>
                  {item.original_message?.slice(0, 200)}{item.original_message?.length > 200 ? '...' : ''}
                </p>
                {item.ai_draft_response && (
                  <div style={{ padding: '12px', background: '#FFFBEB', borderRadius: '6px', border: '1px solid #FDE68A', fontSize: '13px', color: 'var(--text-main)' }}>
                    <strong style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--warning)', letterSpacing: '0.5px' }}>AI Draft Response</strong>
                    <p style={{ marginTop: '6px' }}>{item.ai_draft_response}</p>
                  </div>
                )}
              </div>

              {/* Right side */}
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{formatDate(item.created_at)}</div>
                <div style={{ fontSize: '13px', color: item.confidence < 0.75 ? 'var(--warning)' : 'var(--success)', fontWeight: '500', marginTop: '4px' }}>
                  {Math.round((item.confidence || 0) * 100)}% confidence
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReviewQueue;
