export const API_BASE_URL = 
  (typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_API_BASE_URL) || 
  (import.meta.env && import.meta.env.VITE_API_BASE_URL) || 
  'http://localhost:5000';
