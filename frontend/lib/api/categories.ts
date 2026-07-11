// lib/api/categories.ts
import { apiRequest } from '@/lib/api';
import { Category } from '@/types/category';

/** Fetch list of categories with optional search and status filter */
export const getCategories = async (
  search = '',
  status: 'all' | 'active' | 'inactive' = 'all'
): Promise<Category[]> => {
  const query: Record<string, string> = {};
  if (search) query.q = search;
  if (status !== 'all') query.status = status;
  return await apiRequest<Category[]>('GET', '/api/categories', undefined, query);
};

/** Get a single category by its slug or MongoDB ID */
export const getCategory = async (slugOrId: string): Promise<Category> => {
  return await apiRequest<Category>('GET', `/api/categories/${slugOrId}`);
};

/** Create a brand‑new category (admin endpoint) */
export const createCategory = async (
  payload: Omit<Category, '_id' | 'created_at' | 'updated_at'>
): Promise<Category> => {
  return await apiRequest<Category>('POST', '/api/admin/categories', payload);
};

/** Update an existing category (admin endpoint) */
export const updateCategory = async (
  id: string,
  payload: Partial<Category>
): Promise<Category> => {
  return await apiRequest<Category>('PUT', `/api/admin/categories/${id}`, payload);
};

/** Delete a category (admin endpoint) */
export const deleteCategory = async (id: string): Promise<null> => {
  return await apiRequest<null>('DELETE', `/api/admin/categories/${id}`);
};

/** Persist a new display order after drag‑and‑drop */
export const reorderCategories = async (orderedIds: string[]): Promise<null> => {
  return await apiRequest<null>('PUT', '/api/admin/categories/reorder', {
    orderedIds,
  });
};
