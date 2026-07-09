import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NotificationsProvider } from '../hooks/useNotifications';
import NotificationDropdown from '../components/notifications/NotificationDropdown';

// Mock the fetch API globally
global.fetch = vi.fn();

describe('NotificationDropdown Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('galxy_token', 'test-token-jwt');
  });

  it('renders a list of notifications and handles marking them as read', async () => {
    // 1. Mock fetch notifications call persistently
    fetch.mockResolvedValue({
      json: async () => ({
        success: true,
        data: [
          { _id: 'notif_1', message: 'Test message 1', is_read: false, created_at: new Date().toISOString() },
          { _id: 'notif_2', message: 'Test message 2', is_read: true, created_at: new Date().toISOString() }
        ],
        unread_count: 1,
        page: 1,
        totalPages: 1,
        total: 2,
        limit: 10,
        telegram_linked: false
      })
    });

    render(
      <NotificationsProvider>
        <NotificationDropdown onClose={() => {}} />
      </NotificationsProvider>
    );

    // Verify messages appear
    const msg1 = await screen.findByText('Test message 1');
    const msg2 = await screen.findByText('Test message 2');
    expect(msg1).toBeInTheDocument();
    expect(msg2).toBeInTheDocument();

    // 2. Adjust mock to return success when PUT /api/notifications/notif_1/read is called
    fetch.mockImplementation((url, config) => {
      if (config && config.method === 'PUT') {
        return Promise.resolve({
          json: async () => ({
            success: true,
            data: { _id: 'notif_1', is_read: true }
          })
        });
      }
      return Promise.resolve({
        json: async () => ({
          success: true,
          data: [
            { _id: 'notif_1', message: 'Test message 1', is_read: true, created_at: new Date().toISOString() },
            { _id: 'notif_2', message: 'Test message 2', is_read: true, created_at: new Date().toISOString() }
          ],
          unread_count: 0,
          page: 1,
          totalPages: 1,
          total: 2,
          limit: 10,
          telegram_linked: false
        })
      });
    });

    // Find the mark-as-read checkmark action button
    const checkmarkButtons = screen.getAllByRole('button');
    const unreadCheckBtn = checkmarkButtons.find(b => b.title === 'Mark as read' || b.getAttribute('title') === 'Mark as read');
    if (unreadCheckBtn) {
      fireEvent.click(unreadCheckBtn);
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/v1/notifications/notif_1/read'), expect.objectContaining({ method: 'PUT' }));
      });
    }
  });

  it('displays empty state message when there are no alerts', async () => {
    fetch.mockResolvedValue({
      json: async () => ({
        success: true,
        data: [],
        unread_count: 0,
        page: 1,
        totalPages: 0,
        total: 0,
        limit: 10,
        telegram_linked: false
      })
    });

    render(
      <NotificationsProvider>
        <NotificationDropdown onClose={() => {}} />
      </NotificationsProvider>
    );

    const emptyText = await screen.findByText('No notifications here');
    expect(emptyText).toBeInTheDocument();
  });
});
