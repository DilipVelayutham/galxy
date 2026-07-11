import React from 'react';
import { render, screen } from '@testing-library/react';
import StatCard from '../components/admin/StatCard';

describe('StatCard', () => {
  it('renders title and value', () => {
    render(<StatCard title="Total Orders" value={150} />);
    expect(screen.getByText('Total Orders')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
  });

  it('shows ESTIMATE badge only when isEstimate is true', () => {
    const { rerender } = render(<StatCard title="Revenue" value={45000} />);
    expect(screen.queryByText('ESTIMATE')).not.toBeInTheDocument();

    rerender(<StatCard title="Revenue" value={45000} isEstimate={true} />);
    expect(screen.getByText('ESTIMATE')).toBeInTheDocument();
  });

  it('renders left accent stripe only when accentColor is passed', () => {
    const { container, rerender } = render(<StatCard title="Orders" value={150} />);
    // Since there's no reliable text for the stripe, we'll check the DOM structure for a div with the absolute positioning class
    // The stripe has 'absolute left-0 top-0 bottom-0 w-1' class
    expect(container.querySelector('.absolute.left-0')).not.toBeInTheDocument();

    rerender(<StatCard title="Orders" value={150} accentColor="#FFD84D" />);
    const stripe = container.querySelector('.absolute.left-0');
    expect(stripe).toBeInTheDocument();
    expect(stripe).toHaveStyle({ backgroundColor: '#FFD84D' });
  });

  it('wraps in a Link only when href is passed', () => {
    const { container, rerender } = render(<StatCard title="Orders" value={150} />);
    // It should render a plain div card, not wrapped in an <a> tag
    expect(container.querySelector('a')).not.toBeInTheDocument();

    rerender(<StatCard title="Orders" value={150} href="/admin/orders?status=received,reviewed" />);
    const link = container.querySelector('a');
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/admin/orders?status=received,reviewed');
  });
});
