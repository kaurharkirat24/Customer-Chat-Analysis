import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, Key, Mail, Fingerprint, UserPlus } from 'lucide-react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

const Login = () => {
  const navigate = useNavigate();
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'ADD_YOUR_CLIENT_ID_HERE';

  const handleStandardAuth = async (e) => {
    e.preventDefault();
    setError('');

    const endpoint = isSignUp ? '/auth/signup' : '/auth/login';
    
    try {
      let bodyData;
      let headers = {};

      if (isSignUp) {
        bodyData = JSON.stringify({ email, password, name });
        headers['Content-Type'] = 'application/json';
      } else {
        // FastAPI OAuth2PasswordRequestForm expects form-urlencoded
        bodyData = new URLSearchParams({
          'username': email,
          'password': password
        });
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
      }

      const res = await fetch(`/api${endpoint}`, {
        method: 'POST',
        headers: headers,
        body: bodyData
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Authentication failed');
      }

      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.message);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const res = await fetch('/api/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ credential: credentialResponse.credential })
      });

      if (!res.ok) throw new Error('Google authentication failed on backend');

      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: '20px' }}>
        <div className="glass-panel" style={{ width: '100%', maxWidth: '420px', padding: '48px 40px', borderRadius: '24px' }}>
          
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <div style={{ display: 'inline-flex', padding: '16px', background: 'rgba(127, 149, 209, 0.1)', border: '1px solid rgba(127, 149, 209, 0.3)', borderRadius: '16px', marginBottom: '20px' }}>
              <Fingerprint size={36} color="var(--primary)" />
            </div>
            <h2 className="gradient-text" style={{ fontSize: '28px', fontWeight: '700', letterSpacing: '-0.5px' }}>CX Flow</h2>
            <p style={{ color: 'var(--text-muted)', marginTop: '8px', fontSize: '15px' }}>
              {isSignUp ? 'Create your enterprise account.' : 'Sign in to your enterprise command center.'}
            </p>
          </div>

          {error && (
            <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', padding: '12px', borderRadius: '8px', marginBottom: '16px', fontSize: '14px', textAlign: 'center' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleStandardAuth} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {isSignUp && (
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>Full Name</label>
                <div style={{ position: 'relative' }}>
                  <input type="text" className="input-field" placeholder="Jane Doe" required onChange={(e) => setName(e.target.value)} />
                </div>
              </div>
            )}
            
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
              {isSignUp ? <><UserPlus size={18} /> Sign Up</> : <><LogIn size={18} /> Sign In</>}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
              {isSignUp ? "Already have an account?" : "Don't have an account?"}{' '}
            </span>
            <button 
              type="button" 
              onClick={() => { setIsSignUp(!isSignUp); setError(''); }}
              style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontWeight: '500' }}
            >
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </div>

          <div style={{ margin: '24px 0', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>OR CONTINUE WITH</span>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError('Google Login Failed')}
              theme="filled_black"
              shape="rectangular"
              text={isSignUp ? "signup_with" : "signin_with"}
              size="large"
            />
          </div>

        </div>
      </div>
    </GoogleOAuthProvider>
  );
};

export default Login;
