import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Search } from 'lucide-react';

const API = 'http://localhost:8000';

const Customers = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/customers/`)
      .then(res => res.json())
      .then(data => { setCustomers(data); setLoading(false); })
      .catch(err => { console.error(err); setLoading(false); });
  }, []);

  const formatDate = (iso) => {
    if (!iso) return '-';
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const filtered = customers.filter(c =>
    c.email.toLowerCase().includes(search.toLowerCase()) ||
    (c.name && c.name.toLowerCase().includes(search.toLowerCase()))
  );

  if (loading) return <div style={{ padding: '64px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading customers...</div>;

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: 'var(--text-main)' }}>Customers</h1>
        <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
          {customers.length} customer{customers.length !== 1 ? 's' : ''} in the system.
        </p>
      </div>

      {/* Search */}
      <div style={{ position: 'relative', maxWidth: '400px', marginBottom: '24px' }}>
        <Search size={16} style={{ position: 'absolute', left: '14px', top: '13px', color: 'var(--text-muted)' }} />
        <input
          className="input-field"
          style={{ paddingLeft: '40px' }}
          placeholder="Search by name or email..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {/* Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', background: '#F8FAFC' }}>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Customer</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Tier</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Interactions</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Last Interaction</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Last Intent</th>
              <th style={{ padding: '14px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Last Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(c => (
              <tr
                key={c.id}
                className="table-row"
                style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer' }}
                onClick={() => navigate(`/interactions?search=${encodeURIComponent(c.email)}`)}
              >
                <td style={{ padding: '16px' }}>
                  <div style={{ fontWeight: '500' }}>{c.name}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{c.email}</div>
                </td>
                <td style={{ padding: '16px' }}>
                  <span className="pill" style={{ background: c.tier === 'VIP' ? '#FEF3C7' : c.tier === 'Enterprise' ? '#EDE9FE' : '#F1F5F9', color: c.tier === 'VIP' ? 'var(--warning)' : c.tier === 'Enterprise' ? '#7C3AED' : 'var(--text-muted)', border: `1px solid ${c.tier === 'VIP' ? '#FDE68A' : c.tier === 'Enterprise' ? '#DDD6FE' : '#E2E8F0'}` }}>
                    {c.tier}
                  </span>
                </td>
                <td style={{ padding: '16px', fontWeight: '600' }}>{c.interaction_count}</td>
                <td style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '13px' }}>{formatDate(c.last_interaction_date)}</td>
                <td style={{ padding: '16px' }}>
                  {c.last_intent ? (
                    <span className="pill" style={{ background: '#F1F5F9', color: 'var(--primary)', border: '1px solid #E2E8F0' }}>{c.last_intent}</span>
                  ) : '-'}
                </td>
                <td style={{ padding: '16px', fontSize: '13px', color: 'var(--text-muted)' }}>{c.last_status?.replace(/_/g, ' ') || '-'}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <Users size={32} style={{ marginBottom: '12px', opacity: 0.4 }} />
                  <p>No customers found.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Customers;
