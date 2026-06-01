import React, { useState, useEffect } from 'react';
import { Activity, Users, AlertTriangle, LogOut, CheckCircle, MessageSquare } from 'lucide-react';

const Dashboard = () => {
  const [recentInteractions, setRecentInteractions] = useState([]);

  // Dynamic Metrics Calculation
  const totalIngested = recentInteractions.length;
  const highChurnRisk = recentInteractions.filter(
    it => (it.intent && it.intent.includes('Cancel')) || (it.sentiment && (it.sentiment.includes('Frustrat') || it.sentiment.includes('Neg')))
  ).length;
  
  // For MVP, we assume any successful LangGraph action is an "auto-resolution" unless it explicitly failed
  const autoResolvedCount = recentInteractions.filter(it => it.action !== 'Pending' && it.action !== 'System_Alert').length;
  const autoResolvedPercent = totalIngested > 0 ? Math.round((autoResolvedCount / totalIngested) * 100) : 100;

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  useEffect(() => {
    // Fetch live data from our backend
    fetch('http://localhost:8000/ingestion/interactions')
      .then(res => res.json())
      .then(data => setRecentInteractions(data))
      .catch(err => console.error("Error fetching interactions:", err));
  }, []);

  return (
    <div style={{ padding: '30px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700' }}>Command Center</h1>
          <p style={{ color: 'var(--text-muted)' }}>AI-Powered Customer Experience Automation</p>
        </div>
        <button onClick={handleLogout} className="btn btn-outline">
          <LogOut size={16} /> Logout
        </button>
      </div>

      {/* Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '40px' }}>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Activity color="var(--primary)" />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Total Ingested</h3>
          </div>
          <p style={{ fontSize: '32px', fontWeight: '600' }}>{totalIngested}</p>
        </div>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <AlertTriangle color="var(--danger)" />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '14px' }}>High Churn Risk</h3>
          </div>
          <p style={{ fontSize: '32px', fontWeight: '600', color: 'var(--danger)' }}>{highChurnRisk}</p>
        </div>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <CheckCircle color="var(--success)" />
            <h3 style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Auto-Resolved</h3>
          </div>
          <p style={{ fontSize: '32px', fontWeight: '600', color: 'var(--success)' }}>{autoResolvedPercent}%</p>
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
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Customer</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>AI Intent</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Sentiment</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Automated Action</th>
                <th style={{ padding: '12px 16px', fontWeight: '500' }}>Time</th>
              </tr>
            </thead>
            <tbody>
              {recentInteractions.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '16px', fontWeight: '500' }}>{item.user}</td>
                  <td style={{ padding: '16px' }}>
                    <span style={{ background: 'rgba(255,255,255,0.1)', padding: '4px 10px', borderRadius: '20px', fontSize: '12px' }}>
                      {item.intent}
                    </span>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <span style={{ 
                      color: item.sentiment.includes('Frustrat') || item.sentiment.includes('Neg') ? 'var(--danger)' : 'var(--success)' 
                    }}>
                      {item.sentiment}
                    </span>
                  </td>
                  <td style={{ padding: '16px', color: 'var(--primary)' }}>{item.action}</td>
                  <td style={{ padding: '16px', color: 'var(--text-muted)' }}>{item.time}</td>
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
