import React, { useState } from 'react';
import AIPreviewPanel from './components/AIPreviewPanel';

// Category schema definition from Module 2 (Mock data)
const CATEGORY_SCHEMA = {
  id: "cat_neon_signs_101",
  name: "Neon Sign",
  attributes: [
    { key: "custom_text", label: "Custom Neon Text", type: "text", affects_ai_preview: true, default_value: "Dream Big" },
    { key: "color", label: "Neon Glow Color", type: "radio", affects_ai_preview: true },
    { key: "font", label: "Font Style", type: "select", affects_ai_preview: true },
    { key: "mounting", label: "Mounting Options", type: "radio", affects_ai_preview: true },
    { key: "backing", label: "Backing Board Material", type: "radio", affects_ai_preview: false }
  ],
  ai_prompt_template: 'A realistic professional product photo of a custom {category_name} spelling "{custom_text}", in {color} color, {font} font style, {mounting} hanging, mounted on a dark background with soft ambient glow, studio lighting, high detail, no watermark, no text overlay'
};

export default function App() {
  const [selectedAttributes, setSelectedAttributes] = useState({
    custom_text: "Dream Big",
    color: "blue",
    font: "cursive",
    mounting: "chain",
    backing: "acrylic"
  });

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleAttributeChange = (key, value) => {
    setSelectedAttributes(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <header style={{ marginBottom: '2rem', borderBottom: '1px solid #333', paddingBottom: '1rem' }}>
        <h1 style={{ color: '#fff', fontSize: '2rem', margin: 0 }}>GALXY React Component Verification</h1>
        <p style={{ color: '#999', margin: '0.5rem 0 0' }}>Verifying build integrity of AIPreviewPanel (m5_Frontend1)</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        
        {/* Left Side: Mount AIPreviewPanel */}
        <div>
          <h2 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '1rem' }}>Mount State</h2>
          <AIPreviewPanel
            category={CATEGORY_SCHEMA}
            selectedAttributes={selectedAttributes}
            user={isLoggedIn ? { id: 'usr_123', name: 'Sawthi' } : null}
            defaultProductImage="assets/neon_default.png"
          />
        </div>

        {/* Right Side: Simple Configurator Controller */}
        <div style={{ background: '#121826', padding: '1.5rem', borderRadius: '8px', border: '1px solid #333' }}>
          <h2 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '1.5rem' }}>React Configurator Simulator</h2>
          
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', color: '#ccc', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Custom Text</label>
            <input 
              type="text" 
              value={selectedAttributes.custom_text}
              onChange={(e) => handleAttributeChange('custom_text', e.target.value)}
              style={{ width: '100%', padding: '0.5rem', background: '#222', border: '1px solid #444', color: '#fff', borderRadius: '4px' }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', color: '#ccc', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Neon Color</label>
            <select 
              value={selectedAttributes.color}
              onChange={(e) => handleAttributeChange('color', e.target.value)}
              style={{ width: '100%', padding: '0.5rem', background: '#222', border: '1px solid #444', color: '#fff', borderRadius: '4px' }}
            >
              <option value="blue">Electric Blue</option>
              <option value="pink">Neon Pink</option>
              <option value="gold">Warm Gold</option>
            </select>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', color: '#ccc', fontSize: '0.9rem', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={isLoggedIn}
                onChange={(e) => setIsLoggedIn(e.target.checked)}
                style={{ marginRight: '0.5rem' }}
              />
              Logged in user state
            </label>
          </div>
          
          <p style={{ color: '#666', fontSize: '0.8rem', lineHeight: '1.4', borderTop: '1px solid #222', paddingTop: '1rem' }}>
            Changing these attributes in React triggers the internal state updates, auto tab shifts, and stale banners inside the React <code>AIPreviewPanel</code> component.
          </p>
        </div>

      </div>
    </div>
  );
}
