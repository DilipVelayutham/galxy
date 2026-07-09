/**
 * Utility helper functions for GALXY Admin Dashboard
 */

/**
 * Format a number as currency (INR)
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Generate a URL-friendly slug from a string
 * @param {string} text - The text to slugify
 * @returns {string} URL-friendly slug
 */
export const generateSlug = (text) => {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

/**
 * Truncate text to a specified length
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text with ellipsis if needed
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Format a date string to a readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
export const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('en-IN', options);
};

/**
 * Debounce function to limit rapid function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
};

/**
 * Get stock status badge info
 * @param {string} status - Stock status key
 * @returns {object} Badge label and color
 */
export const getStockStatusInfo = (status) => {
  const statusMap = {
    in_stock: { label: 'In Stock', color: '#22C55E', bg: 'rgba(34, 197, 94, 0.1)' },
    made_to_order: { label: 'Made to Order', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' },
    out_of_stock: { label: 'Out of Stock', color: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)' },
  };
  return statusMap[status] || statusMap.in_stock;
};

/**
 * Validate file for image upload
 * @param {File} file - File to validate
 * @returns {object} { valid: boolean, error?: string }
 */
export const validateImageFile = (file) => {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const acceptedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];

  if (!acceptedTypes.includes(file.type)) {
    return { valid: false, error: `Invalid file type: ${file.type}. Accepted: JPG, PNG, WebP, GIF` };
  }
  if (file.size > maxSize) {
    return { valid: false, error: `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Max: 5MB` };
  }
  return { valid: true };
};
