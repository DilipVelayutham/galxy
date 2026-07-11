export type OrderStatus =
  | 'received'
  | 'reviewed'
  | 'quote_sent'
  | 'confirmed'
  | 'in_production'
  | 'ready'
  | 'out_for_delivery'
  | 'delivered'
  | 'cancelled';

export interface Customer {
  name: string;
  email: string;
  phone: string;
}

export interface ShippingAddress {
  street: string;
  city: string;
  state: string;
  zip: string;
  country: string;
}

export interface OrderItem {
  id: string;
  name: string;
  quantity: number;
  price: number;
}

export interface StatusHistoryItem {
  status: OrderStatus;
  changed_at: string;
  changed_by: string;
  note: string;
}

export interface Order {
  id: string;
  order_number: string;
  customer: Customer;
  shipping_address: ShippingAddress;
  items: OrderItem[];
  estimated_total: number;
  final_quoted_price: number | null;
  status: OrderStatus;
  status_history: StatusHistoryItem[];
  admin_notes: string;
  customer_visible_note: string;
  created_at: string;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface OrdersResponse {
  orders: Order[];
  pagination: PaginationMeta;
}

export const STATUS_LIFECYCLE_ORDER: OrderStatus[] = [
  'received',
  'reviewed',
  'quote_sent',
  'confirmed',
  'in_production',
  'ready',
  'out_for_delivery',
  'delivered'
];

export interface GetOrdersParams {
  page?: number;
  limit?: number;
  status?: OrderStatus | 'all';
  search?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

