"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useCart } from "@/lib/cart-context";
import { OrdersAPI } from "@/lib/api";
import AddressSelector from "@/components/AddressSelector";
import CheckoutSummary from "@/components/CheckoutSummary";
import { CreditCard, ArrowRight, ShoppingBag, AlertCircle, ShoppingCart } from "lucide-react";
import Link from "next/link";

interface ValidationError {
  item: string;
  reason: string;
}

export default function CheckoutPage() {
  const router = useRouter();
  const { items, summary, clearCart } = useCart();
  const [selectedAddressId, setSelectedAddressId] = useState<string | null>(null);
  const [placingOrder, setPlacingOrder] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([]);
  const [generalError, setGeneralError] = useState<string | null>(null);

  const handlePlaceOrder = async () => {
    if (!selectedAddressId) {
      setGeneralError("Please select a delivery address.");
      return;
    }

    setGeneralError(null);
    setValidationErrors([]);
    setPlacingOrder(true);

    try {
      // Call POST /api/orders/checkout
      const response = await OrdersAPI.checkout(selectedAddressId, items, summary);
      
      // On success, clear cart and redirect to detailed order page
      clearCart();
      router.push(`/account/orders/${response.order_number}`);
    } catch (err: any) {
      // Handle API validation errors (400)
      if (err.response && err.response.status === 400 && err.response.data) {
        const errorData = err.response.data;
        if (errorData.errors && Array.isArray(errorData.errors)) {
          setValidationErrors(errorData.errors);
        } else {
          setGeneralError(errorData.message || "A validation error occurred. Please verify your items.");
        }
      } else {
        setGeneralError("An unexpected error occurred while placing your order. Please try again.");
      }
    } finally {
      setPlacingOrder(false);
    }
  };

  const isCartEmpty = items.length === 0;

  return (
    <div className="space-y-6 pb-12 relative text-left">
      {/* Loading Overlay */}
      {placingOrder && (
        <div className="fixed inset-0 z-50 bg-[#090d16]/70 backdrop-blur-md flex flex-col items-center justify-center space-y-4">
          <div className="relative flex items-center justify-center">
            <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-indigo-500 animate-spin" />
            <div className="absolute h-10 w-10 rounded-full border-r-2 border-l-2 border-purple-500 animate-spin animate-reverse" />
          </div>
          <div className="text-center space-y-1">
            <p className="text-white font-extrabold text-sm uppercase tracking-wider">Processing Checkout</p>
            <p className="text-xs text-slate-400">Verifying inventory and securing your items...</p>
          </div>
        </div>
      )}

      {/* Header Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-wide">Secure Checkout</h1>
          <p className="text-xs text-slate-400 mt-1">Review your selections, select an address, and finalize your purchase.</p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-400 font-semibold self-start sm:self-center bg-white/5 border border-white/5 px-3 py-1.5 rounded-lg select-none">
          <span>Cart Summary</span>
          <ArrowRight className="h-3 w-3 text-slate-500" />
          <span className="text-indigo-400">Checkout Details</span>
        </div>
      </div>

      {/* Error Displays */}
      {generalError && (
        <div className="glass-panel border-red-500/20 bg-red-500/5 p-4 rounded-2xl flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
          <div className="text-xs text-red-200 font-medium">{generalError}</div>
        </div>
      )}

      {validationErrors.length > 0 && (
        <div className="glass-panel border-red-500/20 bg-red-500/5 p-5 rounded-2xl space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-red-400">
            <AlertCircle className="h-5 w-5" />
            <span>Validation Failed: Out of Stock / Configuration Conflict</span>
          </div>
          <div className="divide-y divide-red-500/10">
            {validationErrors.map((err, index) => (
              <div key={index} className="py-2.5 first:pt-0 last:pb-0 text-xs">
                <span className="font-extrabold text-red-300 block mb-0.5">{err.item}</span>
                <span className="text-slate-300 font-medium leading-relaxed">{err.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty Cart Notice */}
      {isCartEmpty ? (
        <div className="glass-panel p-12 rounded-3xl border border-white/5 text-center max-w-xl mx-auto flex flex-col items-center justify-center space-y-6">
          <div className="h-16 w-16 rounded-full bg-white/5 flex items-center justify-center text-slate-400">
            <ShoppingCart className="h-8 w-8" />
          </div>
          <div className="space-y-2">
            <h3 className="text-lg font-bold text-white">Your Shopping Cart is Empty</h3>
            <p className="text-xs text-slate-400 leading-relaxed max-w-xs mx-auto">
              You must have items in your shopping cart before you can access the checkout portal.
            </p>
          </div>
          <Link
            href="/account/orders"
            className="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition-all shadow-md shadow-indigo-600/10"
          >
            Go to My Orders
          </Link>
        </div>
      ) : (
        /* Checkout Split Layout */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Address Selection */}
          <div className="lg:col-span-7 space-y-6">
            <div className="glass-panel p-6 rounded-3xl border border-white/5">
              <AddressSelector
                selectedAddressId={selectedAddressId}
                onSelect={(id) => {
                  setSelectedAddressId(id);
                  if (generalError) setGeneralError(null);
                }}
              />
            </div>
            
            {/* Payment Method (Read-only simulation) */}
            <div className="glass-panel p-6 rounded-3xl border border-white/5 space-y-4">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <CreditCard className="h-4.5 w-4.5 text-indigo-400" />
                <span>Payment Method</span>
              </h2>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="h-9 w-12 rounded-lg bg-slate-900 border border-white/10 flex items-center justify-center text-[10px] font-extrabold text-slate-400 italic">
                    CARD
                  </div>
                  <div>
                    <span className="block text-xs font-bold text-slate-200">Alex Mercer (Visa •••• 9821)</span>
                    <span className="block text-[10px] text-slate-500 font-medium">Expires 12/28 • Secure Tokenized</span>
                  </div>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400 border border-indigo-500/20">
                  Pre-Authorized
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: Checkout Summary & Place Order */}
          <div className="lg:col-span-5 space-y-6">
            <CheckoutSummary validationErrors={validationErrors} />

            <button
              onClick={handlePlaceOrder}
              disabled={placingOrder}
              className="w-full py-4 rounded-2xl text-sm font-extrabold text-white bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 hover:opacity-95 active:scale-[0.99] transition-all shadow-xl shadow-indigo-600/10 flex items-center justify-center gap-2"
            >
              <ShoppingBag className="h-5 w-5" />
              <span>Place Secure Order</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
