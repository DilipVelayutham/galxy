"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { useRouter } from "next/navigation";
import { FileText, MapPin, Loader2, ArrowRight } from "lucide-react";
import Link from "next/link";

interface CartItem {
  id: string;
  _id?: string;
  product_id: string;
  selected_attributes: Record<string, any>;
  quantity: number;
  unit_price_estimate: number;
  ai_preview_image: string | null;
  custom_text: string;
}

export default function CheckoutPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  
  // Billing fields
  const [line1, setLine1] = useState("");
  const [line2, setLine2] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [pincode, setPincode] = useState("");

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        showToast("Please login to proceed to checkout", "warning");
        router.push("/login");
        return;
      }
      
      const fetchCheckoutData = async () => {
        try {
          const res = await api.get("/cart");
          if (res.success && res.data) {
            const items = (res.data.items || []).map((item: CartItem) => ({
              ...item,
              id: item._id || item.id
            }));
            setCartItems(items);
            
            // Pre-fill user profile shipping info if present
            const profileRes = await api.get("/auth/session"); // Refresh session user details
            if (profileRes.success && profileRes.data?.user?.shipping_address) {
              const addr = profileRes.data.user.shipping_address;
              setLine1(addr.line1 || "");
              setLine2(addr.line2 || "");
              setCity(addr.city || "");
              setState(addr.state || "");
              setPincode(addr.pincode || "");
            }
          }
        } catch {
          showToast("Error retrieving checkout summary", "error");
        } finally {
          setLoading(false);
        }
      };
      
      fetchCheckoutData();
    }
  }, [isAuthenticated, authLoading, router, showToast]);

  const handleSubmitInquiry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!line1 || !city || !state || !pincode) {
      showToast("Shipping Address details are required", "warning");
      return;
    }

    setSubmitting(true);
    try {
      const res = await api.post("/orders/checkout", {
        shipping_address: {
          line1,
          line2,
          city,
          state,
          pincode
        }
      });

      if (res.success && res.data?.order_number) {
        showToast("Order Inquiry Placed Successfully!", "success");
        // Redirect directly to the order milestone tracker
        router.push(`/account/orders/${res.data.order_number}`);
      } else {
        showToast(res.message || "Failed to submit order inquiry", "error");
      }
    } catch {
      showToast("Network check submission failed", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const getSubtotal = () => {
    return cartItems.reduce((acc, curr) => acc + curr.unit_price_estimate * curr.quantity, 0);
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Compiling final billing parameters...</span>
      </div>
    );
  }

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen bg-void-black text-text-primary p-10 flex flex-col items-center justify-center gap-4">
        <h2 className="text-xl font-bold">No active items for checkout</h2>
        <Link href="/" className="text-neon-blue underline text-xs">Return to Catalog</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="border-b border-panel-charcoal pb-4">
          <h1 className="text-2xl font-black uppercase tracking-tight flex items-center gap-2">
            <FileText className="w-6 h-6 text-neon-blue drop-shadow-[0_0_8px_#18E7FF]" />
            Order Checkout
          </h1>
          <p className="text-xs text-text-muted mt-1">
            Provide shipping information to request your final quote pricing from Asil.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Shipping Form */}
          <form onSubmit={handleSubmitInquiry} className="lg:col-span-7 flex flex-col gap-5">
            <div className="p-6 rounded-2xl bg-panel-charcoal/20 border border-panel-charcoal flex flex-col gap-4">
              <h3 className="text-sm font-bold text-text-primary uppercase flex items-center gap-2 border-b border-panel-charcoal/50 pb-2">
                <MapPin className="w-4 h-4 text-neon-blue" /> Shipping Destination
              </h3>

              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Address Line 1</label>
                <input
                  type="text"
                  value={line1}
                  onChange={(e) => setLine1(e.target.value)}
                  className="p-3 rounded-lg bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                  placeholder="Street address, P.O. box, company name"
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Address Line 2 (Optional)</label>
                <input
                  type="text"
                  value={line2}
                  onChange={(e) => setLine2(e.target.value)}
                  className="p-3 rounded-lg bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                  placeholder="Apartment, suite, unit, building, floor"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">City</label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="p-3 rounded-lg bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                    required
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">State</label>
                  <input
                    type="text"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="p-3 rounded-lg bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                    required
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Pincode</label>
                  <input
                    type="text"
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value)}
                    className="p-3 rounded-lg bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                    required
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="p-4 rounded-xl bg-neon-blue hover:bg-neon-blue/80 text-void-black font-extrabold text-sm tracking-wider glow-blue-hover transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {submitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  PLACE ORDER INQUIRY <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Checkout Items Summary sidebar */}
          <div className="lg:col-span-5 p-6 rounded-2xl bg-panel-charcoal border border-panel-charcoal flex flex-col gap-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary border-b border-panel-charcoal/50 pb-2">
              Item Summary
            </h3>

            <div className="flex flex-col gap-3 max-h-56 overflow-y-auto pr-1">
              {cartItems.map((item) => (
                <div key={item.id} className="flex justify-between items-center text-xs">
                  <div className="min-w-0">
                    <span className="font-bold text-text-primary line-clamp-1">
                      {item.custom_text ? `"${item.custom_text}"` : "Custom Lighting"}
                    </span>
                    <span className="text-[10px] text-text-muted block mt-0.5">Qty: {item.quantity}</span>
                  </div>
                  <span className="font-black text-neon-blue flex-shrink-0 ml-2">
                    ₹{(item.unit_price_estimate * item.quantity).toLocaleString("en-IN")}
                  </span>
                </div>
              ))}
            </div>

            <div className="border-t border-panel-charcoal pt-4 mt-2 flex justify-between items-baseline">
              <span className="text-xs text-text-muted font-bold">Estimated Quote Total</span>
              <span className="text-xl font-black text-neon-blue">
                ₹{getSubtotal().toLocaleString("en-IN")}
              </span>
            </div>

            <p className="text-[9px] text-text-muted leading-relaxed mt-2 italic">
              * The ordering flow acts as a quote validation checklist. No online payments are captured during order submission.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}
