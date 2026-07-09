import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { FiSliders, FiClock, FiGrid } from 'react-icons/fi';
import AdminLayout from './layouts/AdminLayout';
import AdminProductListPage from './pages/admin/products/AdminProductListPage';
import AdminProductFormPage from './pages/admin/products/AdminProductFormPage';
import AdminProductDetailsPage from './pages/admin/products/AdminProductDetailsPage';
import NotFoundPage from './pages/NotFoundPage';

/**
 * PlaceholderPage - A themed view for sections still under development
 */
const PlaceholderPage = ({ title, icon: Icon }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '70vh',
      color: '#F4F4F7',
      fontFamily: "'Outfit', 'Inter', sans-serif"
    }}>
      <div style={{
        background: 'rgba(22, 22, 28, 0.5)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '20px',
        padding: '60px 40px',
        textAlign: 'center',
        maxWidth: '500px',
        width: '100%',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
      }}>
        <Icon style={{ fontSize: '64px', color: '#FF2E8A', marginBottom: '24px', opacity: 0.8 }} />
        <h2 style={{ fontSize: '26px', fontWeight: 800, marginBottom: '12px' }}>{title} Component</h2>
        <p style={{ color: '#8A8A97', fontSize: '15px', lineHeight: 1.6, marginBottom: '28px' }}>
          This sector of the GALXY dashboard is undergoing optimization. Normal communications will resume shortly.
        </p>
        <Link to="/admin/products" style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '10px 24px',
          borderRadius: '8px',
          color: '#F4F4F7',
          fontWeight: 600,
          textDecoration: 'none',
          transition: 'all 0.2s ease'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
          e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        }}
        >
          <FiGrid /> Go to Products Catalog
        </Link>
      </div>
    </div>
  );
};

/**
 * App - Root application component
 * Sets up routing and global providers for GALXY Admin Dashboard
 */
const App = () => {
  return (
    <Router>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#16161C',
            color: '#F4F4F7',
            border: '1px solid rgba(255, 46, 138, 0.3)',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
            fontFamily: "'Inter', sans-serif",
          },
          success: {
            iconTheme: { primary: '#FF2E8A', secondary: '#F4F4F7' },
          },
          error: {
            iconTheme: { primary: '#FF4D4D', secondary: '#F4F4F7' },
          },
        }}
      />
      <Routes>
        <Route path="/" element={<Navigate to="/admin/products" replace />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route path="products" element={<AdminProductListPage />} />
          <Route path="products/:id" element={<AdminProductDetailsPage />} />
          <Route path="products/:id/edit" element={<AdminProductFormPage />} />
          <Route path="analytics" element={<PlaceholderPage title="Analytics" icon={FiClock} />} />
          <Route path="users" element={<PlaceholderPage title="User Management" icon={FiSliders} />} />
          <Route path="settings" element={<PlaceholderPage title="Settings" icon={FiSliders} />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  );
};

export default App;
