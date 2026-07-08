"use client";

import { useQuery } from "@tanstack/react-query";
import { productService } from "../services/productService";
import type { ProductSummary } from "../types/review";

export const useProducts = () => {
  return useQuery<ProductSummary[], Error>({
    queryKey: ["products"],
    queryFn: async () => {
      const data = await productService.list();
      if (!Array.isArray(data)) {
        throw new Error("Invalid response format: expected list of products.");
      }
      return data;
    },
    retry: 1,
    staleTime: 30000,
  });
};
