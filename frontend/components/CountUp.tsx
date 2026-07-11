"use client";

import React, { useEffect, useState } from "react";
import { useReducedMotion } from "framer-motion";

interface CountUpProps {
  value: number;
  duration?: number; // in ms
  prefix?: string;
  decimals?: number;
}

export default function CountUp({ value, duration = 800, prefix = "", decimals = 2 }: CountUpProps) {
  const [displayValue, setDisplayValue] = useState(value);
  const [isMounted, setIsMounted] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted) return;

    if (shouldReduceMotion) {
      setDisplayValue(value);
      return;
    }

    let startTimestamp: number | null = null;
    const startValue = 0;
    const endValue = value;
    let animationFrameId: number;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);

      // Easing out quad formula
      const easedProgress = progress * (2 - progress);
      const current = easedProgress * (endValue - startValue) + startValue;

      setDisplayValue(current);

      if (progress < 1) {
        animationFrameId = window.requestAnimationFrame(step);
      } else {
        setDisplayValue(endValue);
      }
    };

    animationFrameId = window.requestAnimationFrame(step);

    return () => {
      if (animationFrameId) {
        window.cancelAnimationFrame(animationFrameId);
      }
    };
  }, [value, duration, shouldReduceMotion, isMounted]);

  const renderValue = isMounted ? displayValue : value;
  const numericValue = typeof renderValue === "number" && !isNaN(renderValue) ? renderValue : 0;

  // Enforce en-US locale to prevent server-client locale-based hydration errors
  const formattedValue = isMounted
    ? numericValue.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
    : numericValue.toFixed(decimals);

  return (
    <span>
      {prefix}
      {formattedValue}
    </span>
  );
}

