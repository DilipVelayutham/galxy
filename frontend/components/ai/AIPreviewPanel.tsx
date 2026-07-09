"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, AlertCircle, RefreshCw, Eye } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/context/ToastContext";

interface AIPreviewPanelProps {
  categoryId: string;
  selectedAttributes: Record<string, any>;
  onPreviewGenerated: (url: string) => void;
  savedPreviewUrl: string | null;
}

export const AIPreviewPanel: React.FC<AIPreviewPanelProps> = ({
  categoryId,
  selectedAttributes,
  onPreviewGenerated,
  savedPreviewUrl,
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isStale, setIsStale] = useState<boolean>(false);
  const { showToast } = useToast();

  // Watch for changes in attributes that affect AI previews
  // (In dynamic mode, we check any attribute changes)
  useEffect(() => {
    if (savedPreviewUrl) {
      setIsStale(true);
    }
  }, [selectedAttributes]);

  const handleGenerate = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.post("/ai/generate-preview", {
        category_id: categoryId,
        selected_attributes: selectedAttributes,
      });

      if (res.success && res.data?.output_image_url) {
        onPreviewGenerated(res.data.output_image_url);
        setIsStale(false);
        showToast("AI Preview generated successfully!", "success");
      } else {
        // Handle rate limiting specifically (429 or status messages)
        if (res.message?.includes("limit") || res.message?.includes("rate")) {
          setErrorMsg("You have hit the preview generation limit. Please log in or wait until tomorrow.");
        } else {
          setErrorMsg(res.message || "Failed to generate AI preview.");
        }
        showToast(res.message || "AI Generator busy", "warning");
      }
    } catch (err) {
      setErrorMsg("Failed to connect to the AI preview generation engine.");
      showToast("Generation failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative w-full h-[400px] rounded-xl overflow-hidden bg-void-black border border-panel-charcoal flex flex-col items-center justify-center p-6">
      
      {/* 1. Loading/Scan state */}
      {loading && (
        <div className="absolute inset-0 z-20 bg-void-black/90 flex flex-col items-center justify-center gap-4">
          {/* Neon animated scanning line */}
          <div className="absolute top-0 left-0 w-full h-1 bg-neon-blue drop-shadow-[0_0_10px_#18E7FF] animate-[bounce_3s_infinite]" />
          <div className="w-12 h-12 rounded-full border-t-2 border-r-2 border-neon-blue animate-spin" />
          <div className="text-center">
            <h4 className="text-sm font-bold text-neon-blue text-glow-blue tracking-wide uppercase">Generative AI Preview Active</h4>
            <p className="text-[10px] text-text-muted mt-1.5">Assembling lighting prompt constraints...</p>
          </div>
        </div>
      )}

      {/* 2. Success preview display */}
      {!loading && savedPreviewUrl && (
        <div className="absolute inset-0 z-10 w-full h-full flex flex-col justify-end">
          <img
            src={savedPreviewUrl}
            alt="AI Preview"
            className={`w-full h-full object-cover transition-opacity duration-300 ${
              isStale ? "opacity-40 filter blur-[1px]" : "opacity-90"
            }`}
          />
          
          {/* Overlay text detail info */}
          <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-void-black/90 via-void-black/60 to-transparent flex flex-col gap-2">
            <span className="text-[10px] text-text-muted font-bold italic tracking-wide">
              * AI-generated approximation. Actual handcraft detail may vary slightly.
            </span>
            
            {/* Stale warn details */}
            {isStale && (
              <div className="flex items-center justify-between gap-3 bg-void-black/80 border border-neon-yellow/30 p-2.5 rounded-lg">
                <span className="text-[10px] text-neon-yellow font-bold flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5" /> Configuration changed - preview outdated
                </span>
                <button
                  onClick={handleGenerate}
                  className="px-2.5 py-1 text-[10px] bg-neon-yellow text-void-black rounded font-black hover:opacity-85 cursor-pointer"
                >
                  RE-GENERATE
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 3. Empty/Generate State */}
      {!loading && !savedPreviewUrl && (
        <div className="text-center flex flex-col items-center gap-4 max-w-sm">
          <Sparkles className="w-12 h-12 text-neon-violet drop-shadow-[0_0_10px_#9B5CFF]" />
          <div>
            <h3 className="text-sm font-extrabold text-text-primary tracking-wide">AI-POWERED PREVIEW</h3>
            <p className="text-xs text-text-muted mt-2 leading-relaxed">
              Visualize your design in a virtual space. Gemini AI compiles parameters and draws a neon lighting approximation before checkout.
            </p>
          </div>
          
          {errorMsg && (
            <div className="p-2.5 rounded bg-neon-pink/5 border border-neon-pink/20 text-neon-pink text-[10px] font-semibold">
              {errorMsg}
            </div>
          )}

          <button
            onClick={handleGenerate}
            className="px-5 py-3 rounded-lg bg-panel-charcoal hover:bg-void-black border border-neon-violet/40 text-neon-violet font-bold text-xs glow-violet-hover transition-all cursor-pointer flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> GENERATE PREVIEW IMAGE
          </button>
        </div>
      )}
    </div>
  );
};
