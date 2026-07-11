import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NotificationsProvider } from '../hooks/useNotifications';
import NotificationBell from '../components/notifications/NotificationBell';

// Mock the fetch API globally
global.fetch = vi.fn();

describe('NotificationBell Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('galxy_token', 'test-token-jwt');
  });

  it('renders the bell icon and displays the correct unread badge count', async () => {
    // Mock response containing 3 unread alerts
    fetch.mockResolvedValue({
      json: async () => ({
        success: true,
        data: [],
        unread_count: 3,
        telegram_linked: false
      })
    });

    render(
      <NotificationsProvider>
        <NotificationBell />
      </NotificationsProvider>
    );

    // Expect unread badge count '3' to appear on screen
    const badge = await screen.findByText('3');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-[#FF2E8A]'); // pink neon badge class
  });

  it('toggles the dropdown visibility when clicked', async () => {
    fetch.mockResolvedValue({
      json: async () => ({
        success: true,
        data: [
          { _id: 'notif_1', message: 'Your design is review ready', is_read: false, created_at: new Date().toISOString() }
        ],
        unread_count: 1,
        telegram_linked: false
      })
    });

    render(
      <NotificationsProvider>
        <NotificationBell />
      </NotificationsProvider>
    );

    // Find the bell button container and click it
    const button = await screen.findByRole('button');
    fireEvent.click(button);

    // Dropdown panel should now be in the DOM
    const dropdown = await screen.findByText('Your design is review ready');
    expect(dropdown).toBeInTheDocument();
    
    // Click again to close
    fireEvent.click(button);
    await waitFor(() => {
      expect(screen.queryByText('Your design is review ready')).not.toBeInTheDocument();
    });
  });
});
