import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Interactions from './pages/Interactions';
import InteractionDetail from './pages/InteractionDetail';
import ReviewQueue from './pages/ReviewQueue';
import Customers from './pages/Customers';
import AppLayout from './components/AppLayout';
import './index.css';

function App() {
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* All authenticated routes use AppLayout (Sidebar + Content) */}
        <Route path="/dashboard" element={
          isAuthenticated ? <AppLayout><Dashboard /></AppLayout> : <Navigate to="/login" />
        } />
        <Route path="/interactions" element={
          isAuthenticated ? <AppLayout><Interactions /></AppLayout> : <Navigate to="/login" />
        } />
        <Route path="/interactions/:id" element={
          isAuthenticated ? <AppLayout><InteractionDetail /></AppLayout> : <Navigate to="/login" />
        } />
        <Route path="/review" element={
          isAuthenticated ? <AppLayout><ReviewQueue /></AppLayout> : <Navigate to="/login" />
        } />
        <Route path="/customers" element={
          isAuthenticated ? <AppLayout><Customers /></AppLayout> : <Navigate to="/login" />
        } />

        <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
      </Routes>
    </Router>
  );
}

export default App;
