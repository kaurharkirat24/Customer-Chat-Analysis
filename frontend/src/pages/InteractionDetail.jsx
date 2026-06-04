import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, UserCheck, RotateCcw, Clock, Bot, User, ShieldCheck } from 'lucide-react';
import { jwtDecode } from 'jwt-decode';

const API = '/api';

const InteractionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  // Human review state
  const [editedMessage, setEditedMessage] = useState('');
  const [resolutionNote, setResolutionNote] = useState('');
  const [reassignTo, setReassignTo] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const getUserEmail = () => {
    const token = localStorage.getItem('token');
    if (token) {
      try { return jwtDecode(token).sub || 'agent'; } catch { return 'agent'; }
    }
    return 'agent';
  };

  useEffect(() => {
    fetch(`${API}/review/${id}`)
      .then(res => res.json())
      .then(data => {
        setDetail(data);
        // Pre-fill draft message from the last action log
        const lastLog = data.action_history?.[data.action_history.length - 1];
        if (lastLog?.outgoing_message) {
          setEditedMessage(lastLog.outgoing_message);
        }
        setLoading(false);
      })
      .catch(err => { console.error(err); setLoading(false); });
  }, [id]);

  const handleResolve = async (decision) => {
    setSubmitting(true);
    try {
      const body = {
        decision,
        resolved_by: getUserEmail(),
      };
      if (decision === 'approve') body.edited_message = editedMessage;
      if (decision === 'self_resolved') body.resolution_note = resolutionNote;
      if (decision === 'reject') {
        body.reassign_to = reassignTo;
        body.resolution_note = resolutionNote;
      }

      const res = await fetch(`${API}/review/${id}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        // Refresh detail
        const updated = await fetch(`${API}/review/${id}`).then(r => r.json());
        setDetail(updated);
      }
    } catch (err) {
      console.error(err);
    }
    setSubmitting(false);
  };

  if (loading) return <div style={{ padding: '64px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading...</div>;
  if (!detail) return <div style={{ padding: '64px', textAlign: 'center', color: 'var(--text-muted)' }}>Interaction not found.</div>;

  const isPending = detail.status === 'Draft_Pending_Approval';

  const formatDate = (iso) => {
    if (!iso) return '-';
    return new Date(iso).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div style={{ padding: '32px', maxWidth: '960px' }}>
      {/* Back button */}
      <button onClick={() => navigate(-1)} className="btn-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '24px', padding: '8px 16px', border: '1px solid var(--border)', borderRadius: '6px', background: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '14px' }}>
        <ArrowLeft size={16} /> Back
      </button>

      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700' }}>Interaction #{detail.id}</h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
            {detail.customer?.name} · {detail.customer?.email} · {formatDate(detail.created_at)}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className="pill" style={{ background: detail.priority === 'P0' || detail.priority === 'P1' ? '#FEF2F2' : '#F1F5F9', color: detail.priority === 'P0' || detail.priority === 'P1' ? 'var(--danger)' : 'var(--primary)', border: `1px solid ${detail.priority === 'P0' || detail.priority === 'P1' ? '#FECACA' : '#E2E8F0'}`, fontWeight: '600' }}>
            {detail.priority}
          </span>
          <span className="pill" style={{ background: isPending ? '#FEF3C7' : '#F0FDF4', color: isPending ? 'var(--warning)' : 'var(--success)', border: `1px solid ${isPending ? '#FDE68A' : '#BBF7D0'}` }}>
            {detail.status?.replace(/_/g, ' ')}
          </span>
        </div>
      </div>

      {/* Spam Warning Banner */}
      {detail.is_spam && (
        <div style={{ padding: '16px 20px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '8px', marginBottom: '32px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <ShieldCheck size={24} color="var(--danger)" />
          <div>
            <h4 style={{ color: 'var(--danger)', fontWeight: '600', margin: 0, fontSize: '15px' }}>Spam / Phishing Detected</h4>
            <p style={{ color: 'var(--danger)', margin: '4px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
              The AI has flagged this interaction as Spam or a Phishing attempt. Please exercise caution, especially with links or attachments.
            </p>
          </div>
        </div>
      )}

      {/* Two-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '24px', marginBottom: '32px' }}>
        {/* Original Message */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '16px' }}>Original Message</h3>
          <p style={{ lineHeight: '1.7', whiteSpace: 'pre-wrap', color: 'var(--text-main)' }}>{detail.original_message}</p>
        </div>

        {/* AI Analysis */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '16px' }}>AI Analysis</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div><span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Intent</span><br /><span style={{ fontWeight: '600' }}>{detail.ai_intent}</span></div>
            <div><span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Sentiment</span><br /><span style={{ fontWeight: '600' }}>{detail.ai_sentiment}</span></div>
            <div><span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Confidence</span><br /><span style={{ fontWeight: '600', color: detail.confidence < 0.75 ? 'var(--warning)' : 'var(--success)' }}>{Math.round((detail.confidence || 0) * 100)}%</span></div>
            {detail.feature_tag && (
              <div><span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Feature</span><br /><span className="pill" style={{ background: '#FEF3C7', color: 'var(--warning)', border: '1px solid #FDE68A', marginTop: '4px' }}>{detail.feature_tag}</span></div>
            )}
            <div><span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Channel</span><br /><span style={{ fontWeight: '500' }}>{detail.channel}</span></div>
          </div>
        </div>
      </div>

      {/* Human Review Panel */}
      {isPending && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '32px', border: '1px solid #FDE68A' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={20} color="var(--warning)" /> Human Review Required
          </h3>

          {/* Tab-like sections */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Option 1: Approve & Send */}
            <div style={{ padding: '20px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--border)' }}>
              <h4 style={{ fontWeight: '600', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}><Send size={16} /> Approve & Send Email</h4>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>Review and optionally edit the AI-drafted response before sending it to the customer.</p>
              <textarea
                className="input-field"
                rows={4}
                value={editedMessage}
                onChange={e => setEditedMessage(e.target.value)}
                style={{ resize: 'vertical', marginBottom: '12px' }}
              />
              <button className="btn" onClick={() => handleResolve('approve')} disabled={submitting} style={{ fontSize: '14px' }}>
                <Send size={14} /> {submitting ? 'Sending...' : 'Approve & Send'}
              </button>
            </div>

            {/* Option 2: Self-Resolved */}
            <div style={{ padding: '20px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--border)' }}>
              <h4 style={{ fontWeight: '600', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}><UserCheck size={16} /> I Handled It Myself</h4>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>You resolved this outside the system (phone, email, in-person). Add a note for the audit trail.</p>
              <textarea
                className="input-field"
                rows={2}
                placeholder="Brief resolution note..."
                value={resolutionNote}
                onChange={e => setResolutionNote(e.target.value)}
                style={{ resize: 'vertical', marginBottom: '12px' }}
              />
              <button className="btn btn-outline" onClick={() => handleResolve('self_resolved')} disabled={submitting} style={{ fontSize: '14px' }}>
                <UserCheck size={14} /> {submitting ? 'Saving...' : 'Mark as Resolved'}
              </button>
            </div>

            {/* Option 3: Reject & Re-Route */}
            <div style={{ padding: '20px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--border)' }}>
              <h4 style={{ fontWeight: '600', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}><RotateCcw size={16} /> Reject & Re-Route</h4>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>The AI got the classification wrong. Select the correct category.</p>
              <select className="input-field" value={reassignTo} onChange={e => setReassignTo(e.target.value)} style={{ marginBottom: '12px', appearance: 'auto', cursor: 'pointer' }}>
                <option value="">Select correct category...</option>
                <option value="retention">Retention (Cancel/Downgrade)</option>
                <option value="frustration">Frustration (Angry Customer)</option>
                <option value="billing">Billing / Payment</option>
                <option value="security">Security Incident</option>
                <option value="compliance">Legal / Compliance</option>
                <option value="escalation">VIP Escalation</option>
                <option value="feedback">Product Feedback</option>
              </select>
              <button className="btn btn-outline" onClick={() => handleResolve('reject')} disabled={submitting || !reassignTo} style={{ fontSize: '14px', color: 'var(--danger)', borderColor: 'var(--danger)' }}>
                <RotateCcw size={14} /> {submitting ? 'Re-Routing...' : 'Reject & Re-Route'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Resolution info if already resolved */}
      {detail.resolved_by && (
        <div className="glass-panel" style={{ padding: '20px', marginBottom: '32px', background: '#F0FDF4', border: '1px solid #BBF7D0' }}>
          <h4 style={{ fontWeight: '600', color: 'var(--success)', marginBottom: '8px' }}>✓ Resolved</h4>
          <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
            Resolved by <strong>{detail.resolved_by}</strong>
            {detail.resolution_note && <> — {detail.resolution_note}</>}
          </p>
        </div>
      )}

      {/* Action History Timeline */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '20px' }}>Action History</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {detail.action_history?.map((log, idx) => (
            <div key={log.id} style={{ display: 'flex', gap: '16px', paddingBottom: '20px', borderLeft: idx < detail.action_history.length - 1 ? '2px solid var(--border)' : '2px solid transparent', marginLeft: '8px', paddingLeft: '20px', position: 'relative' }}>
              <div style={{ position: 'absolute', left: '-5px', top: '0', width: '12px', height: '12px', borderRadius: '50%', background: log.status === 'Success' ? 'var(--success)' : 'var(--danger)', border: '2px solid white' }}></div>
              <div>
                <div style={{ fontWeight: '600', fontSize: '14px' }}>{log.action_type?.replace(/_/g, ' ')}</div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>{log.outgoing_message}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
                  <Clock size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />{formatDate(log.created_at)}
                </div>
              </div>
            </div>
          ))}
          {(!detail.action_history || detail.action_history.length === 0) && (
            <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>No actions recorded yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default InteractionDetail;
