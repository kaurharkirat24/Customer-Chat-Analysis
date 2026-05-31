import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, Key, Mail, Fingerprint } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    localStorage.setItem('token', 'mock_jwt_token_123');
    // Force reload to apply auth state in MVP routing
    window.location.href = '/dashboard'; 
  };

  const handleOAuth = () => {
    localStorage.setItem('token', 'mock_oauth_token_456');
    window.location.href = '/dashboard';
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: '20px' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '420px', padding: '40px' }}>
        
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ display: 'inline-flex', padding: '12px', background: 'var(--primary)', borderRadius: '12px', marginBottom: '16px' }}>
            <Fingerprint size={32} color="white" />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: '600' }}>CX Flow</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>Sign in to your enterprise command center.</p>
        </div>

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>Email Address</label>
            <div style={{ position: 'relative' }}>
              <Mail size={18} style={{ position: 'absolute', left: '12px', top: '14px', color: 'var(--text-muted)' }} />
              <input type="email" className="input-field" style={{ paddingLeft: '40px' }} placeholder="agent@company.com" required onChange={(e) => setEmail(e.target.value)} />
            </div>
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>Password</label>
            <div style={{ position: 'relative' }}>
              <Key size={18} style={{ position: 'absolute', left: '12px', top: '14px', color: 'var(--text-muted)' }} />
              <input type="password" className="input-field" style={{ paddingLeft: '40px' }} placeholder="••••••••" required onChange={(e) => setPassword(e.target.value)} />
            </div>
          </div>

          <button type="submit" className="btn" style={{ width: '100%', marginTop: '8px' }}>
            <LogIn size={18} /> Sign In
          </button>
        </form>

        <div style={{ margin: '24px 0', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>OR CONTINUE WITH</span>
          <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
        </div>

        <button onClick={handleOAuth} className="btn btn-outline" style={{ width: '100%' }}>
          Google Workspace SSO
        </button>

      </div>
    </div>
  );
};

export default Login;
