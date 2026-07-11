'use client';

import { useEffect, useState, useCallback } from 'react';
import { getCategories, deleteCategory, reorderCategories, updateCategory } from '@/lib/api/categories';
import { Category } from '@/types/category';
import { NeonButton } from '@/components/ui/NeonButton';
import { NeonInput } from '@/components/ui/NeonInput';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';
import { Toast } from '@/components/ui/Toast';
import Link from 'next/link';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';

export default function CategoryListPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const fetchCategories = useCallback(async () => {
    queueMicrotask(() => setLoading(true));
    try {
      const data = await getCategories(search, statusFilter);
      setCategories(data);
    } catch {
      setToast('Failed to load categories');
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchCategories();
  }, [fetchCategories]);

  const handleToggleActive = async (cat: Category) => {
    try {
      await updateCategory(cat._id, { is_active: !cat.is_active });
      fetchCategories();
    } catch {
      setToast('Failed to toggle status');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this category?')) return;
    try {
      await deleteCategory(id);
      fetchCategories();
    } catch {
      setToast('Delete failed');
    }
  };

  const onDragEnd = async (result: DropResult) => {
    if (!result.destination) return;
    const reordered = Array.from(categories);
    const [removed] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, removed);
    setCategories(reordered);
    try {
      await reorderCategories(reordered.map(c => c._id));
    } catch {
      setToast('Reorder failed');
    }
  };

  return (
    <section>
      <h2 className="text-3xl font-bold mb-6 text-primaryNeon">Categories</h2>
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <NeonInput
          placeholder="Search…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1"
        />
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive')}
          className="rounded bg-panelCharcoal text-textPrimary p-2"
        >
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <Link href="/admin/categories/new">
          <NeonButton variant="primary">Create Category</NeonButton>
        </Link>
      </div>

      {loading ? (
        <LoadingSkeleton height="2rem" />
      ) : (
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="categories">
            {provided => (
              <table
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="w-full table-auto border-collapse"
              >
                <thead className="bg-panelCharcoal">
                  <tr>
                    <th className="p-2 text-left">Name</th>
                    <th className="p-2 text-left">Accent</th>
                    <th className="p-2 text-left">Order</th>
                    <th className="p-2 text-left">Status</th>
                    <th className="p-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.map((cat, idx) => (
                    <Draggable key={cat._id} draggableId={cat._id} index={idx}>
                      {provided => (
                        <tr
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          className="border-b border-panelCharcoal hover:bg-panelCharcoal/50"
                        >
                          <td className="p-2" {...provided.dragHandleProps} style={{ cursor: 'move' }}>{cat.name}</td>
                          <td className="p-2">
                            <span
                              className="inline-block w-5 h-5 rounded-full"
                              style={{ backgroundColor: cat.accent_color }}
                            />
                          </td>
                          <td className="p-2">{cat.display_order}</td>
                          <td className="p-2">
                            <NeonButton
                              variant={cat.is_active ? 'primary' : 'danger'}
                              onClick={() => handleToggleActive(cat)}
                            >
                              {cat.is_active ? 'Active' : 'Inactive'}
                            </NeonButton>
                          </td>
                          <td className="p-2 flex gap-2">
                            <Link href={`/admin/categories/${cat._id}/edit`}>
                              <NeonButton variant="secondary">Edit</NeonButton>
                            </Link>
                            <NeonButton variant="danger" onClick={() => handleDelete(cat._id)}>
                              Delete
                            </NeonButton>
                          </td>
                        </tr>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </tbody>
              </table>
            )}
          </Droppable>
        </DragDropContext>
      )}

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </section>
  );
}
