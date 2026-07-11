// ==============================================================================
// LOCAL-TESTING STUB ONLY (NOT A DELIVERABLE)
// ==============================================================================
// This is a local testing stub for the shared useAuth() hook owned by in1.
// In the integrated app, this should be replaced by in1's actual useAuth/AuthContext.
// ==============================================================================

export function useAuth() {
  const getAccessToken = (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  };

  return { getAccessToken };
}
