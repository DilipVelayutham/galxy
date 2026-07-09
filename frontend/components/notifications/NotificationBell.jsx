import React, { useState, useEffect, useRef } from 'react';
import useNotifications from '../../hooks/useNotifications';
import NotificationDropdown from './NotificationDropdown';

export default function NotificationBell() {
  const { unreadCount, fetchNotifications } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const bellRef = useRef(null);

  // Poll for notifications every 30 seconds for real-time updates
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(() => {
      fetchNotifications();
    }, 30000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (bellRef.current && !bellRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="relative inline-block" ref={bellRef}>
      {/* Glow shadow and scale animation on hover */}
      <button
        onClick={handleToggle}
        className="relative p-2 text-[#8A8A97] hover:text-[#18E7FF] transition-all duration-300 rounded-full focus:outline-none focus:ring-2 focus:ring-[#18E7FF]/50 bg-[#16161C]/50 hover:bg-[#16161C] border border-[#8A8A97]/10 hover:border-[#18E7FF]/30"
        style={{
          boxShadow: isOpen ? '0 0 12px rgba(24, 231, 255, 0.4)' : 'none',
        }}
        aria-label="Toggle notifications"
      >
        {/* Bell SVG */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`w-6 h-6 transition-transform duration-300 ${isOpen ? 'rotate-12' : 'hover:animate-bounce'}`}
        >
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
        </svg>

        {/* Pulse unread count badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#FF2E8A] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-5 w-5 bg-[#FF2E8A] text-white text-[10px] font-bold items-center justify-center border border-[#0B0B0F]">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          </span>
        )}
      </button>

      {/* Renders the Dropdown component if open */}
      {isOpen && (
        <div className="absolute right-0 mt-3 w-80 sm:w-96 z-50 origin-top-right transform transition-all duration-300 ease-out">
          <NotificationDropdown onClose={() => setIsOpen(false)} />
        </div>
      )}
    </div>
  );
}
