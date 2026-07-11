// lib/api.ts
import { ApiResponse, PaginatedResponse } from '@/types/api';
import { Order, GetOrdersParams, OrdersResponse, OrderStatus } from '@/types/admin';

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, '') || '';

export async function apiRequest<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  path: string,
  body?: unknown,
  query?: Record<string, string | number | boolean>
): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);
  if (query) {
    Object.entries(query).forEach(([k, v]) => url.searchParams.set(k, String(v)));
  }

  const res = await fetch(url.toString(), {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const json = (await res.json()) as ApiResponse<T> | PaginatedResponse<T>;

  if (!('success' in json) || !json.success) {
    const message = ('message' in json && typeof json.message === 'string') ? json.message : 'API error';
    const err = new Error(message) as Error & { response?: unknown };
    err.response = json;
    throw err;
  }
  // For paginated responses we consider the payload to be the array in `data`
  return json.data as T;
}

// Helper to normalize paths by prefixing /api if missing
const normalizePath = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (cleanPath.startsWith('/api/')) {
    return cleanPath;
  }
  return `/api${cleanPath}`;
};

export const api = {
  get: async (path: string, options?: { signal?: AbortSignal }) => {
    const url = `${BASE_URL}${normalizePath(path)}`;
    const res = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: options?.signal,
    });
    return res.json();
  },
  post: async (path: string, body?: unknown, options?: { signal?: AbortSignal }) => {
    const url = `${BASE_URL}${normalizePath(path)}`;
    const res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: options?.signal,
    });
    return res.json();
  },
  put: async (path: string, body?: unknown, options?: { signal?: AbortSignal }) => {
    const url = `${BASE_URL}${normalizePath(path)}`;
    const res = await fetch(url, {
      method: 'PUT',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: options?.signal,
    });
    return res.json();
  },
  delete: async (path: string, options?: { signal?: AbortSignal }) => {
    const url = `${BASE_URL}${normalizePath(path)}`;
    const res = await fetch(url, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: options?.signal,
    });
    return res.json();
  },
  uploadMedia: async (file: File): Promise<any> => {
    const url = `${BASE_URL}/api/admin/media/upload`;
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    });
    return res.json();
  }
};

export interface Address {
  id: string;
  recipient_name: string;
  recipient_phone: string;
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export interface OrderHistoryItem {
  order_number: string;
  status: string;
  created_at: string;
  item_count: number;
  total: number;
  first_item_thumbnail: string | null;
}

export interface OrderAddress {
  recipient_name: string;
  recipient_phone: string;
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface OrderDetailItem {
  id: string;
  product_id: string;
  thumbnail: string;
  name: string;
  quantity: number;
  configuration: Record<string, any>;
  custom_text?: string | null;
  preview_image?: string | null;
  price: number;
}

export interface StatusHistoryEvent {
  status: string;
  title: string;
  description: string;
  timestamp: string;
  completed: boolean;
}

export interface OrderDetail {
  order_number: string;
  status: string;
  created_at: string;
  estimated_total: number;
  final_quoted_price: number | null;
  customer_visible_note?: string;
  status_history: StatusHistoryEvent[];
  items: OrderDetailItem[];
  address: OrderAddress;
  total: number;
  subtotal: number;
  shipping: number;
  tax: number;
}

const mapBackendOrderToFrontend = (o: any): Order => {
  const customerSnapshot = o.customer_snapshot || {};
  return {
    id: o.id || o._id,
    order_number: o.order_number,
    estimated_total: o.estimated_total,
    final_quoted_price: o.final_quoted_price,
    status: o.status,
    status_history: o.status_history || [],
    admin_notes: o.admin_notes || '',
    customer_visible_note: o.customer_visible_note || '',
    created_at: o.created_at,
    customer: {
      name: customerSnapshot.name || 'Anonymous',
      email: customerSnapshot.email || 'no-email@galxy.in',
      phone: customerSnapshot.phone || '000-000-0000',
    },
    shipping_address: {
      street: customerSnapshot.address?.line1 || customerSnapshot.address?.street || 'N/A',
      city: customerSnapshot.address?.city || 'N/A',
      state: customerSnapshot.address?.state || 'N/A',
      zip: customerSnapshot.address?.pincode || customerSnapshot.address?.zip || 'N/A',
      country: customerSnapshot.address?.country || 'India',
    },
    items: (o.items || []).map((item: any) => ({
      id: item.product_id,
      name: item.product_title || 'Custom Item',
      quantity: item.quantity || 1,
      price: item.line_total_estimate || item.unit_price_estimate || 0,
    })),
  };
};

const buildStatusHistoryEvents = (currentStatus: string, history: any[]): StatusHistoryEvent[] => {
  const stages = [
    {
      status: 'pending',
      title: 'Order Placed',
      description: 'Your customization details and order have been received.',
      matches: ['received', 'reviewed', 'quote_sent']
    },
    {
      status: 'confirmed',
      title: 'Order Confirmed',
      description: 'Design validated and deposit confirmed.',
      matches: ['confirmed']
    },
    {
      status: 'processing',
      title: 'In Production',
      description: 'Our craftsmen are hand-making your custom order.',
      matches: ['in_production', 'ready']
    },
    {
      status: 'shipped',
      title: 'Shipped',
      description: 'Order handed over to logistics. Tracking active.',
      matches: ['out_for_delivery']
    },
    {
      status: 'delivered',
      title: 'Delivered',
      description: 'Package successfully delivered to destination.',
      matches: ['delivered']
    }
  ];

  const findTimestamp = (matches: string[]): string | null => {
    const entry = history.find((h: any) => matches.includes(h.status));
    return entry ? entry.timestamp || entry.changed_at : null;
  };

  const statusLower = currentStatus.toLowerCase();
  
  if (statusLower === 'cancelled') {
    const cancelTime = history.find((h: any) => h.status === 'cancelled')?.timestamp || new Date().toISOString();
    return [
      {
        status: 'cancelled',
        title: 'Order Cancelled',
        description: 'This order has been cancelled.',
        timestamp: cancelTime,
        completed: true
      }
    ];
  }

  let activeIndex = -1;
  for (let i = 0; i < stages.length; i++) {
    if (stages[i].matches.includes(statusLower)) {
      activeIndex = i;
      break;
    }
  }
  if (activeIndex === -1) {
    if (statusLower === 'reviewed' || statusLower === 'quote_sent') activeIndex = 0;
    else if (statusLower === 'ready') activeIndex = 2;
  }

  return stages.map((stage, idx) => {
    const completed = idx <= activeIndex || history.some((h: any) => stage.matches.includes(h.status));
    return {
      status: stage.status,
      title: stage.title,
      description: stage.description,
      timestamp: findTimestamp(stage.matches) || '',
      completed,
    };
  });
};

export const OrdersAPI = {
  getOrders: async (): Promise<OrderHistoryItem[]> => {
    const res = await api.get('/orders');
    const ordersArray = Array.isArray(res.data) ? res.data : (Array.isArray(res) ? res : []);
    return ordersArray.map((o: any) => ({
      order_number: o.order_number,
      status: o.status,
      created_at: o.created_at,
      item_count: o.item_count,
      total: o.estimated_total,
      first_item_thumbnail: o.thumbnail_preview || null,
    }));
  },
  getOrderDetails: async (orderNumber: string): Promise<OrderDetail> => {
    const res = await api.get(`/orders/${orderNumber}`);
    const o = res.data || res;
    const customerSnapshot = o.customer_snapshot || {};
    return {
      order_number: o.order_number,
      status: o.status,
      created_at: o.created_at,
      estimated_total: o.estimated_total,
      final_quoted_price: o.final_quoted_price,
      customer_visible_note: o.customer_visible_note || undefined,
      status_history: buildStatusHistoryEvents(o.status, o.status_history || []),
      total: o.final_quoted_price !== null && o.final_quoted_price !== undefined ? o.final_quoted_price : o.estimated_total,
      subtotal: o.final_quoted_price !== null && o.final_quoted_price !== undefined ? o.final_quoted_price : o.estimated_total,
      shipping: 0,
      tax: 0,
      items: (o.items || []).map((item: any) => ({
        id: item.product_id,
        product_id: item.product_id,
        thumbnail: item.ai_preview_image || item.reference_image || '/placeholder-image.png',
        name: item.product_title || 'Custom Item',
        quantity: item.quantity || 1,
        configuration: item.selected_attributes || {},
        custom_text: item.custom_text || null,
        preview_image: item.ai_preview_image || null,
        price: item.unit_price_estimate || item.line_total_estimate || 0,
      })),
      address: {
        recipient_name: customerSnapshot.name || 'Anonymous',
        recipient_phone: customerSnapshot.phone || 'N/A',
        street: customerSnapshot.address?.line1 || customerSnapshot.address?.street || 'N/A',
        city: customerSnapshot.address?.city || 'N/A',
        state: customerSnapshot.address?.state || 'N/A',
        postal_code: customerSnapshot.address?.pincode || customerSnapshot.address?.postal_code || 'N/A',
        country: customerSnapshot.address?.country || 'India',
      }
    };
  }
};

const mapBackendAddressToFrontend = (a: any): Address => {
  const line1 = a.line1 || '';
  let recipient_name = 'Custom Address';
  let recipient_phone = 'N/A';
  let street = line1;

  const match = line1.match(/^(.*?) \((.*?)\) - (.*)$/);
  if (match) {
    recipient_name = match[1];
    recipient_phone = match[2];
    street = match[3];
  }

  return {
    id: a._id || a.id,
    recipient_name,
    recipient_phone,
    street,
    city: a.city || '',
    state: a.state || '',
    postal_code: a.pincode || '',
    country: 'India',
    is_default: a.is_default || false,
  };
};

export const AddressAPI = {
  getAddresses: async (): Promise<Address[]> => {
    const res = await api.get('/user/profile');
    const addresses = res.data?.addresses || res.addresses || [];
    return addresses.map(mapBackendAddressToFrontend);
  },
  addAddress: async (data: any): Promise<Address> => {
    const payload = {
      label: 'Home',
      line1: `${data.recipient_name} (${data.recipient_phone}) - ${data.street}`,
      city: data.city,
      state: data.state,
      pincode: data.postal_code,
      is_default: false,
    };
    const res = await api.post('/user/addresses', payload);
    return mapBackendAddressToFrontend(res.data || res);
  }
};

export const adminOrderService = {
  getOrders: async (params: GetOrdersParams): Promise<OrdersResponse> => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.set('page', String(params.page));
    if (params.limit) queryParams.set('limit', String(params.limit));
    if (params.status && params.status !== 'all') queryParams.set('status', params.status);
    if (params.search) queryParams.set('search', params.search);
    if (params.date_from) queryParams.set('date_from', params.date_from);
    if (params.date_to) queryParams.set('date_to', params.date_to);
    if (params.sort_by) queryParams.set('sort_by', params.sort_by);
    if (params.sort_order) queryParams.set('sort_order', params.sort_order);

    const queryString = queryParams.toString();
    const path = `/admin/orders${queryString ? `?${queryString}` : ''}`;
    const res = await api.get(path);
    const rawOrders = res.data || [];
    return {
      orders: rawOrders.map(mapBackendOrderToFrontend),
      pagination: {
        page: res.page || 1,
        limit: res.limit || 10,
        total: res.total || 0,
        totalPages: res.totalPages || 1,
      }
    };
  },
  getOrderById: async (id: string): Promise<Order> => {
    const res = await api.get(`/admin/orders/${id}`);
    return mapBackendOrderToFrontend(res.data || res);
  },
  updateOrderStatus: async (id: string, payload: { status: OrderStatus; note?: string; customer_visible_note?: string }): Promise<Order> => {
    const res = await api.put(`/admin/orders/${id}/status`, payload);
    return mapBackendOrderToFrontend(res.data || res);
  },
  updateOrderQuote: async (id: string, price: number | null): Promise<Order> => {
    const res = await api.put(`/admin/orders/${id}/quote`, { final_quoted_price: price });
    return mapBackendOrderToFrontend(res.data || res);
  },
  updateOrderNotes: async (id: string, content: string, options?: { signal?: AbortSignal }): Promise<Order> => {
    const res = await api.put(`/admin/orders/${id}/notes`, { admin_notes: content }, options);
    return mapBackendOrderToFrontend(res.data || res);
  }
};
