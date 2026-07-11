// components/admin/ImageUpload.tsx
'use client';
import { useState } from "react";
import { Toast } from "@/components/ui/Toast";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";

type Props = {
  label: string;
  // Callback to pass uploaded URL back to parent form
  onUpload?: (url: string) => void;
};

export const ImageUpload = ({ label, onUpload }: Props) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    setLoading(true);
    try {
      const res = await fetch("/api/admin/media/upload", {
        method: "POST",
        body: form,
      });
      const json = await res.json();
      if (!json.success) throw new Error(json.message || "Upload failed");
      const url = json.data?.url || json.url;
      setPreview(url);
      onUpload?.(url);
    } catch {
      setToast("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="space-y-2">
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
      <label className="block text-sm font-medium mb-1">{label}</label>
      <div className="flex items-center gap-4">
        <input type="file" accept="image/*" onChange={onChange} />
        {loading && <LoadingSkeleton height="2rem" width="8rem" />}
        {preview && (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img
            src={preview}
            alt="preview"
            className="h-20 w-auto rounded shadow-neon"
          />
        )}
      </div>
    </div>
  );
};
