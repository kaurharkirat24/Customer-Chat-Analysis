import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, MessageSquare } from 'lucide-react';

const API = 'http://localhost:8000';

const Interactions = () => {
  const navigate = useNavigate();
  const [interactions, setInteractions] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [timeframe, setTimeframe] = useState('all');

  useEffect(() => {
    const params = new URLSearchParams();
    if (timeframe !== 'all') params.append('timeframe', timeframe);
    if (search) params.append('search', search);
    if (statusFilter) params.append('status', statusFilter);
    if (priorityFilter) params.append('priority', priorityFilter);

    fetch(`${API}/ingestion/interactions?${params.toString()}`)
      .then(res => res.json())
      .then(data => setInteractions(data))
      .catch(err => console.error(err));
  }, [search, statusFilter, priorityFilter, timeframe]);

  const formatDate = (iso) => {
    if (!iso) return '-';
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const statusColor = (s) => {
    if (s === 'Draft_Pending_Approval') return 'var(--warning)';
    if (s === 'Resolved' || s === 'Resolved_By_Human' || s === 'Action_Taken' || s === 'Logged') return 'var(--success)';
    if (s === 'Escalated' || s === 'Failed_AI_Analysis') return 'var(--danger)';
    return 'var(--text-muted)';
  };

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: 'var(--text-main)' }}>Interactions</h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>Browse, search, and filter all customer interactions.</p>
      </div>

      {/* Search + Filters */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: '1', minWidth: '240px' }}>
          <Search size={16} style={{ position: 'absolute', left: '14px', top: '13px', color: 'var(--text-muted)' }} />
          <input
            className="input-field"
            style={{ paddingLeft: '40px' }}
            placeholder="Search by email or message..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select className="input-field" style={{ width: 'auto', cursor: 'pointer', appearance: 'auto' }} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="Pending">Pending</option>
          <option value="Action_Taken">Action Taken</option>
          <option value="Escalated">Escalated</option>
          <option value="Logged">Logged</option>
          <option value="Draft_Pending_Approval">Pending Review</option>
          <option value="Resolved">Resolved</option>
          <option value="Resolved_By_Human">Resolved by Human</option>
        </select>
        <select className="input-field" style={{ width: 'auto', cursor: 'pointer', appearance: 'auto' }} value={priorityFilter} onChange={e => setPriorityFilter(e.target.value)}>
          <option value="">All Priorities</option>
          <option value="P0">P0 — Critical</option>
          <option value="P1">P1 — High</option>
          <option value="P2">P2 — Medium</option>
          <option value="P3">P3 — Low</option>
        </select>
        <select className="input-field" style={{ width: 'auto', cursor: 'pointer', appearance: 'auto' }} value={timeframe} onChange={e => setTimeframe(e.target.value)}>
          <option value="all">All Time</option>
          <option value="1h">Past 1 Hour</option>
          <option value="1d">Past 24 Hours</option>
          <option value="15d">Past 15 Days</option>
          <option value="30d">Past 30 Days</option>
        </select>
      </div>

      {/* Count */}
      <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '16px' }}>
        Showing {interactions.length} interaction{interactions.length !== 1 ? 's' : ''}
      </p>

      {/* Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', background: '#F8FAFC' }}>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Priority</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Customer</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Message Preview</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Intent</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Status</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Date</th>
            </tr>
          </thead>
          <tbody>
            {interactions.map(item => (
              <tr
                key={item.id}
                className="table-row"
                style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer' }}
                onClick={() => navigate(`/interactions/${item.id}`)}
              >
                <td style={{ padding: '16px', fontWeight: '600', color: item.priority === 'P0' || item.priority === 'P1' ? 'var(--danger)' : 'var(--text-muted)' }}>
                  {item.priority}
                </td>
                <td style={{ padding: '16px' }}>
                  <div style={{ fontWeight: '500' }}>{item.customer_name}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{item.user}</div>
                </td>
                <td style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '13px', maxWidth: '320px' }}>
                  {item.message_preview || '-'}
                </td>
                <td style={{ padding: '16px' }}>
                  <span className="pill" style={{ background: '#F1F5F9', color: 'var(--primary)', border: '1px solid #E2E8F0' }}>
                    {item.intent}
                  </span>
                </td>
                <td style={{ padding: '16px' }}>
                  <span style={{ color: statusColor(item.status), fontWeight: '500', fontSize: '13px' }}>
                    {item.status?.replace(/_/g, ' ')}
                  </span>
                </td>
                <td style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '13px' }}>
                  {formatDate(item.created_at)}
                </td>
              </tr>
            ))}
            {interactions.length === 0 && (
              <tr>
                <td colSpan={6} style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <MessageSquare size={32} style={{ marginBottom: '12px', opacity: 0.4 }} />
                  <p>No interactions found matching your filters.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Interactions;
