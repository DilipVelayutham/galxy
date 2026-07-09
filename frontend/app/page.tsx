"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { TestimonialSection } from "@/components/reviews/TestimonialSection";
import Link from "next/link";
import { Sparkles, ShoppingBag, Eye, ArrowRight, PhoneCall, ShieldCheck } from "lucide-react";

interface Category {
  _id: string;
  slug: string;
  name: string;
  description: string;
  cover_image: string;
  accent_color: string;
}

interface HeroContent {
  title: string;
  tagline: string;
  description: string;
  cta_text: string;
  cta_link: string;
}

export default function Home() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [hero, setHero] = useState<HeroContent>({
    title: "GALXY STUDIO",
    tagline: "CUSTOM LIGHTING & CRAFT WORK",
    description: "Design bespoke glowing neon signs, paper quilled art frames, and acrylic night lamps engineered to order with real-time AI previews.",
    cta_text: "START CONFIGURING",
    cta_link: "#categories-section",
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch CMS Hero Content
        const heroRes = await api.get("/site-content/hero");
        if (heroRes.success && heroRes.data) {
          setHero(heroRes.data);
        }
        
        // Fetch Categories
        const catRes = await api.get("/categories");
        if (catRes.success && catRes.data) {
          setCategories(catRes.data);
        }
      } catch (err) {
        console.error("Failed to load storefront data", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const getAccentBorderClass = (color: string) => {
    switch (color) {
      case "pink": return "hover:border-[#FF2E8A]/50 hover:glow-pink-hover";
      case "blue": return "hover:border-[#18E7FF]/50 hover:glow-blue-hover";
      case "violet": return "hover:border-[#9B5CFF]/50 hover:glow-violet-hover";
      case "yellow": return "hover:border-[#FFD84D]/50 hover:glow-yellow-hover";
      default: return "hover:border-neon-blue/40";
    }
  };

  const getAccentTextClass = (color: string) => {
    switch (color) {
      case "pink": return "text-[#FF2E8A]";
      case "blue": return "text-[#18E7FF]";
      case "violet": return "text-[#9B5CFF]";
      case "yellow": return "text-[#FFD84D]";
      default: return "text-neon-blue";
    }
  };

  return (
    <div className="min-h-screen bg-void-black flex flex-col selection:bg-neon-pink selection:text-void-black">
      {/* Navigation Header */}
      <header className="sticky top-0 z-40 bg-void-black/70 backdrop-blur-md border-b border-panel-charcoal">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="text-xl font-extrabold tracking-wider text-text-primary flex items-center gap-1.5 cursor-pointer">
            <span className="text-neon-blue text-glow-blue animate-flicker">GAL</span>
            <span className="text-neon-pink text-glow-pink">XY</span>
          </Link>
          
          <nav className="flex items-center gap-6 text-sm font-semibold">
            <Link href="#categories-section" className="text-text-muted hover:text-text-primary transition-colors cursor-pointer">
              Shop Categories
            </Link>
            <Link href="/gallery" className="text-text-muted hover:text-text-primary transition-colors cursor-pointer">
              Gallery
            </Link>
            <Link href="/login" className="px-4 py-2 rounded-lg bg-panel-charcoal border border-panel-charcoal/50 text-text-primary text-xs hover:border-neon-blue/40 hover:glow-blue-hover transition-all cursor-pointer">
              Account Login
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-24 sm:py-32 overflow-hidden flex-1 flex flex-col justify-center">
        {/* Neon Background Gradients */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-neon-blue/10 to-neon-violet/0 blur-[140px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full bg-gradient-to-tr from-neon-pink/10 to-neon-yellow/0 blur-[140px] pointer-events-none" />
        
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          {/* Tagline */}
          <span className="text-xs sm:text-sm font-extrabold tracking-widest text-neon-blue text-glow-blue uppercase">
            {hero.tagline}
          </span>
          
          {/* Main Title with Power-on Flicker Effect */}
          <h1 className="mt-6 text-5xl sm:text-7xl font-black text-text-primary tracking-tight uppercase leading-none">
            {hero.title.split(" ").map((word, idx) => (
              <span key={idx} className={idx % 2 === 1 ? "text-neon-pink text-glow-pink animate-flicker" : ""}>
                {word}{" "}
              </span>
            ))}
          </h1>
          
          {/* Description */}
          <p className="mt-8 text-sm sm:text-base text-text-muted max-w-2xl mx-auto leading-relaxed">
            {hero.description}
          </p>
          
          {/* CTA Button */}
          <div className="mt-10 flex justify-center">
            <Link
              href={hero.cta_link}
              className="px-8 py-4 rounded-xl bg-panel-charcoal hover:bg-void-black border border-neon-blue text-neon-blue font-extrabold text-sm tracking-wider glow-blue hover:glow-blue-hover scale-100 hover:scale-[1.03] transition-all cursor-pointer flex items-center gap-2"
            >
              {hero.cta_text} <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Categories Grid Section */}
      <section id="categories-section" className="py-20 bg-panel-charcoal/20 border-t border-b border-panel-charcoal">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-text-primary">
              Browse Custom <span className="text-neon-blue text-glow-blue">Categories</span>
            </h2>
            <p className="text-xs sm:text-sm text-text-muted mt-2">
              Select a craft category to build, price, and preview your bespoke design attribute by attribute.
            </p>
          </div>

          {loading ? (
            <div className="py-12 text-center text-text-muted text-sm">Loading categories...</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {categories.map((cat) => (
                <div
                  key={cat._id}
                  className={`rounded-2xl overflow-hidden bg-panel-charcoal/40 border border-panel-charcoal flex flex-col h-full transition-all duration-300 ${getAccentBorderClass(
                    cat.accent_color
                  )}`}
                >
                  {/* Category Image */}
                  <div className="h-44 relative bg-void-black">
                    <img
                      src={cat.cover_image}
                      alt={cat.name}
                      className="w-full h-full object-cover opacity-80"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-void-black/90 to-transparent" />
                  </div>
                  
                  {/* Category Info */}
                  <div className="p-5 flex-1 flex flex-col justify-between gap-4">
                    <div>
                      <h3 className="text-base font-bold text-text-primary">{cat.name}</h3>
                      <p className="text-xs text-text-muted mt-2 leading-relaxed">{cat.description}</p>
                    </div>
                    
                    <Link
                      href={`/categories/${cat.slug}`}
                      className={`text-xs font-bold flex items-center gap-1.5 tracking-wider cursor-pointer ${getAccentTextClass(
                        cat.accent_color
                      )} hover:opacity-80 transition-opacity`}
                    >
                      START CUSTOMIZING <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Testimonials */}
      <TestimonialSection />

      {/* WhatsApp Conversion Section */}
      <section className="py-16 border-t border-panel-charcoal bg-void-black text-center relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-neon-yellow/5 blur-[80px] pointer-events-none" />
        <div className="max-w-xl mx-auto px-6 relative z-10 flex flex-col items-center gap-5">
          <ShieldCheck className="w-12 h-12 text-neon-yellow drop-shadow-[0_0_8px_#FFD84D]" />
          <h2 className="text-2xl font-extrabold text-text-primary uppercase tracking-tight">
            How inquiries work at <span className="text-neon-yellow text-glow-yellow">GALXY</span>
          </h2>
          <p className="text-xs sm:text-sm text-text-muted leading-relaxed">
            There are no instant online payment gateways here. After configuring and submitting your design, Asil personally reviews details, calculates shipping, sends a finalized price quote, and confirms orders offline.
          </p>
          <a
            href="https://wa.me/919840123456"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 px-6 py-3 rounded-lg bg-panel-charcoal hover:bg-void-black border border-neon-yellow text-neon-yellow font-bold text-xs glow-yellow-hover transition-all flex items-center gap-2 cursor-pointer"
          >
            <PhoneCall className="w-4 h-4" /> CHAT WITH ASIL ON WHATSAPP
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-void-black border-t border-panel-charcoal text-center text-xs text-text-muted">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 GALXY Studio. Handcrafted in India.</p>
          <div className="flex gap-6">
            <Link href="/terms" className="hover:text-text-primary transition-colors cursor-pointer">Terms of Inquiry</Link>
            <Link href="/privacy" className="hover:text-text-primary transition-colors cursor-pointer">Privacy Policy</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
