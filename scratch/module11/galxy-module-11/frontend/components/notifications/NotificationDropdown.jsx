import React, { useEffect, useState } from 'react';
import useNotifications from '../../hooks/useNotifications';

export default function NotificationDropdown({ onClose }) {
  const {
    notifications,
    loading,
    error,
    page,
    totalPages,
    fetchNotifications,
    markAsRead,
    markAllAsRead
  } = useNotifications();

  const [activeTab, setActiveTab] = useState('all'); // 'all', 'unread'

  // Fetch notifications on mount & when filter/page changes
  useEffect(() => {
    const isReadFilter = activeTab === 'unread' ? false : null;
    fetchNotifications(1, isReadFilter);
  }, [fetchNotifications, activeTab]);

  // Spec: "triggers mark-all-read on open"
  // We trigger it on mount when the dropdown opens and the user is on the 'all' tab
  useEffect(() => {
    if (activeTab === 'all') {
      const timer = setTimeout(() => {
        markAllAsRead();
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [markAllAsRead, activeTab]);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      const isReadFilter = activeTab === 'unread' ? false : null;
      fetchNotifications(newPage, isReadFilter);
    }
  };

  const formatTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <div
      className="bg-[#16161C]/95 backdrop-blur-md border border-[#9B5CFF]/30 rounded-xl overflow-hidden shadow-2xl flex flex-col max-h-[500px]"
      style={{
        boxShadow: '0 10px 30px -10px rgba(155, 92, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
      }}
    >
      {/* Dropdown Header */}
      <div className="p-4 border-b border-[#8A8A97]/10 flex items-center justify-between bg-[#16161C]/50">
        <h3 className="font-bold text-[#F4F4F7] tracking-wide text-sm flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#18E7FF] animate-pulse"></span>
          NOTIFICATIONS
        </h3>
        <button
          onClick={markAllAsRead}
          className="text-xs text-[#FF2E8A] hover:text-[#FF2E8A]/80 transition-colors duration-200 font-semibold focus:outline-none"
        >
          Mark all as read
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-[#8A8A97]/10 px-2 bg-[#0B0B0F]/30 text-xs">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-3 py-2 font-medium transition-colors border-b-2 focus:outline-none ${
            activeTab === 'all'
              ? 'text-[#18E7FF] border-[#18E7FF]'
              : 'text-[#8A8A97] border-transparent hover:text-[#F4F4F7]'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setActiveTab('unread')}
          className={`px-3 py-2 font-medium transition-colors border-b-2 focus:outline-none ${
            activeTab === 'unread'
              ? 'text-[#18E7FF] border-[#18E7FF]'
              : 'text-[#8A8A97] border-transparent hover:text-[#F4F4F7]'
          }`}
        >
          Unread
        </button>
      </div>

      {/* Notification List Panel */}
      <div className="flex-1 overflow-y-auto divide-y divide-[#8A8A97]/5 custom-scrollbar min-h-[250px] max-h-[350px]">
        {loading && notifications.length === 0 ? (
          <div className="p-8 text-center text-xs text-[#8A8A97] flex flex-col items-center justify-center gap-3">
            {/* Scanline loading placeholder */}
            <div className="w-8 h-8 rounded-full border-2 border-t-[#FF2E8A] border-r-transparent border-b-[#18E7FF] border-l-transparent animate-spin"></div>
            <span>Loading feed...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-xs text-[#FF2E8A]">
            <p>Error: {error}</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#8A8A97] flex flex-col items-center justify-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-[#8A8A97]/40 w-10 h-10 mb-1"
            >
              <path d="M22 12h-6l-3 9L9 3l-3 9H2" />
            </svg>
            <p>No notifications here</p>
          </div>
        ) : (
          notifications.map((notif) => (
            <div
              key={notif._id}
              className={`p-4 flex gap-3 hover:bg-[#16161C]/80 transition-all duration-300 relative group cursor-pointer ${
                !notif.is_read ? 'bg-[#9B5CFF]/5 border-l-2 border-l-[#9B5CFF]' : 'border-l-2 border-l-transparent'
              }`}
              onClick={() => !notif.is_read && markAsRead(notif._id)}
            >
              {/* Notification Status Indicator */}
              <div className="flex-shrink-0 mt-1">
                {!notif.is_read ? (
                  <span className="flex h-2.5 w-2.5 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#9B5CFF] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#9B5CFF]"></span>
                  </span>
                ) : (
                  <span className="w-2.5 h-2.5 rounded-full border border-[#8A8A97]/30 block"></span>
                )}
              </div>

              {/* Message Details */}
              <div className="flex-1 min-w-0">
                <p className={`text-xs leading-relaxed ${!notif.is_read ? 'text-[#F4F4F7] font-medium' : 'text-[#8A8A97]'}`}>
                  {notif.message}
                </p>
                <div className="flex items-center gap-2 mt-1.5 text-[10px] text-[#8A8A97]/75">
                  {notif.order_id && (
                    <span className="bg-[#16161C] border border-[#8A8A97]/15 px-1.5 py-0.5 rounded text-[#18E7FF] font-mono">
                      {notif.order_id}
                    </span>
                  )}
                  <span>{formatTime(notif.created_at)}</span>
                </div>
              </div>

              {/* Individual Mark Read Hover Action */}
              {!notif.is_read && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    markAsRead(notif._id);
                  }}
                  className="opacity-0 group-hover:opacity-100 absolute right-3 top-3 p-1 rounded hover:bg-[#0B0B0F] text-[#18E7FF] transition-all duration-200 focus:outline-none"
                  title="Mark as read"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="p-3 border-t border-[#8A8A97]/10 bg-[#0B0B0F]/30 flex items-center justify-between text-xs">
          <span className="text-[#8A8A97]">
            Page <strong className="text-[#F4F4F7] font-semibold">{page}</strong> of {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="px-2.5 py-1 bg-[#16161C] text-[#F4F4F7] border border-[#8A8A97]/15 rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#0B0B0F] transition-all duration-200"
            >
              Prev
            </button>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              className="px-2.5 py-1 bg-[#16161C] text-[#F4F4F7] border border-[#8A8A97]/15 rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#0B0B0F] transition-all duration-200"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
