// Helper to build fetch URLs using the environment variable NEXT_PUBLIC_API_BASE_URL.

export const getApiUrl = (path: string): string => {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';
  // If base url ends with /api, and path starts with /api, remove it from path
  const cleanPath = path.startsWith('/api') ? path.substring(4) : path;
  
  // Clean up any double slashes (e.g. if baseUrl ends with / and cleanPath starts with /)
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const normalizedPath = cleanPath.startsWith('/') ? cleanPath : `/${cleanPath}`;
  
  return `${normalizedBase}${normalizedPath}`;
};
