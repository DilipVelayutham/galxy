"use client";

import { Edit, Star, Trash2 } from "lucide-react";
import type { Testimonial } from "../../../types/testimonial";
import { TESTIMONIAL_SOURCE_LABELS, cn } from "../../../utils/constants";
import { TestimonialCard } from "./TestimonialCard";

interface TestimonialTableProps {
  testimonials: Testimonial[];
  loading: boolean;
  error: string | null;
  actionId: string | null;
  onEdit: (testimonial: Testimonial) => void;
  onDelete: (testimonial: Testimonial) => void;
  onRetry: () => void;
}

export function TestimonialTable({
  testimonials,
  loading,
  error,
  actionId,
  onEdit,
  onDelete,
  onRetry,
}: TestimonialTableProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-white/10 bg-[#16161C] p-4">
        <div className="space-y-4" aria-label="Loading testimonials">
          <div className="h-10 rounded-xl bg-white/[0.03] animate-pulse w-full" />
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="grid grid-cols-4 gap-4 items-center h-14 animate-pulse rounded-xl bg-white/5 px-4">
              <div className="h-4 bg-white/10 rounded w-2/3" />
              <div className="h-4 bg-white/10 rounded w-1/3" />
              <div className="h-4 bg-white/10 rounded w-1/4" />
              <div className="h-8 bg-white/10 rounded ml-auto w-20" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-400/20 bg-[#16161C] p-6 text-center">
        <p className="text-sm text-red-200">{error}</p>
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-cyan-300"
        >
          Retry
        </button>
      </div>
    );
  }

  const testimonialsList = Array.isArray(testimonials) ? testimonials : [];

  if (testimonialsList.length === 0) {
    return (
      <div className="rounded-2xl border border-white/10 bg-[#16161C] p-8 text-center text-sm text-slate-400">
        No testimonials have been created yet.
      </div>
    );
  }

  return (
    <section className="grid gap-4">
      <div className="grid gap-3 md:hidden">
        {testimonialsList.map((testimonial) => {
          if (!testimonial || !testimonial._id) return null;
          return <TestimonialCard key={testimonial._id} testimonial={testimonial} />;
        })}
      </div>
      <div className="hidden overflow-hidden rounded-2xl border border-white/10 bg-[#16161C] shadow-xl shadow-black/20 md:block">
        <div className="overflow-x-auto">
          <table className="min-w-[900px] w-full border-collapse text-left text-sm">
            <thead className="bg-white/[0.03] text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-4 py-3 font-semibold">Customer</th>
                <th className="px-4 py-3 font-semibold">Location</th>
                <th className="px-4 py-3 font-semibold">Rating</th>
                <th className="px-4 py-3 font-semibold">Source Badge</th>
                <th className="px-4 py-3 font-semibold">Display Order</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10 text-slate-200">
              {testimonialsList.map((testimonial) => {
                if (!testimonial || !testimonial._id) return null;

                return (
                  <tr key={testimonial._id} className="transition hover:bg-white/[0.025]">
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-3">
                        {testimonial.image_url ? (
                          <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-full border border-white/10 bg-[#0B0B0F]">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                              src={testimonial.image_url}
                              alt={`${testimonial.customer_name ?? "Customer"} avatar`}
                              className="h-full w-full object-cover"
                            />
                          </div>
                        ) : (
                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/5 text-xs font-semibold text-slate-400">
                            {(testimonial.customer_name || "??").substring(0, 2).toUpperCase()}
                          </div>
                        )}
                        <div className="min-w-0">
                          <p className="font-medium text-white">{testimonial.customer_name ?? "Unknown Customer"}</p>
                          <p className="line-clamp-1 max-w-sm text-xs text-slate-500">{testimonial.quote ?? ""}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-slate-300">{testimonial.customer_location || "-"}</td>
                    <td className="px-4 py-4">
                      <span className="inline-flex items-center gap-1 text-amber-200">
                        <Star className="h-4 w-4 fill-amber-300 text-amber-300" aria-hidden="true" />
                        {testimonial.rating ?? 5}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={cn(
                          "rounded-full px-2.5 py-1 text-xs font-semibold",
                          testimonial.source === "review" ? "bg-cyan-400/10 text-cyan-200" : "bg-violet-400/10 text-violet-200"
                        )}
                      >
                        {TESTIMONIAL_SOURCE_LABELS[testimonial.source] ?? testimonial.source}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-slate-300">{testimonial.display_order ?? 0}</td>
                    <td className="px-4 py-4">
                      <span
                        className={cn(
                          "rounded-full px-2.5 py-1 text-xs font-semibold",
                          testimonial.is_active === false ? "bg-slate-500/10 text-slate-300" : "bg-emerald-400/10 text-emerald-200"
                        )}
                      >
                        {testimonial.is_active === false ? "Inactive" : "Active"}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          disabled={actionId === testimonial._id}
                          onClick={() => onEdit(testimonial)}
                          aria-label={`Edit testimonial by ${testimonial.customer_name}`}
                          className="inline-flex h-9 items-center gap-1 rounded-lg border border-cyan-400/30 bg-cyan-400/10 px-3 text-xs font-semibold text-cyan-200 transition hover:bg-cyan-400/20 focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-50"
                        >
                          <Edit className="h-3.5 w-3.5" aria-hidden="true" /> Edit
                        </button>
                        <button
                          type="button"
                          disabled={actionId === testimonial._id}
                          onClick={() => onDelete(testimonial)}
                          aria-label={`Delete testimonial by ${testimonial.customer_name}`}
                          className="inline-flex h-9 items-center gap-1 rounded-lg border border-red-400/30 bg-red-400/10 px-3 text-xs font-semibold text-red-200 transition hover:bg-red-400/20 focus:outline-none focus:ring-2 focus:ring-red-400 disabled:opacity-50"
                        >
                          <Trash2 className="h-3.5 w-3.5" aria-hidden="true" /> Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
