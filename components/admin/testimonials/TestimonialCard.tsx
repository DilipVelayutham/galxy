"use client";

import { Star } from "lucide-react";
import type { Testimonial } from "../../../types/testimonial";
import { TESTIMONIAL_SOURCE_LABELS, cn } from "../../../utils/constants";

interface TestimonialCardProps {
  testimonial: Testimonial;
}

export function TestimonialCard({ testimonial }: TestimonialCardProps) {
  return (
    <article className="rounded-xl border border-white/10 bg-[#0B0B0F] p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          {testimonial.image_url ? (
            <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-full border border-white/10 bg-[#0B0B0F]">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={testimonial.image_url}
                alt={`${testimonial.customer_name} avatar`}
                className="h-full w-full object-cover"
              />
            </div>
          ) : (
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/5 text-xs font-semibold text-slate-400">
              {testimonial.customer_name.substring(0, 2).toUpperCase()}
            </div>
          )}
          <div>
            <h3 className="font-semibold text-white">{testimonial.customer_name}</h3>
            <p className="text-xs text-slate-500">{testimonial.customer_location || "Location not set"}</p>
          </div>
        </div>
        <span className={cn("rounded-full px-2.5 py-1 text-xs font-semibold", testimonial.source === "review" ? "bg-cyan-400/10 text-cyan-200" : "bg-violet-400/10 text-violet-200")}>{TESTIMONIAL_SOURCE_LABELS[testimonial.source]}</span>
      </div>
      <p className="mt-3 line-clamp-3 text-sm text-slate-300">“{testimonial.quote}”</p>
      <div className="mt-3 flex items-center justify-between text-sm text-slate-400">
        <span className="inline-flex items-center gap-1 text-amber-200"><Star className="h-4 w-4 fill-amber-300 text-amber-300" aria-hidden="true" />{testimonial.rating}</span>
        <span>Order {testimonial.display_order}</span>
      </div>
    </article>
  );
}
