import axios from 'axios';

export interface ApiErrorResponse {
  success: boolean;
  message: string;
  errors?: Record<string, string>;
}

export const getErrorMessage = (err: unknown): string => {
  if (axios.isAxiosError(err)) {
    const errorData = err.response?.data as ApiErrorResponse | undefined;
    if (errorData && typeof errorData === 'object') {
      if (errorData.errors && Object.keys(errorData.errors).length > 0) {
        const details = Object.entries(errorData.errors)
          .map(([key, val]) => `${key}: ${val}`)
          .join(', ');
        return `${errorData.message || 'Validation error'} (${details})`;
      }
      return errorData.message || err.message || 'An unexpected API error occurred.';
    }
    return err.message || 'An unexpected API error occurred.';
  }
  return err instanceof Error ? err.message : 'An unexpected error occurred.';
};

