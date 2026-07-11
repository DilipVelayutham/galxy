import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import AdminDashboardPage from '../app/admin/page';
import { ApiClient } from '../components/shared/ApiClient';

jest.mock('../components/shared/ApiClient');

describe('AdminDashboardPage', () => {
  it('renders both charts after fetching data', async () => {
    (ApiClient.getDashboardStats as jest.Mock).mockResolvedValue({
      orders_by_status: [{ status: 'received', count: 10 }],
      top_categories: [{ category_name: 'Lighting', order_count: 5 }],
    });

    render(<AdminDashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Orders By Status')).toBeInTheDocument();
    });
    expect(screen.getByText('Top Categories')).toBeInTheDocument();
  });
});
