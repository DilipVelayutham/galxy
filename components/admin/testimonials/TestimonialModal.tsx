"use client";

import type { ReactNode } from "react";
import type { Testimonial, TestimonialFormValues } from "../../../types/testimonial";
import { TestimonialForm } from "./TestimonialForm";
import { useFocusTrap } from "../../../hooks/useFocusTrap";

export interface TestimonialModalProps {
  open: boolean;
  testimonial?: Testimonial | null;
  loading: boolean;
  onClose: () => void;
  onSubmit: (values: TestimonialFormValues) => Promise<void>;
  renderMediaUpload?: (value: string | undefined, onChange: (url: string) => void) => ReactNode;
}

export function TestimonialModal({ open, testimonial, loading, onClose, onSubmit, renderMediaUpload }: TestimonialModalProps) {
  const containerRef = useFocusTrap(open, onClose);

  if (!open) return null;

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/70 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="testimonial-modal-title"
    >
      <div className="w-full max-w-xl rounded-2xl border border-white/10 bg-[#16161C] p-5 text-white shadow-2xl">
        <h2 id="testimonial-modal-title" className="text-lg font-semibold">
          {testimonial ? "Edit testimonial" : "Create testimonial"}
        </h2>
        <p className="mb-5 mt-2 text-sm text-slate-400">Manual testimonials can include an optional uploaded image.</p>
        <TestimonialForm
          testimonial={testimonial}
          loading={loading}
          onCancel={onClose}
          onSubmit={onSubmit}
          renderMediaUpload={renderMediaUpload}
        />
      </div>
    </div>
  );
}
