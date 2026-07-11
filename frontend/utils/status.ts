import { OrderStatus } from '@/types/admin';

/**
 * Returns Tailwind css classes for a given order status badge.
 */
export const getStatusBadgeStyle = (status: OrderStatus | string): string => {
  switch (status) {
    case 'received':
      return 'bg-slate-900 text-slate-300 border-slate-700 border';
    case 'reviewed':
      return 'bg-blue-950 text-blue-400 border border-blue-800';
    case 'quote_sent':
      return 'bg-amber-950 text-amber-400 border border-amber-800';
    case 'confirmed':
      return 'bg-emerald-950 text-emerald-400 border border-emerald-800';
    case 'in_production':
      return 'bg-indigo-950 text-indigo-400 border border-indigo-800';
    case 'ready':
      return 'bg-teal-950 text-teal-400 border border-teal-800';
    case 'out_for_delivery':
      return 'bg-cyan-950 text-cyan-400 border border-cyan-800';
    case 'delivered':
      return 'bg-green-950 text-green-400 border border-green-800';
    case 'cancelled':
      return 'bg-rose-950 text-rose-400 border border-rose-800';
    default:
      return 'bg-slate-900 text-slate-300 border border-slate-700';
  }
};

/**
 * Returns a human-friendly label for a status code.
 */
export const formatStatusLabel = (status: OrderStatus | string): string => {
  const mapping: Record<string, string> = {
    received: 'Received',
    reviewed: 'Reviewed',
    quote_sent: 'Quote Sent',
    confirmed: 'Confirmed',
    in_production: 'In Production',
    ready: 'Ready',
    out_for_delivery: 'Out for Delivery',
    delivered: 'Delivered',
    cancelled: 'Cancelled',
  };
  return mapping[status] || status.replace(/_/g, ' ');
};
