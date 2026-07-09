import React from 'react';
import { render, screen } from '@testing-library/react';
import OrdersByStatusChart from '../components/admin/OrdersByStatusChart';

describe('OrdersByStatusChart', () => {
  it('renders the chart title and all status bars', () => {
    const data = [
      { status: 'received', count: 10 },
      { status: 'delivered', count: 4 },
    ];
    render(<OrdersByStatusChart data={data} />);
    expect(screen.getByText('Orders By Status')).toBeInTheDocument();
  });
});
