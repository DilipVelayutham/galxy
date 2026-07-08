"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { X, RefreshCw } from "lucide-react";
import toast from "react-hot-toast";
import type { Testimonial, TestimonialFormValues } from "../../../types/testimonial";
import { testimonialSchema } from "../../../utils/validators";

export interface TestimonialFormProps {
  testimonial?: Testimonial | null;
  loading: boolean;
  onCancel: () => void;
  onSubmit: (values: TestimonialFormValues) => Promise<void>;
  renderMediaUpload?: (value: string | undefined, onChange: (url: string) => void) => ReactNode;
}

export function TestimonialForm({ testimonial, loading, onCancel, onSubmit, renderMediaUpload }: TestimonialFormProps) {
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [lastUploadedFile, setLastUploadedFile] = useState<File | null>(null);

  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
    setFocus,
    setValue,
    watch,
  } = useForm<TestimonialFormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(testimonialSchema) as any,
    defaultValues: {
      customer_name: "",
      customer_location: "",
      quote: "",
      rating: 5,
      image_url: "",
      is_active: true,
    },
  });

  const imageUrl = watch("image_url");

  useEffect(() => {
    reset({
      customer_name: testimonial?.customer_name ?? "",
      customer_location: testimonial?.customer_location ?? "",
      quote: testimonial?.quote ?? "",
      rating: testimonial?.rating ?? 5,
      image_url: testimonial?.image_url ?? "",
      is_active: testimonial?.is_active ?? true,
    });
    const focusTimer = window.setTimeout(() => setFocus("customer_name"), 0);

    return () => window.clearTimeout(focusTimer);
  }, [reset, setFocus, testimonial]);

  const processFile = (file: File) => {
    setUploadError(null);
    setUploading(true);
    setLastUploadedFile(file);

    if (!file.type.startsWith("image/")) {
      setUploadError("Only image files are allowed.");
      toast.error("Only image files are allowed.");
      setUploading(false);
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setUploadError("Image size exceeds the 5MB limit.");
      toast.error("Image size exceeds the 5MB limit.");
      setUploading(false);
      return;
    }

    const reader = new FileReader();
    const timeoutId = setTimeout(() => {
      reader.abort();
      setUploadError("Upload timed out.");
      toast.error("Image upload timed out.");
      setUploading(false);
    }, 10000);

    reader.onload = (event) => {
      clearTimeout(timeoutId);
      const result = event.target?.result;
      if (typeof result === "string") {
        setValue("image_url", result, { shouldDirty: true, shouldValidate: true });
        toast.success("Image uploaded successfully.");
      } else {
        setUploadError("Could not read image content.");
        toast.error("Failed to read image content.");
      }
      setUploading(false);
    };

    reader.onerror = () => {
      clearTimeout(timeoutId);
      setUploadError("Error reading file.");
      toast.error("Error reading image file.");
      setUploading(false);
    };

    reader.readAsDataURL(file);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    processFile(files[0]);
    e.target.value = "";
  };

  const handleRetryUpload = () => {
    if (lastUploadedFile) {
      processFile(lastUploadedFile);
    }
  };

  const handleCancel = () => {
    reset();
    setUploadError(null);
    setUploading(false);
    onCancel();
  };

  return (
    <form
      onSubmit={handleSubmit(async (values) => {
        const payload: TestimonialFormValues = {
          customer_name: values.customer_name.trim(),
          quote: values.quote.trim(),
          rating: Number(values.rating),
          is_active: !!values.is_active,
        };
        const customerLocation = values.customer_location?.trim();
        const imageUrlValue = values.image_url?.trim();

        if (customerLocation) payload.customer_location = customerLocation;
        else payload.customer_location = undefined;

        if (imageUrlValue) payload.image_url = imageUrlValue;
        else payload.image_url = undefined;

        await onSubmit(payload);
      })}
      className="grid gap-4"
    >
      <label className="grid gap-1 text-sm text-slate-200">
        Customer Name
        <input
          type="text"
          {...register("customer_name")}
          className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
        />
        {errors.customer_name?.message && <span className="text-xs text-red-300">{errors.customer_name.message}</span>}
      </label>

      <label className="grid gap-1 text-sm text-slate-200">
        Customer Location <span className="text-xs text-slate-500">Optional</span>
        <input
          type="text"
          {...register("customer_location")}
          className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
        />
        {errors.customer_location?.message && <span className="text-xs text-red-300">{errors.customer_location.message}</span>}
      </label>

      <label className="grid gap-1 text-sm text-slate-200">
        Quote
        <textarea
          rows={5}
          {...register("quote")}
          className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
        />
        {errors.quote?.message && <span className="text-xs text-red-300">{errors.quote.message}</span>}
      </label>

      <label className="grid gap-1 text-sm text-slate-200">
        Rating
        <select
          {...register("rating")}
          className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 h-[46px]"
        >
          {[5, 4, 3, 2, 1].map((rating) => (
            <option key={rating} value={rating}>
              {rating} Stars
            </option>
          ))}
        </select>
        {errors.rating?.message && <span className="text-xs text-red-300">{errors.rating.message}</span>}
      </label>

      <div className="grid gap-2 text-sm text-slate-200">
        <span>Image Upload <span className="text-xs text-slate-500">Optional</span></span>
        {renderMediaUpload ? (
          renderMediaUpload(imageUrl || undefined, (url) =>
            setValue("image_url", url, { shouldDirty: true, shouldValidate: true })
          )
        ) : (
          <div className="grid gap-2">
            <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
              <input
                type="text"
                value={imageUrl || ""}
                onChange={(e) => setValue("image_url", e.target.value, { shouldDirty: true, shouldValidate: true })}
                placeholder="Paste image URL here..."
                className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              />
              <label className="inline-flex items-center justify-center rounded-xl bg-cyan-400 text-slate-950 px-4 py-3 font-semibold hover:bg-cyan-300 transition cursor-pointer">
                Upload File
                <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
              </label>
            </div>

            {uploading && <div className="text-xs text-cyan-300 animate-pulse">Reading file...</div>}

            {uploadError && (
              <div className="flex items-center justify-between rounded-lg bg-red-500/10 border border-red-500/20 p-2.5 text-xs text-red-300">
                <span>{uploadError}</span>
                <button
                  type="button"
                  onClick={handleRetryUpload}
                  className="font-bold underline text-red-200 hover:text-red-100 flex items-center gap-1 focus:outline-none"
                >
                  <RefreshCw className="h-3.5 w-3.5" /> Retry
                </button>
              </div>
            )}

            {imageUrl && (
              <div className="relative h-20 w-20 overflow-hidden rounded-xl border border-white/10 bg-[#0B0B0F]">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={imageUrl} alt="Testimonial preview" className="h-full w-full object-cover" />
                <button
                  type="button"
                  onClick={() => setValue("image_url", "", { shouldDirty: true, shouldValidate: true })}
                  className="absolute right-1 top-1 flex h-6 w-6 items-center justify-center rounded-full bg-red-500/80 text-white hover:bg-red-600 transition"
                  aria-label="Remove image"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            )}
          </div>
        )}
        <input type="hidden" {...register("image_url")} />
      </div>

      <div className="flex items-center gap-3 pt-2">
        <input
          type="checkbox"
          id="is_active_checkbox"
          {...register("is_active")}
          className="h-5 w-5 rounded border-white/10 bg-[#0B0B0F] text-cyan-400 focus:ring-2 focus:ring-cyan-400/20 outline-none cursor-pointer"
        />
        <label htmlFor="is_active_checkbox" className="text-sm font-medium text-slate-200 cursor-pointer select-none">
          Active (Visible on public site)
        </label>
      </div>

      <div className="flex justify-end gap-2 pt-2 border-t border-white/10 mt-2">
        <button
          type="button"
          onClick={handleCancel}
          className="rounded-lg px-4 py-2 text-sm text-slate-300 hover:bg-white/5 focus:outline-none focus:ring-2 focus:ring-slate-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading || uploading}
          className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-cyan-300 disabled:opacity-60"
        >
          {loading ? "Saving..." : testimonial ? "Update" : "Create"}
        </button>
      </div>
    </form>
  );
}
