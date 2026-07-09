"use client";

import { Search } from "lucide-react";
import type { ReviewFiltersState } from "../../../types/review";
import { cn } from "../../../utils/constants";

interface ReviewFiltersProps {
  filters: ReviewFiltersState;
  onChange: (filters: Partial<ReviewFiltersState>) => void;
}

export function ReviewFilters({ filters, onChange }: ReviewFiltersProps) {
  return (
    <section className="rounded-2xl border border-white/10 bg-[#16161C] p-4 shadow-xl shadow-black/20" aria-label="Review filters">
      <div className="grid gap-3 md:grid-cols-[auto_1fr_220px] md:items-center">
        <div className="flex rounded-xl border border-white/10 bg-[#0B0B0F] p-1" role="tablist" aria-label="Approval status">
          {(["pending", "approved"] as const).map((approval) => (
            <button
              key={approval}
              type="button"
              role="tab"
              aria-selected={filters.approval === approval}
              onClick={() => onChange({ approval })}
              className={cn(
                "rounded-lg px-4 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-cyan-400",
                filters.approval === approval ? "bg-cyan-400 text-slate-950" : "text-slate-300 hover:bg-white/5 hover:text-white",
              )}
            >
              {approval === "pending" ? "Pending" : "Approved"}
            </button>
          ))}
        </div>

        <label className="relative block">
          <span className="sr-only">Search reviews</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" aria-hidden="true" />
          <input
            value={filters.search}
            onChange={(event) => onChange({ search: event.target.value })}
            placeholder="Search product, customer, comment, order"
            className="h-11 w-full rounded-xl border border-white/10 bg-[#0B0B0F] pl-10 pr-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          />
        </label>

        <label className="block">
          <span className="sr-only">Product ID filter</span>
          <input
            value={filters.product_id}
            onChange={(event) => onChange({ product_id: event.target.value })}
            placeholder="Product ID"
            className="h-11 w-full rounded-xl border border-white/10 bg-[#0B0B0F] px-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          />
        </label>
      </div>
    </section>
  );
}
