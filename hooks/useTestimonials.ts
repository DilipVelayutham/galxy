"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getApiErrorMessage } from "../services/api";
import { testimonialService } from "../services/testimonialService";
import type { ReorderTestimonialPayload, Testimonial, TestimonialFormValues } from "../types/testimonial";

export const useTestimonials = () => {
  const queryClient = useQueryClient();
  const [actionId, setActionId] = useState<string | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["testimonials"],
    queryFn: async () => {
      const res = await testimonialService.list();
      return res.testimonials;
    },
    retry: 1,
    staleTime: 30000,
  });

  const testimonials = data ?? [];

  const create = async (payload: TestimonialFormValues) => {
    try {
      await testimonialService.create(payload);
      toast.success("Testimonial created.");
      await queryClient.invalidateQueries({ queryKey: ["testimonials"] });
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    }
  };

  const update = async (testimonialId: string, payload: TestimonialFormValues) => {
    setActionId(testimonialId);
    try {
      await testimonialService.update(testimonialId, payload);
      toast.success("Testimonial updated.");
      await queryClient.invalidateQueries({ queryKey: ["testimonials"] });
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    } finally {
      setActionId(null);
    }
  };

  const remove = async (testimonialId: string) => {
    setActionId(testimonialId);
    try {
      await testimonialService.delete(testimonialId);
      toast.success("Testimonial deleted.");
      await queryClient.invalidateQueries({ queryKey: ["testimonials"] });
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    } finally {
      setActionId(null);
    }
  };

  const reorder = async (orderedTestimonials: Testimonial[]) => {
    const previous = testimonials;
    const normalized = orderedTestimonials.map((testimonial, index) => ({
      ...testimonial,
      display_order: index + 1,
    }));
    const payload: ReorderTestimonialPayload[] = normalized.map((testimonial) => ({
      testimonial_id: testimonial._id,
      display_order: testimonial.display_order,
    }));

    // Optimistic Update
    queryClient.setQueryData(["testimonials"], normalized);

    try {
      await testimonialService.reorder(payload);
      toast.success("Testimonials reordered.");
      await queryClient.invalidateQueries({ queryKey: ["testimonials"] });
    } catch (err) {
      // Rollback
      queryClient.setQueryData(["testimonials"], previous);
      toast.error(getApiErrorMessage(err));
    }
  };

  return {
    actionId,
    create,
    error: error ? getApiErrorMessage(error) : null,
    fetchTestimonials: refetch,
    loading: isLoading,
    remove,
    reorder,
    testimonials,
    update,
  };
};
