"use client";

import React, { useState, useRef, useEffect } from "react";
import { StarRating } from "./StarRating";
import { useToast } from "@/context/ToastContext";
import { api } from "@/lib/api";
import { Camera, Loader2, X } from "lucide-react";

interface ReviewFormProps {
  productId: string;
  onSuccess?: () => void;
}

export const ReviewForm: React.FC<ReviewFormProps> = ({ productId, onSuccess }) => {
  const [rating, setRating] = useState<number>(5);
  const [comment, setComment] = useState<string>("");
  const [images, setImages] = useState<string[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  const { showToast } = useToast();
  
  const errorRef = useRef<HTMLDivElement>(null);
  const successRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Focus managers for screen reader accessibility
  useEffect(() => {
    if (errorMsg) {
      errorRef.current?.focus();
    }
  }, [errorMsg]);

  useEffect(() => {
    if (successMsg) {
      successRef.current?.focus();
    }
  }, [successMsg]);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    setUploading(true);
    setErrorMsg(null);
    
    try {
      // Reusing the shared upload helper instead of duplicate logic
      const res = await api.uploadMedia(files[0]);
      const imageUrl = res.data?.url;
      if (res.success && imageUrl) {
        setImages((prev) => [...prev, imageUrl]);
        showToast("Image uploaded successfully!", "success");
      } else {
        showToast(res.message || "Failed to upload image", "error");
      }
    } catch {
      showToast("Media upload connection failed", "error");
    } finally {
      setUploading(false);
      // Clear file input value to allow uploading same file again
      if (e.target) {
        e.target.value = "";
      }
    }
  };

  const handleRemoveImage = (indexToRemove: number) => {
    setImages((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleUploadKeyDown = (e: React.KeyboardEvent<HTMLLabelElement>) => {
    if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      fileInputRef.current?.click();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim()) {
      showToast("Please enter a comment for your review", "warning");
      return;
    }
    
    setSubmitting(true);
    setErrorMsg(null);
    
    try {
      const res = await api.post(`/products/${productId}/reviews`, {
        rating,
        comment: comment.trim(),
        images
      });
      
      if (res.success) {
        setSuccessMsg("Review submitted, pending approval");
        showToast("Review submitted, pending approval", "success");
        if (onSuccess) onSuccess();
      } else {
        // Implement proper 403 and 409 error handling exactly as defined by the backend contract
        const backendMsg = res.message || "Could not submit review";
        if (res.status === 403 || backendMsg.toLowerCase().includes("not a verified delivered purchase")) {
          setErrorMsg(backendMsg);
        } else if (res.status === 409 || backendMsg.toLowerCase().includes("already reviewed")) {
          setErrorMsg("You've already reviewed this order's purchase of this product");
        } else {
          setErrorMsg(backendMsg);
        }
        showToast(backendMsg, "error");
      }
    } catch {
      setErrorMsg("Failed to connect to reviews server");
      showToast("Submission failed", "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (successMsg) {
    return (
      <div 
        ref={successRef}
        tabIndex={-1}
        role="alert"
        className="p-6 rounded-xl glass-panel border border-neon-blue/30 text-center focus:outline-none focus:ring-1 focus:ring-neon-blue"
      >
        <h4 className="text-neon-blue text-lg font-bold mb-2 text-glow-blue">Submission Received!</h4>
        <p className="text-sm text-text-muted">{successMsg}</p>
      </div>
    );
  }

  return (
    <form 
      onSubmit={handleSubmit} 
      className="p-6 rounded-xl glass-panel border border-panel-charcoal flex flex-col gap-5"
      aria-label="Submit Product Review Form"
    >
      <h3 className="text-lg font-bold text-text-primary uppercase tracking-tight">Leave a Product Review</h3>
      
      {errorMsg && (
        <div 
          ref={errorRef}
          tabIndex={-1}
          role="alert"
          className="p-3.5 rounded-lg border border-neon-pink/30 bg-neon-pink/5 text-neon-pink text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-neon-pink flex items-start gap-2 justify-between"
        >
          <span>{errorMsg}</span>
          <button 
            type="button" 
            onClick={() => setErrorMsg(null)}
            className="text-neon-pink/60 hover:text-neon-pink cursor-pointer"
            aria-label="Dismiss error message"
          >
            <X className="w-4 h-4 flex-shrink-0" />
          </button>
        </div>
      )}

      {/* Star Input */}
      <div className="flex flex-col gap-2">
        <label className="text-xs text-text-muted uppercase tracking-wider font-bold">Your Rating</label>
        <StarRating rating={rating} interactive={true} onChange={setRating} size={28} />
      </div>

      {/* Comment Input */}
      <div className="flex flex-col gap-2">
        <label htmlFor="review-comment" className="text-xs text-text-muted uppercase tracking-wider font-bold">Review Details</label>
        <textarea
          id="review-comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Share your experience about the design, glow, and overall quality..."
          rows={4}
          required
          aria-required="true"
          aria-label="Review Comments text area"
          className="w-full p-3 rounded-lg border border-panel-charcoal bg-void-black text-sm text-text-primary focus:outline-none focus:border-neon-blue/50 focus:glow-blue transition-all resize-none"
        />
      </div>

      {/* Image Upload Widget */}
      <div className="flex flex-col gap-2">
        <span className="text-xs text-text-muted uppercase tracking-wider font-bold">Add Product Photos (Max 3)</span>
        <div className="flex flex-wrap gap-3 items-center">
          {/* Preview grid */}
          {images.map((img, idx) => (
            <div key={idx} className="relative w-16 h-16 rounded-lg overflow-hidden border border-panel-charcoal group">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={img} alt={`Uploaded product preview ${idx + 1}`} className="w-full h-full object-cover" />
              <button
                type="button"
                onClick={() => handleRemoveImage(idx)}
                className="absolute inset-0 bg-void-black/70 flex items-center justify-center text-xs text-neon-pink font-bold opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity cursor-pointer"
                aria-label={`Remove uploaded product photo number ${idx + 1}`}
              >
                Remove
              </button>
            </div>
          ))}
          
          {/* Upload Button */}
          {images.length < 3 && (
            <label 
              role="button"
              tabIndex={0}
              onKeyDown={handleUploadKeyDown}
              aria-label="Upload photo to attach to review"
              className="w-16 h-16 rounded-lg border border-dashed border-text-muted/30 hover:border-neon-blue/50 bg-void-black flex flex-col items-center justify-center gap-1 cursor-pointer transition-colors text-text-muted hover:text-neon-blue focus:outline-none focus:border-neon-blue"
            >
              {uploading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Camera className="w-5 h-5" aria-hidden="true" />
                  <span className="text-[10px] font-bold">Upload</span>
                </>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                disabled={uploading}
                tabIndex={-1} // Handled by label container
                className="hidden"
              />
            </label>
          )}
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={submitting || uploading}
        aria-busy={submitting || uploading}
        className="w-full p-3.5 rounded-lg bg-panel-charcoal hover:bg-void-black border border-neon-blue/40 text-neon-blue font-bold text-sm glow-blue-hover transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
      >
        {submitting ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" /> Submitting...
          </>
        ) : (
          "SUBMIT FOR APPROVAL"
        )}
      </button>
    </form>
  );
};
