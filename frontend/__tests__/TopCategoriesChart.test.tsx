import React from 'react';
import { render, screen } from '@testing-library/react';
import TopCategoriesChart from '../components/admin/TopCategoriesChart';

describe('TopCategoriesChart', () => {
  it('renders the chart title with category data', () => {
    const data = [{ category_name: 'Lighting', order_count: 5 }];
    render(<TopCategoriesChart data={data} />);
    expect(screen.getByText('Top Categories')).toBeInTheDocument();
  });

  it('does not crash when data is empty', () => {
    render(<TopCategoriesChart data={[]} />);
    expect(screen.getByText('Top Categories')).toBeInTheDocument();
  });
});
