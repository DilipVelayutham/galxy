import { api, unwrapApiResponse } from "./api";
import type { ApiResponse } from "../types/review";

export interface ProductSummary {
  _id: string;
  name: string;
  title?: string | undefined;
  sku?: string | undefined;
}

export const productService = {
  async list(): Promise<ProductSummary[]> {
    const response = await api.get<ApiResponse<ProductSummary[]>>("/api/products");
    return unwrapApiResponse(response.data);
  },
};
