"use client";

import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, X, RefreshCw, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";
import type { Review, ReviewFormValues } from "../../../types/review";
import { useProducts } from "../../../hooks/useProducts";
import { reviewSchema } from "../../../utils/validators";

export interface ReviewFormProps {
  review?: Review | null;
  loading: boolean;
  onCancel: () => void;
  onSubmit: (values: Partial<Review>) => Promise<void>;
}

export function ReviewForm({ review, loading, onCancel, onSubmit }: ReviewFormProps) {
  const [imageUrlInput, setImageUrlInput] = useState("");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [lastUploadedFiles, setLastUploadedFiles] = useState<File[]>([]);

  // Fetch dynamic products using React Query
  const { data: products, isLoading: productsLoading, error: productsError } = useProducts();

  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
    setFocus,
    setValue,
    watch,
  } = useForm<ReviewFormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(reviewSchema) as any,
    defaultValues: {
      customer_name: "",
      email: "",
      title: "",
      product_id: "",
      product_name: "",
      comment: "",
      rating: 5,
      order_number: "",
      is_featured: false,
      images: [],
    },
  });

  const images = watch("images") || [];

  // Reset form when review object changes
  useEffect(() => {
    reset({
      customer_name: review?.customer_name ?? "",
      email: review?.email ?? "",
      title: review?.title ?? "",
      product_id: review?.product_id ?? "",
      product_name: review?.product_name ?? review?.product?.name ?? review?.product?.title ?? "",
      comment: review?.comment ?? "",
      rating: review?.rating ?? 5,
      order_number: review?.order_number ?? "",
      is_featured: review?.is_featured ?? false,
      images: review?.images ?? [],
    });
    const focusTimer = window.setTimeout(() => setFocus("customer_name"), 0);

    return () => window.clearTimeout(focusTimer);
  }, [reset, setFocus, review]);

  // Clean option lists for selecting products
  const productOptions = useMemo(() => {
    const list = products ? [...products] : [];
    if (review?.product_id && !list.some((p) => p._id === review.product_id)) {
      list.unshift({
        _id: review.product_id,
        name: review.product_name || review.product?.name || review.product?.title || "Current Product",
      });
    }
    return list;
  }, [products, review]);

  const handleAddImageUrl = () => {
    const trimmed = imageUrlInput.trim();
    if (!trimmed) return;

    if (!trimmed.startsWith("http://") && !trimmed.startsWith("https://") && !trimmed.startsWith("data:image/")) {
      toast.error("Please enter a valid URL starting with http://, https:// or data:image/");
      return;
    }

    setValue("images", [...images, trimmed], { shouldDirty: true, shouldValidate: true });
    setImageUrlInput("");
  };

  const processFiles = (files: FileList) => {
    setUploadError(null);
    setUploading(true);
    setLastUploadedFiles(Array.from(files));

    const promises = Array.from(files).map((file) => {
      return new Promise<string>((resolve, reject) => {
        if (!file.type.startsWith("image/")) {
          reject(new Error(`File "${file.name}" is not an image.`));
          return;
        }

        // Limit size to 5MB
        if (file.size > 5 * 1024 * 1024) {
          reject(new Error(`File "${file.name}" exceeds the 5MB size limit.`));
          return;
        }

        const reader = new FileReader();
        const timeoutId = setTimeout(() => {
          reader.abort();
          reject(new Error(`Upload timed out for "${file.name}".`));
        }, 10000); // 10s timeout

        reader.onload = (event) => {
          clearTimeout(timeoutId);
          const result = event.target?.result;
          if (typeof result === "string") {
            resolve(result);
          } else {
            reject(new Error(`Could not parse data for "${file.name}".`));
          }
        };

        reader.onerror = () => {
          clearTimeout(timeoutId);
          reject(new Error(`Error reading "${file.name}".`));
        };

        reader.readAsDataURL(file);
      });
    });

    Promise.all(promises)
      .then((results) => {
        setValue("images", [...images, ...results], {
          shouldDirty: true,
          shouldValidate: true,
        });
        toast.success("Images loaded successfully.");
      })
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .catch((err: any) => {
        setUploadError(err.message || "Upload failed.");
        toast.error(err.message || "Failed to upload images.");
      })
      .finally(() => {
        setUploading(false);
      });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    processFiles(files);
    e.target.value = "";
  };

  const handleRetryUpload = () => {
    if (lastUploadedFiles.length > 0) {
      const dataTransfer = new DataTransfer();
      lastUploadedFiles.forEach((file) => dataTransfer.items.add(file));
      processFiles(dataTransfer.files);
    }
  };

  const handleRemoveImage = (indexToRemove: number) => {
    setValue(
      "images",
      images.filter((_, idx) => idx !== indexToRemove),
      { shouldDirty: true, shouldValidate: true }
    );
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
        const payload: Partial<Review> = {
          customer_name: values.customer_name.trim(),
          email: values.email?.trim() || undefined,
          title: values.title?.trim() || undefined,
          product_id: values.product_id.trim(),
          product_name: values.product_name?.trim() || undefined,
          comment: values.comment.trim(),
          rating: Number(values.rating),
          order_number: values.order_number?.trim() || undefined,
          is_featured: !!values.is_featured,
          images: values.images || [],
        };
        await onSubmit(payload);
      })}
      className="grid gap-4 max-h-[70vh] overflow-y-auto px-1"
    >
      <div className="grid gap-4 sm:grid-cols-2">
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
          Customer Email <span className="text-xs text-slate-500">Optional</span>
          <input
            type="email"
            {...register("email")}
            className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          />
          {errors.email?.message && <span className="text-xs text-red-300">{errors.email.message}</span>}
        </label>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="grid gap-1 text-sm text-slate-200">
          Product Selection
          {productsLoading ? (
            <div className="h-[46px] rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-slate-400 animate-pulse flex items-center justify-between">
              <span>Loading dynamic products...</span>
              <RefreshCw className="h-4 w-4 animate-spin text-cyan-400" />
            </div>
          ) : productsError || !products ? (
            <div className="grid gap-1">
              <div className="flex items-center gap-1 text-xs text-amber-300">
                <AlertCircle className="h-3.5 w-3.5" />
                <span>Error loading products. Manual input enabled.</span>
              </div>
              <input
                type="text"
                {...register("product_id")}
                placeholder="Enter Product ID manually"
                className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              />
            </div>
          ) : (
            <select
              {...register("product_id")}
              className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 h-[46px]"
              onChange={(e) => {
                const selectedId = e.target.value;
                const found = productOptions.find((p) => p._id === selectedId);
                if (found) {
                  setValue("product_name", found.name || found.title || "");
                }
              }}
            >
              <option value="">-- Select Product --</option>
              {productOptions.map((p) => (
                <option key={p._id} value={p._id}>
                  {p.name || p.title || p._id} (ID: {p._id})
                </option>
              ))}
            </select>
          )}
          {errors.product_id?.message && <span className="text-xs text-red-300">{errors.product_id.message}</span>}
        </label>

        <label className="grid gap-1 text-sm text-slate-200">
          Product Name <span className="text-xs text-slate-500">Optional</span>
          <input
            type="text"
            {...register("product_name")}
            className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          />
          {errors.product_name?.message && <span className="text-xs text-red-300">{errors.product_name.message}</span>}
        </label>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <label className="grid gap-1 text-sm text-slate-200 sm:col-span-2">
          Review Title <span className="text-xs text-slate-500">Optional</span>
          <input
            type="text"
            {...register("title")}
            className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          />
          {errors.title?.message && <span className="text-xs text-red-300">{errors.title.message}</span>}
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
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="grid gap-1 text-sm text-slate-200">
          Order Number <span className="text-xs text-slate-500">Optional</span>
          <input
            type="text"
            {...register("order_number")}
            className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          />
          {errors.order_number?.message && <span className="text-xs text-red-300">{errors.order_number.message}</span>}
        </label>

        <div className="flex items-center gap-3 pt-6">
          <input
            type="checkbox"
            id="is_featured_checkbox"
            {...register("is_featured")}
            className="h-5 w-5 rounded border-white/10 bg-[#0B0B0F] text-cyan-400 focus:ring-2 focus:ring-cyan-400/20 outline-none cursor-pointer"
          />
          <label htmlFor="is_featured_checkbox" className="text-sm font-medium text-slate-200 cursor-pointer select-none">
            Feature this review (Highlight on site)
          </label>
        </div>
      </div>

      <label className="grid gap-1 text-sm text-slate-200">
        Review Comment
        <textarea
          rows={4}
          {...register("comment")}
          className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
        />
        {errors.comment?.message && <span className="text-xs text-red-300">{errors.comment.message}</span>}
      </label>

      <div className="grid gap-2 text-sm text-slate-200">
        <span className="font-medium">Images / Photos <span className="text-xs text-slate-500">Optional</span></span>
        <div className="grid gap-2 sm:grid-cols-[1fr_auto_auto]">
          <input
            type="text"
            value={imageUrlInput}
            onChange={(e) => setImageUrlInput(e.target.value)}
            placeholder="Paste image URL here..."
            className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-white outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          />
          <button
            type="button"
            onClick={handleAddImageUrl}
            className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-4 py-3 hover:bg-white/10 transition"
          >
            Add URL
          </button>
          <label className="inline-flex items-center justify-center rounded-xl bg-cyan-400 text-slate-950 px-4 py-3 font-semibold hover:bg-cyan-300 transition cursor-pointer">
            <Plus className="mr-1 h-4 w-4" /> Upload File
            <input type="file" multiple accept="image/*" onChange={handleFileUpload} className="hidden" />
          </label>
        </div>

        {uploading && <div className="text-xs text-cyan-300 animate-pulse mt-1">Reading files...</div>}

        {uploadError && (
          <div className="mt-2 flex items-center justify-between rounded-lg bg-red-500/10 border border-red-500/20 p-2.5 text-xs text-red-300">
            <span>{uploadError}</span>
            <button
              type="button"
              onClick={handleRetryUpload}
              className="font-bold underline text-red-200 hover:text-red-100 flex items-center gap-1 focus:outline-none"
            >
              <RefreshCw className="h-3 w-3" /> Retry
            </button>
          </div>
        )}

        {images.length > 0 && (
          <div className="mt-3 grid grid-cols-4 gap-3 sm:grid-cols-6 md:grid-cols-8">
            {images.map((url, index) => (
              <div key={index} className="group relative aspect-square rounded-xl border border-white/10 bg-[#0B0B0F] overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={url} alt={`Preview ${index + 1}`} className="h-full w-full object-cover" />
                <button
                  type="button"
                  onClick={() => handleRemoveImage(index)}
                  className="absolute right-1 top-1 flex h-6 w-6 items-center justify-center rounded-full bg-red-500/80 text-white hover:bg-red-600 transition opacity-0 group-hover:opacity-100"
                  aria-label={`Remove image ${index + 1}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-end gap-2 pt-4 border-t border-white/10 mt-2">
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
          className="rounded-lg bg-cyan-400 px-6 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-cyan-300 disabled:opacity-60"
        >
          {loading ? "Saving..." : review ? "Update Review" : "Create Review"}
        </button>
      </div>
    </form>
  );
}
