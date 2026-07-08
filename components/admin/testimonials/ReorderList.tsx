"use client";

import { CSS } from "@dnd-kit/utilities";
import { DndContext, KeyboardSensor, PointerSensor, closestCenter, type DragEndEvent, useSensor, useSensors } from "@dnd-kit/core";
import { SortableContext, arrayMove, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { GripVertical, Star } from "lucide-react";
import type { Testimonial } from "../../../types/testimonial";

interface ReorderListProps {
  testimonials: Testimonial[];
  onReorder: (testimonials: Testimonial[]) => void;
}

interface SortableRowProps {
  testimonial: Testimonial;
}

function SortableRow({ testimonial }: SortableRowProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: testimonial._id });
  const style = { transform: CSS.Transform.toString(transform), transition };

  return (
    <li ref={setNodeRef} style={style} className={isDragging ? "relative z-10 opacity-80" : undefined}>
      <div className="grid grid-cols-[auto_1fr_auto] items-center gap-3 rounded-xl border border-white/10 bg-[#0B0B0F] p-3">
        <button
          type="button"
          {...attributes}
          {...listeners}
          aria-label={`Reorder testimonial by ${testimonial.customer_name}`}
          className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-white focus:outline-none focus:ring-2 focus:ring-cyan-400"
        >
          <GripVertical className="h-5 w-5" aria-hidden="true" />
        </button>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <p className="truncate font-medium text-white">{testimonial.customer_name}</p>
            <span className="inline-flex items-center gap-1 text-xs text-amber-200">
              <Star className="h-3.5 w-3.5 fill-amber-300 text-amber-300" aria-hidden="true" />
              {testimonial.rating}
            </span>
          </div>
          <p className="truncate text-xs text-slate-500">{testimonial.quote}</p>
        </div>
        <span className="rounded-full bg-white/5 px-2.5 py-1 text-xs font-semibold text-slate-300">
          #{testimonial.display_order}
        </span>
      </div>
    </li>
  );
}

export function ReorderList({ testimonials, onReorder }: ReorderListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = testimonials.findIndex((testimonial) => testimonial._id === active.id);
    const newIndex = testimonials.findIndex((testimonial) => testimonial._id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;

    onReorder(arrayMove(testimonials, oldIndex, newIndex));
  };

  return (
    <section className="rounded-2xl border border-white/10 bg-[#16161C] p-4" aria-labelledby="testimonial-reorder-title">
      <div className="mb-4">
        <h2 id="testimonial-reorder-title" className="text-base font-semibold text-white">
          Reorder Testimonials
        </h2>
        <p className="text-sm text-slate-500">Drag items to update display order.</p>
      </div>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={testimonials.map((testimonial) => testimonial._id)} strategy={verticalListSortingStrategy}>
          <ol className="grid gap-2">
            {testimonials.map((testimonial) => (
              <SortableRow key={testimonial._id} testimonial={testimonial} />
            ))}
          </ol>
        </SortableContext>
      </DndContext>
    </section>
  );
}
