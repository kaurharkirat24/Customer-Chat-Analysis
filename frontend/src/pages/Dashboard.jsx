import React, { useState, useEffect } from 'react';
import { Activity, Users, AlertTriangle, CheckCircle, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

const Dashboard = () => {
  const navigate = useNavigate();
  const [recentInteractions, setRecentInteractions] = useState([]);
  const [timeframe, setTimeframe] = useState('all');
  const [userName, setUserName] = useState('');

  // Dynamic Metrics Calculation
  const totalIngested = recentInteractions.length;
  const highChurnRisk = recentInteractions.filter(
    it => (it.intent && it.intent.includes('Cancel')) || (it.sentiment && (it.sentiment.includes('Frustrat') || it.sentiment.includes('Neg')))
  ).length;
  
  const autoResolvedCount = recentInteractions.filter(it => it.action !== 'Pending' && it.action !== 'System_Alert' && it.status !== 'Draft_Pending_Approval').length;
  const autoResolvedPercent = totalIngested > 0 ? Math.round((autoResolvedCount / totalIngested) * 100) : 100;

  const humanReviewQueue = recentInteractions.filter(it => it.status === 'Draft_Pending_Approval').length;

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        if (decoded.name) setUserName(decoded.name.split(' ')[0]);
      } catch (e) { console.error("Invalid token", e); }
    }

    fetch(`/api/ingestion/interactions?timeframe=${timeframe}`)
      .then(res => res.json())
      .then(data => setRecentInteractions(data))
      .catch(err => console.error("Error fetching interactions:", err));
  }, [timeframe]);

  const formatDate = (iso) => {
    if (!iso) return '-';
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div style={{ padding: '32px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <h1 className="gradient-text" style={{ fontSize: '32px', fontWeight: '700', letterSpacing: '-0.5px' }}>
            {userName ? `Hi ${userName}` : 'Command Center'}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '15px', marginTop: '4px' }}>Here's what's happening with your customer experience today.</p>
        </div>
        <select 
          className="input-field" 
          style={{ width: 'auto', padding: '10px 16px', cursor: 'pointer', appearance: 'auto' }}
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
        >
          <option value="all">All Time</option>
          <option value="1h">Past 1 Hour</option>
          <option value="1d">Past 24 Hours</option>
          <option value="15d">Past 15 Days</option>
          <option value="30d">Past 30 Days</option>
          <option value="1y">Past 1 Year</option>
        </select>
      </div>

      {/* Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '40px' }}>
        <div className="glass-panel metric-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <Activity color="var(--primary)" size={18} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>Total Ingested</h3>
          </div>
          <p style={{ fontSize: '36px', fontWeight: '700' }}>{totalIngested}</p>
        </div>
        <div className="glass-panel metric-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <AlertTriangle color="var(--danger)" size={18} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>Churn Risk</h3>
          </div>
          <p style={{ fontSize: '36px', fontWeight: '700', color: 'var(--danger)' }}>{highChurnRisk}</p>
        </div>
        <div className="glass-panel metric-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <CheckCircle color="var(--success)" size={18} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>Auto-Resolved</h3>
          </div>
          <p style={{ fontSize: '36px', fontWeight: '700', color: 'var(--success)' }}>{autoResolvedPercent}%</p>
        </div>
        <div className="glass-panel metric-card" style={{ padding: '24px', cursor: 'pointer' }} onClick={() => navigate('/review')}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <Users color="var(--warning)" size={18} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>Review Queue</h3>
          </div>
          <p style={{ fontSize: '36px', fontWeight: '700', color: 'var(--warning)' }}>{humanReviewQueue}</p>
        </div>
      </div>

      {/* Recent Interactions — top 10 */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <MessageSquare size={18} />
            <h2 style={{ fontSize: '18px', fontWeight: '600' }}>Recent Interactions</h2>
          </div>
          <button onClick={() => navigate('/interactions')} style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontWeight: '500', fontSize: '14px' }}>
            View All →
          </button>
        </div>
        
        <div style={{ width: '100%', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', background: '#F8FAFC' }}>
                <th style={{ padding: '12px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Priority</th>
                <th style={{ padding: '12px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Customer</th>
                <th style={{ padding: '12px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Intent</th>
                <th style={{ padding: '12px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Confidence</th>
                <th style={{ padding: '12px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Status</th>
                <th style={{ padding: '12px 16px', fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {recentInteractions.slice(0, 10).map((item) => (
                <tr key={item.id} className="table-row" style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer' }} onClick={() => navigate(`/interactions/${item.id}`)}>
                  <td style={{ padding: '14px 16px', fontWeight: '600', color: item.priority === 'P0' || item.priority === 'P1' ? 'var(--danger)' : 'var(--text-muted)' }}>
                    {item.priority}
                  </td>
                  <td style={{ padding: '14px 16px', fontWeight: '500' }}>{item.user}</td>
                  <td style={{ padding: '14px 16px' }}>
                    <span className="pill" style={{ background: '#F1F5F9', color: 'var(--primary)', border: '1px solid #E2E8F0' }}>
                      {item.intent}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{ color: item.confidence < 0.75 ? 'var(--warning)' : 'var(--success)', fontWeight: '500' }}>
                      {Math.round(item.confidence * 100)}%
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{ color: item.status === 'Draft_Pending_Approval' ? 'var(--warning)' : 'var(--primary)', fontWeight: '500', fontSize: '13px' }}>
                      {item.status?.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', color: 'var(--text-muted)', fontSize: '13px' }}>{formatDate(item.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default Dashboard;
