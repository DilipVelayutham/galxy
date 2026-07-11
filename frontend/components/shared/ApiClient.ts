export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export class ApiClient {
  static async getDashboardStats(dateFrom?: string, dateTo?: string) {
    const query = [];
    if (dateFrom) query.push(`date_from=${encodeURIComponent(dateFrom)}`);
    if (dateTo) query.push(`date_to=${encodeURIComponent(dateTo)}`);

    const queryString = query.join('&');
    const url = `${API_BASE_URL}/api/admin/dashboard/stats${queryString ? '?' + queryString : ''}`;
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    const response = await fetch(url, {
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    });
    if (!response.ok) {
      throw new Error(`UNAUTHORIZED`);
    }
    const data = await response.json();
    if (!data.success) {
      throw new Error(data.message || 'Error fetching stats');
    }
    return data.data;
  }
}
