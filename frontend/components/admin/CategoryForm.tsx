'use client';

import { useEffect, useState } from 'react';
import { useForm, Resolver } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { NeonButton } from '@/components/ui/NeonButton';
import { NeonInput } from '@/components/ui/NeonInput';
import { Toast } from '@/components/ui/Toast';
import { Category } from '@/types/category';
import { createCategory, updateCategory } from '@/lib/api/categories';
import { useRouter } from 'next/navigation';
import { ImageUpload } from '@/components/admin/ImageUpload';

// Validation schema
const categorySchema = z.object({
  name: z.string().min(2, 'Name required'),
  slug: z.string().optional(),
  description: z.string().optional(),
  tagline: z.string().optional(),
  accent_color: z.enum(['#FF2E8A', '#18E7FF', '#9B5CFF', '#FFD84D']),
  display_order: z.coerce.number().int().min(0),
  is_active: z.boolean().default(true),
  seo: z.object({
    meta_title: z.string().optional(),
    meta_description: z.string().optional(),
    og_image: z.string().url().optional(),
  }).optional(),
});

type FormValues = z.infer<typeof categorySchema>;

type Props = { initialData?: Category };

export const CategoryForm = ({ initialData }: Props) => {
  const router = useRouter();
  const [toast, setToast] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(categorySchema) as Resolver<FormValues>,
    defaultValues: {
      accent_color: '#FF2E8A',
      is_active: true,
      display_order: 0,
    },
  });

  // Populate form when editing
  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        slug: initialData.slug,
        description: initialData.description ?? '',
        tagline: initialData.tagline ?? '',
        accent_color: initialData.accent_color,
        display_order: initialData.display_order,
        is_active: initialData.is_active,
        seo: initialData.seo ?? {},
      });
    }
  }, [initialData, reset]);

  const onSubmit = async (data: FormValues) => {
    try {
      if (initialData) {
        await updateCategory(initialData._id, data as Partial<Category>);
        setToast('Category updated');
      } else {
        await createCategory(data as Omit<Category, '_id' | 'created_at' | 'updated_at'>);
        setToast('Category created');
      }
      router.push('/admin/categories');
    } catch {
      setToast('Failed to save category');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit as Parameters<typeof handleSubmit>[0])} className="space-y-6 max-w-2xl">
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}

      <div>
        <label className="block mb-1 font-medium">Name *</label>
        <NeonInput {...register('name')} />
        {errors.name && <p className="text-sm text-accentViolet">{errors.name.message}</p>}
      </div>

      <div>
        <label className="block mb-1 font-medium">Slug (optional)</label>
        <NeonInput {...register('slug')} />
      </div>

      <div>
        <label className="block mb-1 font-medium">Description</label>
        <NeonInput {...register('description')} />
      </div>

      <div>
        <label className="block mb-1 font-medium">Tagline</label>
        <NeonInput {...register('tagline')} />
      </div>

      {/* Accent color picker */}
      <div>
        <label className="block mb-1 font-medium">Accent Color *</label>
        <div className="flex gap-2">
          {['#FF2E8A', '#18E7FF', '#9B5CFF', '#FFD84D'].map((c) => (
            <label key={c} className="flex items-center cursor-pointer">
              <input type="radio" value={c} {...register('accent_color')} className="hidden" />
              <span
                className={`w-6 h-6 rounded-full border-2 ${c === (initialData?.accent_color ?? '#FF2E8A') ? 'border-primaryNeon ring-2 ring-primaryNeon' : ''}`}
                style={{ backgroundColor: c }}
              />
            </label>
          ))}
        </div>
        {errors.accent_color && <p className="text-sm text-accentViolet">{errors.accent_color.message}</p>}
      </div>

      {/* Image uploads */}
      <ImageUpload label="Banner Image" />
      <ImageUpload label="Cover Image" />

      {/* SEO fields */}
      <fieldset className="border border-panelCharcoal p-4 rounded">
        <legend className="px-2 text-sm text-textMuted">SEO (optional)</legend>
        <div>
          <label className="block mb-1">Meta Title</label>
          <NeonInput {...register('seo.meta_title')} />
        </div>
        <div>
          <label className="block mb-1">Meta Description</label>
          <NeonInput {...register('seo.meta_description')} />
        </div>
        <div>
          <label className="block mb-1">OG Image URL</label>
          <NeonInput {...register('seo.og_image')} />
        </div>
      </fieldset>

      {/* Order & active toggle */}
      <div className="flex items-center gap-4">
        <div>
          <label className="block mb-1">Display Order</label>
          <NeonInput type="number" {...register('display_order')} />
        </div>
        <div className="flex items-center mt-6">
          <input type="checkbox" {...register('is_active')} id="active" className="mr-2" />
          <label htmlFor="active" className="text-sm">Active</label>
        </div>
      </div>

      <NeonButton type="submit" disabled={isSubmitting}>
        {initialData ? 'Update Category' : 'Create Category'}
      </NeonButton>
    </form>
  );
};
