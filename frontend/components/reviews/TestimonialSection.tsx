"use client";

import React, { useState, useEffect, useRef } from "react";
import { StarRating } from "./StarRating";
import { api } from "@/lib/api";
import { motion, useReducedMotion } from "framer-motion";
import { Quote, ChevronLeft, ChevronRight } from "lucide-react";

interface Testimonial {
  _id: string;
  customer_name: string;
  customer_location: string;
  quote: string;
  rating: number;
  image: string | null;
}

const TestimonialSkeleton: React.FC = () => (
  <div className="p-6 rounded-2xl bg-panel-charcoal/10 border border-panel-charcoal/30 flex flex-col gap-4 animate-pulse">
    <div className="h-4 w-20 bg-panel-charcoal/40 rounded" />
    <div className="space-y-2 mt-2">
      <div className="h-3 w-full bg-panel-charcoal/20 rounded" />
      <div className="h-3 w-[90%] bg-panel-charcoal/20 rounded" />
      <div className="h-3 w-[75%] bg-panel-charcoal/20 rounded" />
    </div>
    <div className="flex items-center gap-3 mt-4 pt-4 border-t border-panel-charcoal/30">
      <div className="w-10 h-10 rounded-full bg-panel-charcoal/40" />
      <div className="flex flex-col gap-2">
        <div className="h-3 w-24 bg-panel-charcoal/40 rounded" />
        <div className="h-2.5 w-16 bg-panel-charcoal/20 rounded" />
      </div>
    </div>
  </div>
);

export const TestimonialSection: React.FC = () => {
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [visibleCount, setVisibleCount] = useState<number>(3);

  const shouldReduceMotion = useReducedMotion();
  const carouselRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    const fetchTestimonials = async () => {
      try {
        const res = await api.get("/testimonials", { signal: controller.signal });
        if (res.success && res.data) {
          setTestimonials(res.data);
        }
        setLoading(false);
      } catch (e) {
        if (e instanceof Error && e.name !== 'AbortError') {
          console.error("Failed to load testimonials", e);
          setLoading(false);
        }
      }
    };
    fetchTestimonials();
    return () => controller.abort();
  }, []);

  // Update visibleCount based on window size
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setVisibleCount(1);
      } else if (window.innerWidth < 1024) {
        setVisibleCount(2);
      } else {
        setVisibleCount(3);
      }
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const maxIndex = Math.max(0, testimonials.length - visibleCount);

  // Auto-reset index if bounds change
  useEffect(() => {
    if (currentIndex > maxIndex) {
      setCurrentIndex(maxIndex);
    }
  }, [maxIndex, currentIndex]);

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : maxIndex));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < maxIndex ? prev + 1 : 0));
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      handlePrev();
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      handleNext();
    }
  };

  // Touch handlers for swiping
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart(e.targetTouches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > 50;
    const isRightSwipe = distance < -50;

    if (isLeftSwipe) {
      handleNext();
    } else if (isRightSwipe) {
      handlePrev();
    }
    setTouchStart(null);
    setTouchEnd(null);
  };

  // Framer Motion Animation Variants
  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.15,
      },
    },
  };

  const cardVariants = {
    hidden: { 
      opacity: 0, 
      y: shouldReduceMotion ? 0 : 30 
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: { 
        duration: 0.6, 
        ease: "easeOut" as const
      },
    },
  };

  if (loading) {
    return (
      <section className="py-20 bg-void-black relative">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <div className="h-8 w-64 bg-panel-charcoal/40 rounded mx-auto animate-pulse" />
            <div className="h-4 w-96 bg-panel-charcoal/20 rounded mx-auto mt-4 animate-pulse" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <TestimonialSkeleton />
            <TestimonialSkeleton />
            <TestimonialSkeleton />
          </div>
        </div>
      </section>
    );
  }

  if (testimonials.length === 0) {
    return null; // Don't render empty section
  }

  return (
    <section className="py-20 bg-void-black relative overflow-hidden">
      {/* Background Soft Glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-neon-pink/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-neon-blue/5 blur-[120px] pointer-events-none" />

      <div className="max-w-6xl mx-auto px-6 relative z-10">
        {/* Section Heading */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <motion.h2 
            initial={{ opacity: 0, y: -20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.5 }}
            className="text-3xl sm:text-4xl font-extrabold tracking-tight text-text-primary"
          >
            Loved by Our <span className="text-neon-pink text-glow-pink">Community</span>
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mt-4 text-text-muted text-sm sm:text-base"
          >
            See what customers say about Asil&apos;s custom neon signage and paper quilling frames.
          </motion.p>
        </div>

        {/* Carousel Container */}
        <div 
          ref={carouselRef}
          role="region"
          aria-label="Customer Testimonials Carousel"
          tabIndex={0}
          onKeyDown={handleKeyDown}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          className="relative px-0 md:px-12 focus:outline-none focus-visible:ring-2 focus-visible:ring-neon-pink/50 rounded-2xl"
        >
          {/* Side Navigation Buttons (Desktop/Tablet) */}
          {maxIndex > 0 && (
            <>
              <button
                onClick={handlePrev}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-20 hidden md:flex w-10 h-10 rounded-full bg-panel-charcoal hover:bg-void-black border border-neon-pink/40 hover:border-neon-pink text-neon-pink items-center justify-center cursor-pointer transition-all hover:glow-pink-hover focus:outline-none focus:ring-1 focus:ring-neon-pink"
                aria-label="Previous testimonials"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={handleNext}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-20 hidden md:flex w-10 h-10 rounded-full bg-panel-charcoal hover:bg-void-black border border-neon-pink/40 hover:border-neon-pink text-neon-pink items-center justify-center cursor-pointer transition-all hover:glow-pink-hover focus:outline-none focus:ring-1 focus:ring-neon-pink"
                aria-label="Next testimonials"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </>
          )}

          {/* Viewport wrapper */}
          <div className="overflow-hidden mx-[-12px]">
            {/* Sliding Track */}
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="flex"
              animate={{ x: `-${currentIndex * (100 / testimonials.length)}%` }}
              transition={shouldReduceMotion ? { duration: 0 } : { type: "spring", stiffness: 220, damping: 26 }}
              style={{
                width: `${(testimonials.length / visibleCount) * 100}%`,
              }}
            >
              {testimonials.map((t) => (
                <div
                  key={t._id}
                  style={{ width: `${100 / testimonials.length}%` }}
                  className="px-3 flex-shrink-0"
                >
                  <motion.div
                    variants={cardVariants}
                    className="p-6 rounded-2xl glass-panel border border-panel-charcoal flex flex-col justify-between relative hover:glow-pink-hover hover:border-neon-pink/20 hover:scale-[1.02] transition-all duration-300 h-full min-h-[220px]"
                  >
                    {/* Quote Icon */}
                    <Quote className="w-8 h-8 text-neon-pink/20 absolute top-6 right-6" />

                    <div className="flex flex-col gap-4">
                      {/* Rating */}
                      <StarRating rating={t.rating} size={16} />
                      
                      {/* Quote Text */}
                      <p className="text-sm text-text-primary leading-relaxed italic">
                        &ldquo;{t.quote}&rdquo;
                      </p>
                    </div>

                    {/* Customer details */}
                    <div className="flex items-center gap-4 mt-6 pt-4 border-t border-panel-charcoal/50">
                      {t.image ? (
                        <div className="w-10 h-10 rounded-full overflow-hidden border border-neon-pink/40">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img src={t.image} alt={t.customer_name} className="w-full h-full object-cover" />
                        </div>
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-panel-charcoal flex items-center justify-center border border-panel-charcoal text-neon-pink font-bold text-sm">
                          {t.customer_name.charAt(0)}
                        </div>
                      )}
                      
                      <div>
                        <h4 className="font-bold text-sm text-text-primary">{t.customer_name}</h4>
                        {t.customer_location && (
                          <span className="text-xs text-text-muted">{t.customer_location}</span>
                        )}
                      </div>
                    </div>
                  </motion.div>
                </div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* Carousel Bottom Controls (Indicators & Arrows for Mobile) */}
        {maxIndex > 0 && (
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8 px-3">
            {/* Indicators */}
            <div className="flex gap-2 justify-center" role="group" aria-label="Carousel slide page selectors">
              {Array.from({ length: maxIndex + 1 }).map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentIndex(idx)}
                  className={`h-2 rounded-full transition-all cursor-pointer ${
                    currentIndex === idx
                      ? "bg-neon-pink w-6 glow-pink"
                      : "bg-text-muted/30 hover:bg-text-muted/60 w-2"
                  }`}
                  aria-label={`Go to slide page ${idx + 1}`}
                  aria-current={currentIndex === idx ? "true" : "false"}
                />
              ))}
            </div>

            {/* Navigation Arrows for Mobile view */}
            <div className="flex gap-3 md:hidden">
              <button
                onClick={handlePrev}
                className="w-10 h-10 rounded-full bg-panel-charcoal hover:bg-void-black border border-neon-pink/40 hover:border-neon-pink text-neon-pink flex items-center justify-center cursor-pointer transition-all hover:glow-pink-hover focus:outline-none focus:ring-1 focus:ring-neon-pink"
                aria-label="Previous testimonials"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={handleNext}
                className="w-10 h-10 rounded-full bg-panel-charcoal hover:bg-void-black border border-neon-pink/40 hover:border-neon-pink text-neon-pink flex items-center justify-center cursor-pointer transition-all hover:glow-pink-hover focus:outline-none focus:ring-1 focus:ring-neon-pink"
                aria-label="Next testimonials"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
