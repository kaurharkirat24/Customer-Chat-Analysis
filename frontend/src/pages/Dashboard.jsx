import React, { useState, useEffect } from 'react';
import { Activity, Users, AlertTriangle, LogOut, CheckCircle, MessageSquare } from 'lucide-react';
import { jwtDecode } from 'jwt-decode';

const Dashboard = () => {
  const [recentInteractions, setRecentInteractions] = useState([]);
  const [timeframe, setTimeframe] = useState('all');
  const [userName, setUserName] = useState('');

  // Dynamic Metrics Calculation
  const totalIngested = recentInteractions.length;
  const highChurnRisk = recentInteractions.filter(
    it => (it.intent && it.intent.includes('Cancel')) || (it.sentiment && (it.sentiment.includes('Frustrat') || it.sentiment.includes('Neg')))
  ).length;
  
  // For MVP, we assume any successful LangGraph action is an "auto-resolution" unless it explicitly failed or is pending review
  const autoResolvedCount = recentInteractions.filter(it => it.action !== 'Pending' && it.action !== 'System_Alert' && it.status !== 'Draft_Pending_Approval').length;
  const autoResolvedPercent = totalIngested > 0 ? Math.round((autoResolvedCount / totalIngested) * 100) : 100;

  const humanReviewQueue = recentInteractions.filter(it => it.status === 'Draft_Pending_Approval').length;

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  useEffect(() => {
    // Fetch user name from token
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        if (decoded.name) {
          setUserName(decoded.name.split(' ')[0]);
        }
      } catch (e) {
        console.error("Invalid token", e);
      }
    }

    // Fetch live data from our backend
    fetch(`http://localhost:8000/ingestion/interactions?timeframe=${timeframe}`)
      .then(res => res.json())
      .then(data => setRecentInteractions(data))
      .catch(err => console.error("Error fetching interactions:", err));
  }, [timeframe]);

  return (
    <div style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <h1 className="gradient-text" style={{ fontSize: '32px', fontWeight: '700', letterSpacing: '-0.5px' }}>
            {userName ? `Hi ${userName}` : 'Command Center'}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '15px', marginTop: '4px' }}>Here's what's happening with your customer experience today.</p>
        </div>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
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
          <button onClick={handleLogout} className="btn btn-outline">
            <LogOut size={16} /> Logout
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', marginBottom: '48px' }}>
        <div className="glass-panel metric-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <Activity color="var(--primary)" size={20} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '600' }}>Total Ingested</h3>
          </div>
          <p style={{ fontSize: '40px', fontWeight: '700' }}>{totalIngested}</p>
        </div>
        <div className="glass-panel metric-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <AlertTriangle color="var(--danger)" size={20} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '600' }}>High Churn Risk</h3>
          </div>
          <p style={{ fontSize: '40px', fontWeight: '700', color: 'var(--danger)' }}>{highChurnRisk}</p>
        </div>
        <div className="glass-panel metric-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <CheckCircle color="var(--success)" size={20} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '600' }}>Auto-Resolved</h3>
          </div>
          <p style={{ fontSize: '40px', fontWeight: '700', color: 'var(--success)' }}>{autoResolvedPercent}%</p>
        </div>
        <div className="glass-panel metric-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <Users color="var(--warning)" size={20} />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '600' }}>Human Review Queue</h3>
          </div>
          <p style={{ fontSize: '40px', fontWeight: '700', color: 'var(--warning)' }}>{humanReviewQueue}</p>
        </div>
      </div>

      {/* Interactions Hub */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <MessageSquare />
          <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Recent Interactions & Actions</h2>
        </div>
        
        <div style={{ width: '100%', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Priority</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Customer</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>AI Intent</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Feature Tag</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Confidence</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Status / Action</th>
              </tr>
            </thead>
            <tbody>
              {recentInteractions.map((item) => (
                <tr key={item.id} className="table-row" style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '20px 16px', fontWeight: '600', color: item.priority === 'P0' || item.priority === 'P1' ? 'var(--danger)' : 'var(--text-muted)' }}>
                    {item.priority}
                  </td>
                  <td style={{ padding: '20px 16px', fontWeight: '500' }}>{item.user}</td>
                  <td style={{ padding: '20px 16px' }}>
                    <span className="pill" style={{ background: '#F1F5F9', color: 'var(--primary)', border: '1px solid #E2E8F0' }}>
                      {item.intent}
                    </span>
                  </td>
                  <td style={{ padding: '20px 16px', color: 'var(--text-muted)' }}>
                    {item.feature ? <span className="pill" style={{ background: '#FEF3C7', color: 'var(--warning)', border: '1px solid #FDE68A' }}>{item.feature}</span> : '-'}
                  </td>
                  <td style={{ padding: '20px 16px' }}>
                    <span style={{ color: item.confidence < 0.75 ? 'var(--warning)' : 'var(--success)', fontWeight: '500' }}>
                      {Math.round(item.confidence * 100)}%
                    </span>
                  </td>
                  <td style={{ padding: '20px 16px' }}>
                    {item.status === 'Draft_Pending_Approval' ? (
                      <button className="btn" style={{ padding: '6px 14px', fontSize: '13px', background: 'var(--warning)', color: '#000' }}>Review Draft</button>
                    ) : (
                      <span style={{ color: 'var(--primary)', fontWeight: '500' }}>{item.action}</span>
                    )}
                  </td>
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
