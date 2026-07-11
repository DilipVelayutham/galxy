'use client';

import React, { useState, useEffect, useRef, use, useCallback } from 'react';
import Link from 'next/link';
import { adminOrderService } from '@/lib/api';
import { Order, OrderStatus } from '@/types/admin';
import { AdminStatusUpdateForm } from '@/components/admin/AdminStatusUpdateForm';
import { getStatusBadgeStyle, formatStatusLabel } from '@/utils/status';
import { formatCurrency, getCurrencySymbol } from '@/utils/currency';
import { formatDate } from '@/utils/date';
import { getErrorMessage } from '@/utils/error';
import { useDebouncedCallback } from '@/hooks/useDebouncedCallback';
import { ArrowLeft, Check, AlertCircle, DollarSign, Save, Loader2, User, ClipboardList, MapPin } from 'lucide-react';
interface OrderDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function OrderDetailPage({ params }: OrderDetailPageProps) {
  const { id } = use(params);

  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Status Form state
  const [isStatusSubmitting, setIsStatusSubmitting] = useState(false);
  const [statusError, setStatusError] = useState<string | null>(null);

  // Quote state
  const [quoteInput, setQuoteInput] = useState<string>('');
  const [isQuoteSaving, setIsQuoteSaving] = useState(false);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  const [quoteSaveStatus, setQuoteSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  // Notes state
  const [notesInput, setNotesInput] = useState('');
  const [notesSaveStatus, setNotesSaveStatus] = useState<'saved' | 'unsaved' | 'saving' | 'error'>('saved');
  const [notesError, setNotesError] = useState<string | null>(null);
  
  // Abort controller ref to cancel concurrent autosave requests
  const notesAbortControllerRef = useRef<AbortController | null>(null);

  // Fetch single order details
  const fetchOrderDetails = useCallback(async (showLoader = true) => {
    if (showLoader) setIsLoading(true);
    setError(null);
    try {
      const data = await adminOrderService.getOrderById(id);
      setOrder(data);
      setNotesInput(data.admin_notes || '');
      setQuoteInput(data.final_quoted_price !== null ? data.final_quoted_price.toString() : '');
      setNotesSaveStatus('saved');
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    } finally {
      if (showLoader) setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchOrderDetails();
    // Cleanup any pending saves on unmount
    return () => {
      if (notesAbortControllerRef.current) {
        notesAbortControllerRef.current.abort();
      }
    };
  }, [id, fetchOrderDetails]);

  // Handle status update form submissions
  const handleStatusUpdate = async (payload: {
    status: OrderStatus;
    note?: string;
    customer_visible_note?: string;
  }) => {
    setIsStatusSubmitting(true);
    setStatusError(null);
    try {
      const updated = await adminOrderService.updateOrderStatus(id, payload);
      setOrder(updated);
      // Success refetch to get updated logs
      await fetchOrderDetails(false);
    } catch (err: unknown) {
      const errMsg = getErrorMessage(err);
      setStatusError(errMsg);
      throw err;
    } finally {
      setIsStatusSubmitting(false);
    }
  };

  // Handle Quote update
  const handleQuoteSave = async () => {
    setIsQuoteSaving(true);
    setQuoteError(null);
    setQuoteSaveStatus('saving');
    try {
      const price = quoteInput.trim() === '' ? null : parseFloat(quoteInput);
      if (price !== null && (isNaN(price) || price < 0)) {
        throw new Error('Quote must be a valid, non-negative decimal number');
      }

      const updated = await adminOrderService.updateOrderQuote(id, price);
      setOrder(updated);
      setQuoteSaveStatus('saved');
      setTimeout(() => setQuoteSaveStatus('idle'), 3000);
    } catch (err: unknown) {
      const errMsg = getErrorMessage(err);
      setQuoteError(errMsg);
      setQuoteSaveStatus('error');
    } finally {
      setIsQuoteSaving(false);
    }
  };

  // Save notes directly (cancels any pending/in-flight autosaves)
  const saveNotesDirectly = useCallback(async (content: string) => {
    if (notesAbortControllerRef.current) {
      notesAbortControllerRef.current.abort();
    }
    const controller = new AbortController();
    notesAbortControllerRef.current = controller;

    setNotesSaveStatus('saving');
    setNotesError(null);
    try {
      const updated = await adminOrderService.updateOrderNotes(id, content, { signal: controller.signal });
      setOrder(updated);
      setNotesSaveStatus('saved');
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'CanceledError') {
        return; // Ignore abort errors
      }
      const errMsg = getErrorMessage(err);
      setNotesError(errMsg);
      setNotesSaveStatus('error');
    } finally {
      if (notesAbortControllerRef.current === controller) {
        notesAbortControllerRef.current = null;
      }
    }
  }, [id]);

  // Hook Optimization: Debounce notes saving
  const debouncedSaveNotes = useDebouncedCallback((content: string) => {
    saveNotesDirectly(content);
  }, 1500);

  // Handle Notes keydown / change with Autosave
  const handleNotesChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setNotesInput(value);
    setNotesSaveStatus('unsaved');
    debouncedSaveNotes(value);
  };

  // Save notes on textarea Blur (autosave fallback)
  const handleNotesBlur = () => {
    if (notesSaveStatus === 'unsaved') {
      debouncedSaveNotes.cancel();
      saveNotesDirectly(notesInput);
    }
  };

  if (isLoading) {
    return (
      <div className="w-full flex flex-col items-center justify-center py-24 gap-3 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="text-sm font-medium">Loading order details...</span>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="space-y-4">
        <Link
          href="/admin/orders"
          className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Order List</span>
        </Link>
        <div className="bg-rose-950/20 border border-rose-900/50 p-4 rounded-lg text-rose-400 text-xs" role="alert">
          <p className="font-semibold uppercase tracking-wider">Error Details</p>
          <p className="mt-1 leading-relaxed">{error || 'Order could not be loaded.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Detail Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex flex-col gap-1.5">
          <Link
            href="/admin/orders"
            className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200"
          >
            <ArrowLeft className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Back to Orders</span>
          </Link>
          <div className="flex items-center gap-3 mt-1">
            <h1 className="text-xl font-bold font-mono text-slate-100 uppercase tracking-wide">
              {order.order_number}
            </h1>
            <span className={`inline-flex px-2.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${getStatusBadgeStyle(order.status)}`}>
              {formatStatusLabel(order.status)}
            </span>
          </div>
        </div>
        <div className="text-xs text-slate-500 font-mono">
          Created: <span className="text-slate-300 font-semibold">{formatDate(order.created_at)}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT COLUMN: Customer Info, Shipping Address, Items Table, Quote Editor */}
        <div className="lg:col-span-2 space-y-6">
          {/* Section: Customer & Address */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Customer Details Card */}
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg text-xs space-y-3">
              <div className="flex items-center gap-1.5 border-b border-slate-900 pb-2 text-slate-400 font-semibold uppercase tracking-wider">
                <User className="w-4 h-4 text-blue-400" aria-hidden="true" />
                <span>Customer Information</span>
              </div>
              <div className="space-y-2">
                <div className="grid grid-cols-3">
                  <span className="text-slate-500">Name</span>
                  <span className="col-span-2 text-slate-300 font-medium">{order.customer.name}</span>
                </div>
                <div className="grid grid-cols-3">
                  <span className="text-slate-500">Email</span>
                  <span className="col-span-2 text-slate-300 font-medium truncate select-all">{order.customer.email}</span>
                </div>
                <div className="grid grid-cols-3">
                  <span className="text-slate-500">Phone</span>
                  <span className="col-span-2 text-slate-300 font-mono font-medium select-all">{order.customer.phone}</span>
                </div>
              </div>
            </div>

            {/* Shipping Address Card */}
            <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg text-xs space-y-3">
              <div className="flex items-center gap-1.5 border-b border-slate-900 pb-2 text-slate-400 font-semibold uppercase tracking-wider">
                <MapPin className="w-4 h-4 text-blue-400" aria-hidden="true" />
                <span>Shipping Address</span>
              </div>
              <div className="space-y-1 text-slate-300 leading-relaxed font-medium">
                <div>{order.shipping_address.street}</div>
                <div>
                  {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.zip}
                </div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider mt-1">{order.shipping_address.country}</div>
              </div>
            </div>
          </div>

          {/* Section: Items Table */}
          <div className="bg-slate-950 border border-slate-800 rounded-lg overflow-hidden text-xs">
            <div className="flex items-center gap-1.5 bg-slate-900/60 border-b border-slate-800 py-3 px-4 text-slate-400 font-semibold uppercase tracking-wider">
              <ClipboardList className="w-4 h-4 text-blue-400" aria-hidden="true" />
              <span>Order Items & Estimation</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-slate-900 text-slate-500 uppercase tracking-wider font-semibold text-[10px] text-left">
                    <th className="py-2.5 px-4 font-medium">Item Details</th>
                    <th className="py-2.5 px-4 font-medium text-right w-24">Unit Price</th>
                    <th className="py-2.5 px-4 font-medium text-center w-20">Quantity</th>
                    <th className="py-2.5 px-4 font-medium text-right w-28">Subtotal</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900 font-medium">
                  {order.items.map((item) => (
                    <tr key={item.id} className="text-slate-300">
                      <td className="py-3 px-4">{item.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(item.price)}</td>
                      <td className="py-3 px-4 text-center font-mono text-slate-400">{item.quantity}</td>
                      <td className="py-3 px-4 text-right font-mono text-slate-200">
                        {formatCurrency(item.price * item.quantity)}
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-slate-900/30 font-semibold border-t border-slate-800 text-slate-200">
                    <td colSpan={3} className="py-2.5 px-4 uppercase text-slate-400 tracking-wider">
                      Estimated Total
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-100 text-sm">
                      {formatCurrency(order.estimated_total)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Section: Quote Entry Box */}
          <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg text-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-900 pb-2.5">
              <div className="flex items-center gap-1.5 text-slate-400 font-semibold uppercase tracking-wider">
                <DollarSign className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                <span>Quote Entry</span>
              </div>
              {/* Separate displays */}
              <div className="flex gap-4 font-mono">
                <div className="text-[11px] text-right">
                  <span className="text-slate-500 uppercase text-[10px] block">Estimated Total</span>
                  <span className="text-slate-300 font-semibold text-xs">{formatCurrency(order.estimated_total)}</span>
                </div>
                <div className="text-[11px] text-right border-l border-slate-850 pl-4">
                  <span className="text-slate-500 uppercase text-[10px] block">Final Quoted Price</span>
                  <span className="text-emerald-400 font-semibold text-xs">
                    {order.final_quoted_price !== null ? formatCurrency(order.final_quoted_price) : 'NOT SET'}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-end gap-3 max-w-md">
              <div className="flex-1 w-full">
                <label htmlFor="quote-input" className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                  Set Final Quoted Price ({getCurrencySymbol()})
                </label>
                <div className="relative">
                  <span className="absolute left-2.5 top-2 text-slate-500 font-mono font-medium">{getCurrencySymbol()}</span>
                  <input
                    id="quote-input"
                    type="number"
                    step="0.01"
                    placeholder="Enter final quote..."
                    value={quoteInput}
                    onChange={(e) => {
                      setQuoteInput(e.target.value);
                      setQuoteError(null);
                      setQuoteSaveStatus('idle');
                    }}
                    disabled={isQuoteSaving || order.status === 'delivered'}
                    className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded pl-7 pr-2.5 py-1.5 focus:border-blue-500 focus:outline-none placeholder-slate-600 font-mono font-medium"
                  />
                </div>
              </div>
              <button
                onClick={handleQuoteSave}
                type="button"
                disabled={isQuoteSaving || order.status === 'delivered'}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-4 py-2 font-bold text-slate-200 hover:text-white bg-slate-900 border border-slate-800 hover:border-slate-700 rounded transition-all duration-150 uppercase tracking-wider disabled:opacity-40 disabled:cursor-not-allowed text-[11px]"
              >
                {isQuoteSaving ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Save className="w-3.5 h-3.5" />
                )}
                <span>Save Quote</span>
              </button>
            </div>

            {/* Status notification */}
            {quoteSaveStatus === 'saving' && (
              <span className="text-[10px] text-slate-500 font-mono italic">Saving quote...</span>
            )}
            {quoteSaveStatus === 'saved' && (
              <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-semibold uppercase tracking-wider">
                <Check className="w-3 h-3" aria-hidden="true" />
                <span>Saved</span>
              </span>
            )}
            {quoteError && (
              <div className="flex items-center gap-1.5 text-[10.5px] text-rose-400 font-semibold bg-rose-950/20 border border-rose-900/30 p-2 rounded" role="alert">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
                <span>{quoteError}</span>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Admin Notes, Status update Form, Status History */}
        <div className="space-y-6">
          {/* Section: Admin Notes (Autosaving) */}
          <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg text-xs space-y-3">
            <div className="flex items-center justify-between border-b border-slate-900 pb-2">
              <label htmlFor="admin-notes-textarea" className="font-semibold text-slate-400 uppercase tracking-wider cursor-pointer">
                Admin Notes
              </label>
              {/* Saving status indicator */}
              <div className="font-mono text-[10px] select-none">
                {notesSaveStatus === 'saving' && (
                  <span className="text-blue-400 inline-flex items-center gap-1 font-semibold uppercase tracking-wider">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Saving...</span>
                  </span>
                )}
                {notesSaveStatus === 'saved' && (
                  <span className="text-slate-500 font-semibold uppercase tracking-wider">Saved</span>
                )}
                {notesSaveStatus === 'unsaved' && (
                  <span className="text-amber-400 font-semibold uppercase tracking-wider">Unsaved Changes</span>
                )}
                {notesSaveStatus === 'error' && (
                  <span className="text-rose-400 font-semibold uppercase tracking-wider">Save Failed</span>
                )}
              </div>
            </div>

            <textarea
              id="admin-notes-textarea"
              value={notesInput}
              onChange={handleNotesChange}
              onBlur={handleNotesBlur}
              disabled={order.status === 'delivered'}
              placeholder="Write internal notes about this order... (Changes autosave on typing/blur)"
              className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded p-2.5 h-28 placeholder-slate-600 focus:border-blue-500 focus:outline-none resize-none leading-relaxed"
            />
            {notesError && (
              <p className="text-[10px] text-rose-400 font-medium" role="alert">{notesError}</p>
            )}
            <p className="text-[9.5px] text-slate-500 leading-normal">
              Admin Notes are 100% private to admin operations and are replaced completely when updated.
            </p>
          </div>

          {/* Section: Status Update Form */}
          <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg text-xs space-y-3">
            <div className="border-b border-slate-900 pb-2 text-slate-400 font-semibold uppercase tracking-wider">
              Status Actions
            </div>
            <AdminStatusUpdateForm
              currentStatus={order.status}
              initialCustomerVisibleNote={order.customer_visible_note}
              isSubmitting={isStatusSubmitting}
              onUpdate={handleStatusUpdate}
              backendError={statusError}
            />
          </div>

          {/* Section: Status History Timeline */}
          <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg text-xs space-y-3.5">
            <div className="border-b border-slate-900 pb-2 text-slate-400 font-semibold uppercase tracking-wider">
              Status History Log
            </div>
            <div className="relative border-l border-slate-850 pl-4 ml-2 space-y-4">
              {order.status_history.map((log, index) => (
                <div key={index} className="relative space-y-1">
                  {/* Bullet */}
                  <span className="absolute -left-[21px] top-1.5 w-2 h-2 rounded-full border border-slate-700 bg-slate-950"></span>
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold uppercase tracking-wider text-[10px] text-slate-300">
                      {formatStatusLabel(log.status)}
                    </span>
                    <span className="text-[9px] text-slate-500 font-mono">{formatDate(log.changed_at)}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[9px] text-slate-500 font-medium">
                    <User className="w-2.5 h-2.5" />
                    <span>Changed by {log.changed_by}</span>
                  </div>
                  {log.note && (
                    <p className="text-[10px] text-slate-400 italic bg-slate-900/40 p-2 border border-slate-900/60 rounded mt-1.5 leading-relaxed">
                      {log.note}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

