import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NotificationsProvider } from '../hooks/useNotifications';
import TelegramLinkSettings from '../components/notifications/TelegramLinkSettings';

// Mock the fetch API globally
global.fetch = vi.fn();

describe('TelegramLinkSettings Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('galxy_token', 'test-token-jwt');
  });

  it('renders instructions initially and links chat ID, showing verification code', async () => {
    // 1. Mock status GET call -> returns unlinked
    fetch.mockResolvedValueOnce({
      json: async () => ({
        success: true,
        data: null,
        unread_count: 0
      })
    });

    render(
      <NotificationsProvider>
        <TelegramLinkSettings />
      </NotificationsProvider>
    );

    // Verify instructions and link form are present
    expect(await screen.findByText('SETUP INSTRUCTIONS')).toBeInTheDocument();
    const input = screen.getByLabelText('Telegram Chat ID');
    const button = screen.getByRole('button', { name: 'Link Telegram' });
    expect(input).toBeInTheDocument();
    expect(button).toBeInTheDocument();

    // 2. Perform Link
    fireEvent.change(input, { target: { value: '987654321' } });
    
    // Mock POST link response -> returns code 482910
    fetch.mockResolvedValueOnce({
      json: async () => ({
        success: true,
        data: {
          chat_id: '987654321',
          is_active: false,
          is_verified: false,
          verification_code: '482910'
        },
        unread_count: 0
      })
    });

    fireEvent.click(button);

    // Should transition to pending verification state and display instructions, but NOT the code
    expect(await screen.findByText('Status: PENDING VERIFICATION')).toBeInTheDocument();
    expect(screen.queryByText('482910')).not.toBeInTheDocument();
  });

  it('submits verification code successfully and marks integration active', async () => {
    // Mock initial status GET call -> returns pending verification code '482910'
    fetch.mockResolvedValueOnce({
      json: async () => ({
        success: true,
        data: {
          chat_id: '987654321',
          is_active: false,
          is_verified: false,
          verification_code: '482910'
        },
        unread_count: 0
      })
    });

    render(
      <NotificationsProvider>
        <TelegramLinkSettings />
      </NotificationsProvider>
    );

    // Enter verification code
    const codeInput = await screen.findByPlaceholderText('Enter 6-digit code');
    const verifyButton = screen.getByRole('button', { name: 'Verify Ownership' });
    expect(codeInput).toBeInTheDocument();
    expect(verifyButton).toBeInTheDocument();

    fireEvent.change(codeInput, { target: { value: '482910' } });

    // Mock POST verify response -> returns success verified status
    fetch.mockResolvedValueOnce({
      json: async () => ({
        success: true,
        data: {
          chat_id: '987654321',
          is_active: true,
          is_verified: true
        },
        unread_count: 0
      })
    });

    fireEvent.click(verifyButton);

    // Should transition to Active & Verified state
    expect(await screen.findByText('Status: ACTIVE & VERIFIED')).toBeInTheDocument();
  });
});
