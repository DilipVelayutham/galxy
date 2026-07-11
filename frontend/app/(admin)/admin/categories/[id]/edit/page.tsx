'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Category } from '@/types/category';
import { getCategory } from '@/lib/api/categories';
import { CategoryForm } from '@/components/admin/CategoryForm';
import { AttributeSchemaBuilder } from '@/components/admin/AttributeSchemaBuilder';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';

export default function EditCategoryPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const [category, setCategory] = useState<Category | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getCategory(id);
        setCategory(data);
      } catch {
        // If fetch fails, navigate back to list
        router.push('/admin/categories');
      } finally {
        setLoading(false);
      }
    })();
  }, [id, router]);

  if (loading) {
    return <LoadingSkeleton height="2rem" />;
  }

  if (!category) {
    return null; // Should never happen because of redirect above
  }

  return (
    <section>
      <h2 className="text-2xl font-bold mb-6 text-primaryNeon">
        Edit Category – {category.name}
      </h2>
      <CategoryForm initialData={category} />
      <AttributeSchemaBuilder
        categoryId={category._id}
        schema={category.attribute_schema}
        onSchemaChange={newSchema => setCategory({ ...category, attribute_schema: newSchema })}
      />
    </section>
  );
};
