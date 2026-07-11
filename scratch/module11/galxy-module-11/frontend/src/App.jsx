import React, { useState, useEffect } from 'react';
import NotificationBell from '../components/notifications/NotificationBell';
import TelegramLinkSettings from '../components/notifications/TelegramLinkSettings';
import useNotifications, { NotificationsProvider } from '../hooks/useNotifications';

import { API_BASE_URL } from './config';

function Dashboard() {
  const { fetchNotifications } = useNotifications();
  const [currentUser, setCurrentUser] = useState(localStorage.getItem('galxy_username') || 'customer1');
  const [alertMessage, setAlertMessage] = useState('Your neon name board status changed to In Production!');
  const [orderNumber, setOrderNumber] = useState('GLX-2026-00042');
  const [triggering, setTriggering] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  // Save user changes to localstorage and fetch a valid signed JWT token from the backend
  const handleUserChange = async (newUser) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: newUser })
      });
      const data = await response.json();
      if (data.success && data.token) {
        localStorage.setItem('galxy_token', data.token);
        localStorage.setItem('galxy_username', newUser);
        setCurrentUser(newUser);
        // Reload notifications for new user
        window.location.reload();
      }
    } catch (err) {
      console.error("Failed to authenticate as mock user", err);
    }
  };

  // Check if token exists on load, otherwise request a mock token for customer1
  useEffect(() => {
    const initToken = async () => {
      const token = localStorage.getItem('galxy_token');
      if (!token) {
        await handleUserChange('customer1');
      }
    };
    initToken();
  }, []);

  // Function to post a mock notification to the backend
  const triggerMockNotification = async (e) => {
    e.preventDefault();
    if (!alertMessage.trim()) return;

    setTriggering(true);
    setStatusMsg('');
    try {
      const token = localStorage.getItem('galxy_token');
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/mock-trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: alertMessage.trim(),
          order_id: orderNumber.trim() || undefined
        })
      });
      const data = await response.json();
      if (data.success) {
        setStatusMsg('Notification triggered! Watch the bell badge.');
        // Refresh notifications to update unread badge immediately (shared state via Context!)
        fetchNotifications();
        // Clear message after 3 seconds
        setTimeout(() => setStatusMsg(''), 3000);
      } else {
        setStatusMsg(`Failed to trigger: ${data.message}`);
      }
    } catch (err) {
      setStatusMsg(`Network error: ${err.message}`);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0B0F] text-[#F4F4F7] flex flex-col font-sans">
      
      {/* Navigation Header */}
      <header className="border-b border-[#8A8A97]/15 bg-[#16161C]/50 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Glowing Brand Mark */}
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#FF2E8A] via-[#9B5CFF] to-[#18E7FF] flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(155,92,255,0.4)]">
              G
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-wider text-[#F4F4F7]">
                GALXY
              </h1>
              <p className="text-[10px] text-[#8A8A97] tracking-widest uppercase">Lighting & Craft Studio</p>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            {/* User Account State indicator */}
            <div className="hidden sm:flex items-center gap-2 bg-[#0B0B0F]/60 border border-[#8A8A97]/10 px-3 py-1 rounded-lg">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs text-[#8A8A97]">Active Account:</span>
              <strong className="text-xs text-[#18E7FF] font-mono">{currentUser}</strong>
            </div>

            {/* Notification Bell Component */}
            <NotificationBell />
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        
        {/* Left Column: Control Panel / Mock Trigger */}
        <section className="bg-[#16161C] border border-[#8A8A97]/10 rounded-2xl p-6 space-y-6">
          <div>
            <h2 className="text-xl font-bold tracking-wide text-[#F4F4F7] mb-1">
              DEMO CONTROL ROOM
            </h2>
            <p className="text-xs text-[#8A8A97]">Simulate user logins and order updates in real-time.</p>
          </div>

          {/* User switcher */}
          <div className="space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#9B5CFF]">
              1. Toggle User Account
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleUserChange('customer1')}
                className={`py-2 px-4 rounded-xl text-xs font-semibold transition-all duration-300 border ${
                  currentUser === 'customer1'
                    ? 'bg-[#9B5CFF]/15 border-[#9B5CFF] text-[#F4F4F7]'
                    : 'bg-[#0B0B0F] border-[#8A8A97]/10 text-[#8A8A97] hover:text-[#F4F4F7]'
                }`}
              >
                Customer 1
              </button>
              <button
                onClick={() => handleUserChange('customer2')}
                className={`py-2 px-4 rounded-xl text-xs font-semibold transition-all duration-300 border ${
                  currentUser === 'customer2'
                    ? 'bg-[#9B5CFF]/15 border-[#9B5CFF] text-[#F4F4F7]'
                    : 'bg-[#0B0B0F] border-[#8A8A97]/10 text-[#8A8A97] hover:text-[#F4F4F7]'
                }`}
              >
                Customer 2
              </button>
            </div>
          </div>

          {/* Alert Simulator */}
          <div className="space-y-3 pt-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#9B5CFF]">
              2. Trigger Custom Order Alerts
            </h3>
            <form onSubmit={triggerMockNotification} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] text-[#8A8A97] uppercase font-bold tracking-wider">
                  Notification Message
                </label>
                <textarea
                  value={alertMessage}
                  onChange={(e) => setAlertMessage(e.target.value)}
                  rows="3"
                  className="w-full bg-[#0B0B0F] border border-[#8A8A97]/20 rounded-xl px-3 py-2 text-xs text-[#F4F4F7] focus:border-[#18E7FF] focus:outline-none focus:ring-1 focus:ring-[#18E7FF] transition-all duration-200"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-[#8A8A97] uppercase font-bold tracking-wider">
                  Order Number (Optional)
                </label>
                <input
                  type="text"
                  value={orderNumber}
                  onChange={(e) => setOrderNumber(e.target.value)}
                  className="w-full bg-[#0B0B0F] border border-[#8A8A97]/20 rounded-xl px-3 py-2 text-xs text-[#F4F4F7] focus:border-[#18E7FF] focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={triggering || !alertMessage.trim()}
                className="w-full py-2.5 bg-[#18E7FF] hover:bg-[#18E7FF]/85 disabled:opacity-40 text-black font-bold rounded-xl text-xs tracking-wider transition-all duration-300 shadow-[0_0_15px_rgba(24,231,255,0.25)] focus:outline-none"
              >
                {triggering ? 'Triggering...' : 'Trigger Order Status Change'}
              </button>
            </form>

            {statusMsg && (
              <div className="text-center text-xs text-[#18E7FF] font-medium bg-[#18E7FF]/5 border border-[#18E7FF]/20 py-2 rounded-xl">
                {statusMsg}
              </div>
            )}
          </div>
        </section>

        {/* Right Column: Telegram Settings Card */}
        <section className="space-y-6 flex flex-col items-center justify-center md:items-start md:justify-start">
          <TelegramLinkSettings />

          {/* Design System Reference Information */}
          <div className="bg-[#16161C]/60 border border-[#8A8A97]/10 rounded-2xl p-5 w-full space-y-3">
            <h4 className="text-xs uppercase tracking-wider font-bold text-[#FF2E8A]">
              Design System Alignment
            </h4>
            <ul className="text-[11px] text-[#8A8A97] space-y-2 list-disc list-inside leading-relaxed">
              <li>Near-black base (<code className="text-[#F4F4F7]">#0B0B0F</code>) ensures neon elements jump visually.</li>
              <li>Interactive states utilize box-shadow glows in the component's color.</li>
              <li>Glassmorphism panels feature <code className="text-[#F4F4F7]">backdrop-blur-md</code> and gradient borders.</li>
              <li>Unread notifications are decorated with a Violet pulse indicator.</li>
            </ul>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-[#8A8A97]/15 py-6 text-center text-xs text-[#8A8A97]">
        <p>GALXY Studio CMS & Storefront &copy; 2026. Handcrafted for LTI Innovate.</p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <NotificationsProvider>
      <Dashboard />
    </NotificationsProvider>
  );
}
