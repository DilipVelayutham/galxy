import { CategoryForm } from '@/components/admin/CategoryForm';
import { NeonButton } from '@/components/ui/NeonButton';
import Link from 'next/link';

export default function NewCategoryPage() {
  return (
    <section>
      <h2 className="text-2xl font-bold mb-6 text-primaryNeon">Create New Category</h2>
      <CategoryForm />
      <div className="mt-4">
        <Link href="/admin/categories">
          <NeonButton variant="secondary">Back to Categories</NeonButton>
        </Link>
      </div>
    </section>
  );
}
