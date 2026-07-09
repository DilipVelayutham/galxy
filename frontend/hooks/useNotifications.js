import React, { createContext, useContext, useState, useCallback } from 'react';
import { API_BASE_URL } from '../src/config';

const NotificationsContext = createContext(null);

export function NotificationsProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [limit, setLimit] = useState(10);
  const [isReadFilter, setIsReadFilter] = useState(null); // null = all, true = read, false = unread
  const [telegramStatus, setTelegramStatus] = useState(null);

  // Helper to get auth headers from localstorage
  const getHeaders = useCallback(() => {
    const token = localStorage.getItem('galxy_token');
    if (!token) return {};
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  }, []);

  // Fetch Notifications
  const fetchNotifications = useCallback(async (targetPage = 1, filter = isReadFilter) => {
    const headers = getHeaders();
    if (!headers.Authorization) {
      setError("No authentication token found.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      let url = `${API_BASE_URL}/api/v1/notifications?page=${targetPage}&limit=${limit}`;
      if (filter !== null) {
        url += `&is_read=${filter}`;
      }
      
      const response = await fetch(url, {
        headers
      });
      const resData = await response.json();
      
      if (resData.success) {
        setNotifications(resData.data);
        setUnreadCount(resData.unread_count);
        setPage(resData.page);
        setTotalPages(resData.totalPages);
        setTotal(resData.total);
        setLimit(resData.limit);
        
        // Update local Telegram status cache if returned in route payload
        if (resData.telegram_linked !== undefined) {
          setTelegramStatus(prev => ({
            ...prev,
            linked: resData.telegram_linked,
            chatId: resData.telegram_chat_id,
            isActive: resData.telegram_linked,
            isVerified: resData.telegram_linked
          }));
        }
      } else {
        setError(resData.message || 'Failed to fetch notifications');
      }
    } catch (err) {
      setError(err.message || 'Network error fetching notifications');
    } finally {
      setLoading(false);
    }
  }, [getHeaders, limit, isReadFilter]);

  // Mark single notification as read
  const markAsRead = useCallback(async (id) => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/${id}/read`, {
        method: 'PUT',
        headers: getHeaders()
      });
      const resData = await response.json();
      
      if (resData.success) {
        setNotifications(prev => 
          prev.map(n => n._id === id ? { ...n, is_read: true } : n)
        );
        setUnreadCount(resData.unread_count !== undefined ? resData.unread_count : Math.max(0, unreadCount - 1));
        return true;
      } else {
        setError(resData.message || 'Failed to mark notification as read');
        return false;
      }
    } catch (err) {
      setError(err.message || 'Network error marking notification read');
      return false;
    }
  }, [getHeaders, unreadCount]);

  // Mark all notifications as read
  const markAllAsRead = useCallback(async () => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/read-all`, {
        method: 'PUT',
        headers: getHeaders()
      });
      const resData = await response.json();
      
      if (resData.success) {
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        setUnreadCount(0);
        return true;
      } else {
        setError(resData.message || 'Failed to mark all as read');
        return false;
      }
    } catch (err) {
      setError(err.message || 'Network error marking all read');
      return false;
    }
  }, [getHeaders]);

  // Fetch Telegram Link Status
  const fetchTelegramStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/telegram/status`, {
        headers: getHeaders()
      });
      const resData = await response.json();
      if (resData.success) {
        if (resData.data) {
          setTelegramStatus({
            linked: resData.data.linked,
            chatId: resData.data.chat_id,
            isActive: resData.data.is_active,
            isVerified: resData.data.is_verified,
            verificationCode: resData.data.verification_code
          });
        } else {
          setTelegramStatus({
            linked: false,
            chatId: null,
            isActive: false,
            isVerified: false,
            verificationCode: null
          });
        }
      }
    } catch (err) {
      console.error('Error fetching Telegram status:', err);
    }
  }, [getHeaders]);

  // Link Telegram Chat ID
  const linkTelegram = useCallback(async (chatId) => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/telegram/link`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ chat_id: chatId })
      });
      const resData = await response.json();
      
      if (resData.success) {
        setTelegramStatus({
          linked: resData.data.is_verified,
          chatId: resData.data.chat_id,
          isActive: resData.data.is_active,
          isVerified: resData.data.is_verified,
          verificationCode: resData.data.verification_code
        });
        return true;
      } else {
        setError(resData.message || 'Failed to link Telegram');
        return false;
      }
    } catch (err) {
      setError(err.message || 'Network error linking Telegram');
      return false;
    }
  }, [getHeaders]);

  // Verify Telegram Code (Handshake validation)
  const verifyTelegram = useCallback(async (code) => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/telegram/verify`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ verification_code: code })
      });
      const resData = await response.json();
      
      if (resData.success) {
        setTelegramStatus({
          linked: true,
          chatId: resData.data.chat_id,
          isActive: true,
          isVerified: true,
          verificationCode: null
        });
        return true;
      } else {
        setError(resData.message || 'Failed to verify Telegram code');
        return false;
      }
    } catch (err) {
      setError(err.message || 'Network error verifying Telegram');
      return false;
    }
  }, [getHeaders]);

  // Unlink Telegram
  const unlinkTelegram = useCallback(async () => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/telegram/link`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      const resData = await response.json();
      
      if (resData.success) {
        setTelegramStatus({
          linked: false,
          chatId: null,
          isActive: false,
          isVerified: false,
          verificationCode: null
        });
        return true;
      } else {
        setError(resData.message || 'Failed to unlink Telegram');
        return false;
      }
    } catch (err) {
      setError(err.message || 'Network error unlinking Telegram');
      return false;
    }
  }, [getHeaders]);

  const value = {
    notifications,
    unreadCount,
    loading,
    error,
    page,
    totalPages,
    total,
    limit,
    isReadFilter,
    telegramStatus,
    setIsReadFilter,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    fetchTelegramStatus,
    linkTelegram,
    verifyTelegram,
    unlinkTelegram
  };

  return React.createElement(
    NotificationsContext.Provider,
    { value: value },
    children
  );
}

export default function useNotifications() {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationsProvider');
  }
  return context;
}
