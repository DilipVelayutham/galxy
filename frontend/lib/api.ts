const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

let accessToken = "";
let refreshInProgress: Promise<string | null> | null = null;

export const setAccessToken = (token: string) => {
  accessToken = token;
};

export const getAccessToken = () => {
  return accessToken;
};

// Generic response interface matching Flask standard contract
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  errors?: Record<string, string>;
  page?: number;
  limit?: number;
  total?: number;
  totalPages?: number;
  status?: number;
}

// Function to refresh the access token silently
const refreshSession = async (): Promise<string | null> => {
  if (refreshInProgress) return refreshInProgress;

  refreshInProgress = (async () => {
    try {
      const res = await fetch(`${BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (res.ok) {
        const body: ApiResponse = await res.json();
        if (body.success && body.data?.access_token) {
          const newToken = body.data.access_token;
          setAccessToken(newToken);
          return newToken;
        }
      }
      return null;
    } catch (e) {
      console.error("Session refresh failed", e);
      return null;
    } finally {
      refreshInProgress = null;
    }
  })();

  return refreshInProgress;
};

// Core fetch wrapper
export const apiRequest = async <T = any>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  const url = path.startsWith("http") ? path : `${BASE_URL}${path}`;
  
  // Set JSON headers
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  
  // Inject Bearer Token
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  
  options.credentials = "include"; // crucial for cookies
  options.headers = headers;

  let response = await fetch(url, options);

  // If unauthorized, attempt silent refresh
  if (response.status === 401) {
    const newToken = await refreshSession();
    if (newToken) {
      // Retry request with new token
      headers.set("Authorization", `Bearer ${newToken}`);
      options.headers = headers;
      response = await fetch(url, options);
    } else {
      // Clear token and broadcast logout event
      setAccessToken("");
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("auth-logout"));
      }
    }
  }

  // Parse JSON
  try {
    const data = await response.json();
    if (!response.ok) {
      return {
        success: false,
        message: data.message || "An error occurred",
        errors: data.errors,
        data: data.data,
        status: response.status
      };
    }
    return {
      ...data,
      status: response.status
    };
  } catch (err) {
    return {
      success: false,
      message: response.statusText || "Server communication failed",
      status: response.status
    };
  }
};

export const api = {
  get: <T = any>(path: string, options?: RequestInit) =>
    apiRequest<T>(path, { ...options, method: "GET" }),
    
  post: <T = any>(path: string, body?: unknown, options?: RequestInit) =>
    apiRequest<T>(path, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body)
    }),
    
  put: <T = any>(path: string, body?: unknown, options?: RequestInit) =>
    apiRequest<T>(path, {
      ...options,
      method: "PUT",
      body: body instanceof FormData ? body : JSON.stringify(body)
    }),
    
  delete: <T = any>(path: string, options?: RequestInit) =>
    apiRequest<T>(path, { ...options, method: "DELETE" }),

  uploadMedia: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiRequest<{ url: string; message?: string }>("/admin/media/upload", {
      method: "POST",
      body: formData,
    });
  }
};
