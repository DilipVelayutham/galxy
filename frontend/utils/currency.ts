export const CURRENCY_CONFIG = {
  code: process.env.NEXT_PUBLIC_CURRENCY_CODE || 'INR',
  locale: process.env.NEXT_PUBLIC_CURRENCY_LOCALE || 'en-IN',
};

export const formatCurrency = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-';
  try {
    return new Intl.NumberFormat(CURRENCY_CONFIG.locale, {
      style: 'currency',
      currency: CURRENCY_CONFIG.code,
    }).format(value);
  } catch {
    // Fail-safe default
    const fixedVal = value.toFixed(2);
    return CURRENCY_CONFIG.code === 'INR' ? `₹${fixedVal}` : `${CURRENCY_CONFIG.code} ${fixedVal}`;
  }
};

export const getCurrencySymbol = (): string => {
  try {
    const formatter = new Intl.NumberFormat(CURRENCY_CONFIG.locale, {
      style: 'currency',
      currency: CURRENCY_CONFIG.code,
    });
    const parts = formatter.formatToParts(0);
    const symbolPart = parts.find((part) => part.type === 'currency');
    return symbolPart ? symbolPart.value : '₹';
  } catch {
    return '₹';
  }
};
