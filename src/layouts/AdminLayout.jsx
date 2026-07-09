import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import './AdminLayout.css';

/**
 * AdminLayout - Main layout wrapper for admin pages
 * Provides the dark futuristic dashboard shell with sidebar and header
 */
const AdminLayout = () => {
  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className="admin-sidebar">
        <div className="sidebar-logo">
          <span className="logo-text">GAL</span>
          <span className="logo-accent">XY</span>
        </div>
        <nav className="sidebar-nav">
          <NavLink
            to="/admin/products"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end
          >
            <span className="nav-icon">📦</span>
            <span className="nav-label">Products</span>
          </NavLink>
          <NavLink
            to="/admin/analytics"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Analytics</span>
          </NavLink>
          <NavLink
            to="/admin/users"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">👥</span>
            <span className="nav-label">Users</span>
          </NavLink>
          <NavLink
            to="/admin/settings"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">⚙️</span>
            <span className="nav-label">Settings</span>
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="admin-avatar">A</div>
          <div className="admin-info">
            <span className="admin-name">Admin</span>
            <span className="admin-role">Super Admin</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
