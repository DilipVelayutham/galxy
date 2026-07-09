import axios, { AxiosError } from "axios";
import type { ApiResponse } from "../types/review";
import { FRIENDLY_ERROR_MESSAGES } from "../utils/constants";

const getBaseURL = (): string => {
  const envVal = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (envVal) {
    if (envVal.endsWith("/api")) {
      return envVal.slice(0, -4);
    }
    return envVal;
  }
  return "http://localhost:5000";
};

export const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

export const getApiErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message?: string; errors?: Record<string, string[]> }>;
    const status = axiosError.response?.status;
    const serverMessage = axiosError.response?.data?.message;

    if (serverMessage) return serverMessage;
    if (status && FRIENDLY_ERROR_MESSAGES[status]) return FRIENDLY_ERROR_MESSAGES[status];
  }

  if (error instanceof Error && error.message) return error.message;
  return "Something went wrong. Please try again.";
};

export const unwrapApiResponse = <T>(response: ApiResponse<T>): T => {
  if (!response.success) {
    throw new Error(response.message || "The requested action could not be completed.");
  }

  return response.data;
};
