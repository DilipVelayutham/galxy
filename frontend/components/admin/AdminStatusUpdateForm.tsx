'use client';

import React, { useState, useEffect } from 'react';
import { OrderStatus, STATUS_LIFECYCLE_ORDER } from '@/types/admin';
import { AlertCircle, CheckCircle, RefreshCw, XCircle } from 'lucide-react';
import { formatStatusLabel } from '@/utils/status';

interface AdminStatusUpdateFormProps {
  currentStatus: OrderStatus;
  initialCustomerVisibleNote: string;
  isSubmitting: boolean;
  onUpdate: (payload: {
    status: OrderStatus;
    note?: string;
    customer_visible_note?: string;
  }) => Promise<void>;
  backendError?: string | null;
}

// Static definition outside component scope to optimize rendering performance
const ALL_STATUSES: OrderStatus[] = [
  ...STATUS_LIFECYCLE_ORDER,
  'cancelled',
];

// Helper to determine status type transition
const getTransitionType = (from: OrderStatus, to: OrderStatus) => {
  if (from === to) return 'none';
  if (to === 'cancelled') return 'cancellation';
  if (from === 'cancelled') return 'restore'; // Cancelled to active

  const fromIdx = STATUS_LIFECYCLE_ORDER.indexOf(from);
  const toIdx = STATUS_LIFECYCLE_ORDER.indexOf(to);

  if (toIdx > fromIdx) return 'forward';
  return 'backward';
};

export const AdminStatusUpdateForm: React.FC<AdminStatusUpdateFormProps> = ({
  currentStatus,
  initialCustomerVisibleNote,
  isSubmitting,
  onUpdate,
  backendError,
}) => {
  const [selectedStatus, setSelectedStatus] = useState<OrderStatus>(currentStatus);
  const [note, setNote] = useState('');
  const [customerVisibleNote, setCustomerVisibleNote] = useState(initialCustomerVisibleNote);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [showForwardNote, setShowForwardNote] = useState(false);

  // Sync state if props change
  useEffect(() => {
    setSelectedStatus(currentStatus);
  }, [currentStatus]);

  useEffect(() => {
    setCustomerVisibleNote(initialCustomerVisibleNote);
  }, [initialCustomerVisibleNote]);

  const transitionType = getTransitionType(currentStatus, selectedStatus);
  const isBackward = transitionType === 'backward' || transitionType === 'restore';
  const isCancellation = transitionType === 'cancellation';

  const isNoteRequired = isBackward || isCancellation;
  const isNoteFieldVisible = isNoteRequired || (transitionType === 'forward' && showForwardNote);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (transitionType === 'none') {
      setValidationError('Please select a different status to update.');
      return;
    }

    // Validation rules
    if (isNoteRequired && !note.trim()) {
      setValidationError(
        `An internal explanation note is required for ${
          isCancellation ? 'cancellation' : 'moving the status backward'
        }.`
      );
      return;
    }

    // Trigger confirmation prompt if it's a backward transition or cancellation
    if ((isBackward || isCancellation) && !showConfirmation) {
      setShowConfirmation(true);
      return;
    }

    try {
      await onUpdate({
        status: selectedStatus,
        note: (isNoteFieldVisible && note.trim()) ? note.trim() : undefined,
        customer_visible_note: customerVisibleNote.trim() || undefined,
      });
      // Clear form inputs on success
      setNote('');
      setShowForwardNote(false);
      setShowConfirmation(false);
    } catch {
      // Backend validation errors will be caught and displayed by the parent
    }
  };

  const handleCancelConfirmation = () => {
    setShowConfirmation(false);
    setValidationError(null);
  };

  if (currentStatus === 'delivered') {
    return (
      <div className="border border-emerald-950 bg-emerald-950/20 p-4 rounded text-xs" role="alert">
        <div className="flex items-start gap-2.5">
          <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <h4 className="font-semibold text-emerald-400 uppercase tracking-wide">Order Delivered</h4>
            <p className="text-slate-400 mt-1">
              This order has been delivered and is closed. Status modifications and cancellations are disabled.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 text-xs">
      {/* Dropdown Selector */}
      <div>
        <label htmlFor="status-select" className="block font-medium text-slate-400 mb-1.5 uppercase tracking-wide">
          Update Order Status
        </label>
        <select
          id="status-select"
          value={selectedStatus}
          onChange={(e) => {
            setSelectedStatus(e.target.value as OrderStatus);
            setShowConfirmation(false);
            setValidationError(null);
            setShowForwardNote(false);
            setNote('');
          }}
          disabled={isSubmitting}
          className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded px-2.5 py-1.5 focus:border-blue-500 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {ALL_STATUSES.map((status) => (
            <option key={status} value={status}>
              {formatStatusLabel(status).toUpperCase()} {status === currentStatus ? '(Current)' : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Conditional Warning Alerts */}
      {(isBackward || isCancellation) && (
        <div 
          className={`p-3 border rounded ${isCancellation ? 'bg-rose-950/20 border-rose-900 text-rose-300' : 'bg-amber-950/20 border-amber-900 text-amber-300'}`}
          role="alert"
        >
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true" />
            <div>
              <p className="font-semibold uppercase tracking-wide">
                {isCancellation ? 'Order Cancellation Warning' : 'Backward Status Transition Warning'}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                {isCancellation
                  ? 'You are cancelling this order. An internal reason is required below.'
                  : `You are moving the status backward from "${formatStatusLabel(currentStatus).toUpperCase()}" to "${formatStatusLabel(selectedStatus).toUpperCase()}". An explanation note is required below and a confirmation step will be prompted.`}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Optional Note Toggle for Forward Transitions */}
      {transitionType === 'forward' && !showForwardNote && (
        <div className="flex justify-start">
          <button
            type="button"
            onClick={() => setShowForwardNote(true)}
            className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold uppercase tracking-wider transition-colors focus:outline-none"
          >
            + Add Internal Note (Optional)
          </button>
        </div>
      )}

      {/* Internal Note field (Conditional) */}
      {isNoteFieldVisible && (
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label htmlFor="status-note" className="block font-medium text-slate-400 uppercase tracking-wide">
              Internal Note {isNoteRequired ? <span className="text-rose-400 font-bold">* Required</span> : <span className="text-slate-500 font-normal">(Optional)</span>}
            </label>
            {transitionType === 'forward' && (
              <button
                type="button"
                onClick={() => {
                  setShowForwardNote(false);
                  setNote('');
                }}
                className="text-[10px] text-slate-500 hover:text-slate-400 font-semibold uppercase tracking-wider focus:outline-none"
              >
                Hide Note
              </button>
            )}
          </div>
          <textarea
            id="status-note"
            value={note}
            onChange={(e) => {
              setNote(e.target.value);
              setValidationError(null);
            }}
            disabled={isSubmitting}
            placeholder={
              isNoteRequired
                ? 'Provide explanation/reason for this transition (Mandatory)...'
                : 'Add optional internal note about this transition...'
            }
            className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded px-2.5 py-2 h-20 placeholder-slate-600 focus:border-blue-500 focus:outline-none resize-none"
          />
        </div>
      )}

      {/* Customer Visible Note */}
      <div>
        <label htmlFor="customer-visible-note" className="block font-medium text-slate-400 mb-1.5 uppercase tracking-wide">
          Customer Visible Note <span className="text-slate-500 font-normal">(Optional - Visible in Tracker)</span>
        </label>
        <textarea
          id="customer-visible-note"
          value={customerVisibleNote}
          onChange={(e) => setCustomerVisibleNote(e.target.value)}
          disabled={isSubmitting}
          placeholder="Message visible to the customer on their order tracker..."
          className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded px-2.5 py-2 h-20 placeholder-slate-600 focus:border-blue-500 focus:outline-none resize-none"
        />
      </div>

      {/* Validation or Backend Error Display */}
      {(validationError || backendError) && (
        <div className="flex items-start gap-2 text-rose-400 bg-rose-950/20 border border-rose-900/50 p-2.5 rounded" role="alert">
          <XCircle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true" />
          <span className="leading-relaxed font-medium">{validationError || backendError}</span>
        </div>
      )}

      {/* Confirmation Step Checklist */}
      {showConfirmation && (
        <div className="p-3 border border-blue-900 bg-blue-950/20 text-blue-300 rounded" role="dialog" aria-labelledby="confirmation-title">
          <p id="confirmation-title" className="font-semibold uppercase tracking-wide mb-2">Confirmation Required</p>
          <p className="text-[11px] text-slate-400 mb-3">
            Please confirm that you want to force this {isCancellation ? 'cancellation' : 'backward transition'} and verify all details are correct.
          </p>
          <div className="flex flex-col sm:flex-row gap-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-150 uppercase tracking-wider"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <span>Confirm & Save</span>
              )}
            </button>
            <button
              type="button"
              onClick={handleCancelConfirmation}
              disabled={isSubmitting}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 rounded font-semibold uppercase tracking-wider transition-colors duration-150"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Standard Submit Button */}
      {!showConfirmation && (
        <button
          type="submit"
          disabled={isSubmitting || transitionType === 'none'}
          className="w-full flex items-center justify-center gap-1.5 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-200 hover:text-white border border-slate-700 font-bold py-2 px-4 rounded transition-colors duration-150 uppercase tracking-wider disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <span>Update Status</span>
          )}
        </button>
      )}
    </form>
  );
};

