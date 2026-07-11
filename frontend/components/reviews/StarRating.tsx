"use client";
import React, { useState, useId } from "react";
import { Star } from "lucide-react";
import { useReducedMotion } from "framer-motion";

/** Props for the StarRating component */
interface StarRatingProps {
  rating: number;
  interactive?: boolean;
  onChange?: (rating: number) => void;
  size?: number;
}

export const StarRating: React.FC<StarRatingProps> = ({
  rating,
  interactive = false,
  onChange,
  size = 20,
}) => {
  const [hoverRating, setHoverRating] = useState<number | null>(null);
  const [pulsingStar, setPulsingStar] = useState<number | null>(null);
  const [pulseKey, setPulseKey] = useState<number>(0);
  const shouldReduceMotion = useReducedMotion();
  const instanceId = useId();

  const handleClick = (value: number) => {
    if (interactive && onChange) {
      onChange(value);
      setPulsingStar(value);
      setPulseKey((prev) => prev + 1);
    }
  };

  const handleMouseEnter = (value: number) => {
    if (interactive) {
      setHoverRating(value);
    }
  };

  const handleMouseLeave = () => {
    if (interactive) {
      setHoverRating(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!interactive || !onChange) return;

    let nextRating = rating;
    switch (e.key) {
      case "ArrowRight":
      case "ArrowUp":
        nextRating = Math.min(5, rating + 1);
        break;
      case "ArrowLeft":
      case "ArrowDown":
        nextRating = Math.max(1, rating - 1);
        break;
      case "Home":
        nextRating = 1;
        break;
      case "End":
        nextRating = 5;
        break;
      case " ":
      case "Enter":
        e.preventDefault();
        const selectionVal = hoverRating !== null ? hoverRating : rating;
        onChange(selectionVal);
        setPulsingStar(selectionVal);
        setPulseKey((prev) => prev + 1);
        return;
      default:
        return;
    }

    e.preventDefault();
    onChange(nextRating);
    setPulsingStar(nextRating);
    setPulseKey((prev) => prev + 1);
  };

  const activeRating = hoverRating !== null ? hoverRating : rating;

  // Render a single star (handles partial fill for read-only averages)
  const renderStar = (index: number) => {
    const starValue = index + 1;

    if (interactive) {
      const isActive = starValue <= activeRating;
      const isPulsing = starValue === pulsingStar;
      const transitionClass = shouldReduceMotion
        ? ""
        : "transition-all duration-200 focus:scale-110 active:scale-95";
      
      return (
        <button
          key={index}
          type="button"
          tabIndex={-1} // Slider container is focused, not individual buttons
          aria-hidden="true" // Hidden from assistive tech to avoid redundant screen reader inputs
          onClick={() => handleClick(starValue)}
          onMouseEnter={() => handleMouseEnter(starValue)}
          onMouseLeave={handleMouseLeave}
          className={`text-transparent cursor-pointer focus:outline-none flex items-center justify-center ${transitionClass}`}
          style={{ minWidth: 44, minHeight: 44, padding: 8 }}
        >
          <Star
            key={isPulsing ? `pulse-${pulseKey}` : "static"}
            size={size}
            className={`transition-all duration-200 ${
              isPulsing && !shouldReduceMotion
                ? "animate-star-pulse text-neon-yellow fill-neon-yellow"
                : isActive
                ? "text-neon-yellow fill-neon-yellow drop-shadow-[0_0_8px_#FFD84D]"
                : "text-text-muted/30 fill-transparent"
            }`}
            style={{ width: size, height: size }}
          />
        </button>
      );
    }

    // Read-only partial fill logic
    let fillPercent = 0;
    if (rating >= starValue) {
      fillPercent = 100;
    } else if (rating > starValue - 1) {
      fillPercent = (rating - (starValue - 1)) * 100;
    }

    // Use a unique ID prefix with instanceId to prevent SVG ID naming collisions
    const gradientId = `star-grad-${instanceId}-${starValue}-${fillPercent}`;

    return (
      <div key={index} className="relative inline-block" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 24 24" className="absolute top-0 left-0" aria-hidden="true">
          <defs>
            <linearGradient id={gradientId}>
              <stop offset={`${fillPercent}%`} stopColor="var(--neon-yellow)" />
              <stop offset={`${fillPercent}%`} stopColor="rgba(138, 138, 151, 0.2)" />
            </linearGradient>
          </defs>
          <path
            d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"
            fill={`url(#${gradientId})`}
            stroke={fillPercent > 0 ? "var(--neon-yellow)" : "rgba(138, 138, 151, 0.3)"}
            strokeWidth="1"
            className={fillPercent > 0 ? "drop-shadow-[0_0_4px_rgba(255,216,77,0.4)]" : ""}
          />
        </svg>
      </div>
    );
  };

  if (interactive) {
    return (
      <div
        role="slider"
        aria-label="Star Rating Input"
        aria-valuenow={rating}
        aria-valuemin={1}
        aria-valuemax={5}
        aria-valuetext={`${rating} out of 5 stars`}
        tabIndex={0}
        onKeyDown={handleKeyDown}
        className="flex items-center gap-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-neon-violet/70 focus-visible:ring-offset-2 focus-visible:ring-offset-void-black p-1 rounded-lg transition-all cursor-pointer"
      >
        {Array.from({ length: 5 }).map((_, i) => renderStar(i))}
      </div>
    );
  }

  return (
    <div 
      className="flex items-center gap-1" 
      role="img" 
      aria-label={`Rated ${rating} out of 5 stars`}
    >
      {Array.from({ length: 5 }).map((_, i) => renderStar(i))}
    </div>
  );
};
