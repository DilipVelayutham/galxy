'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  role?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  cartCount: number;
  login: (email: string, password?: string) => Promise<{ success: boolean; message?: string }>;
  signup: (name: string, email: string, phone: string, password?: string) => Promise<{ success: boolean; message?: string }>;
  logout: () => void;
  refreshCart: () => Promise<void>;
  triggerToast: (message: string, type: 'success' | 'error' | 'warning') => void;
  toast: { message: string; type: 'success' | 'error' | 'warning' } | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [cartCount, setCartCount] = useState(0);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'warning' } | null>(null);

  const triggerToast = useCallback((message: string, type: 'success' | 'error' | 'warning') => {
    setToast({ message, type });
  }, []);

  // Automatically dismiss toast after 4 seconds
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const refreshCart = useCallback(async () => {
    if (!user) return;
    try {
      const res = await fetch('/api/cart');
      if (res.ok) {
        const result = await res.json();
        if (result.success && result.data) {
          setCartCount(result.data.item_count || 0);
        }
      }
    } catch (err) {
      console.error('Error fetching cart:', err);
    }
  }, [user]);

  // Load user from localStorage on mount (for persistent demo mock state)
  useEffect(() => {
    const savedUser = localStorage.getItem('galxy_user');
    setTimeout(() => {
      if (savedUser) {
        setUser(JSON.parse(savedUser));
      }
      setLoading(false);
    }, 0);
  }, []);

  // Fetch cart count whenever user changes
  useEffect(() => {
    setTimeout(() => {
      if (user) {
        refreshCart();
      } else {
        setCartCount(0);
      }
    }, 0);
  }, [user, refreshCart]);



  const login = async (email: string, password?: string) => {
    const mockUser: User = {
      id: 'usr_mock_123',
      name: email.split('@')[0].toUpperCase(),
      email: email,
    };
    setUser(mockUser);
    localStorage.setItem('galxy_user', JSON.stringify(mockUser));

    const pendingItemStr = sessionStorage.getItem('pending_cart_item');
    if (pendingItemStr) {
      try {
        const pendingItem = JSON.parse(pendingItemStr);
        triggerToast('Auth success! Resuming Add-to-Cart...', 'warning');

        const res = await fetch('/api/cart/items', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(pendingItem),
        });

        const data = await res.json();
        if (res.status === 201 || data.success) {
          triggerToast('Successfully added your custom product configuration to cart!', 'success');
          
          const cartRes = await fetch('/api/cart');
          if (cartRes.ok) {
            const result = await cartRes.json();
            if (result.success && result.data) {
              setCartCount(result.data.item_count || 0);
            }
          }
        } else {
          triggerToast(data.message || 'Could not restore pending selection', 'error');
        }
      } catch (err) {
        console.error('Error resuming cart item:', err);
        triggerToast('Error automatically adding pending selection to cart', 'error');
      } finally {
        sessionStorage.removeItem('pending_cart_item');
      }
    } else {
      triggerToast(`Welcome back, ${mockUser.name}!`, 'success');
    }

    return { success: true };
  };

  const signup = async (name: string, email: string, phone: string, password?: string) => {
    return { success: true };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('galxy_user');
    triggerToast('Logged out successfully', 'success');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        cartCount,
        login,
        signup,
        logout,
        refreshCart,
        triggerToast,
        toast,
      }}
    >
      {children}
      
      {/* Visual Toast Component */}
      {toast && (
        <div 
          className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg transition-all duration-300 glass-panel animate-bounce"
          style={{
            borderColor: toast.type === 'success' ? '#FF2E8A' : toast.type === 'error' ? '#FFD84D' : '#18E7FF',
            boxShadow: `0 0 15px ${toast.type === 'success' ? 'rgba(255, 46, 138, 0.2)' : toast.type === 'error' ? 'rgba(255, 216, 77, 0.2)' : 'rgba(24, 231, 255, 0.2)'}`
          }}
        >
          <div 
            className="w-2.5 h-2.5 rounded-full"
            style={{
              backgroundColor: toast.type === 'success' ? '#FF2E8A' : toast.type === 'error' ? '#FFD84D' : '#18E7FF',
              boxShadow: `0 0 8px ${toast.type === 'success' ? '#FF2E8A' : toast.type === 'error' ? '#FFD84D' : '#18E7FF'}`
            }} 
          />
          <span className="text-sm font-semibold text-[#F4F4F7]">{toast.message}</span>
        </div>
      )}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
