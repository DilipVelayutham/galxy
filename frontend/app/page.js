'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';

// SVG Preset Paths & Elements
const PRESETS = {
  lamp: {
    name: "Nebula Lamp",
    svg: (glowColor) => (
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="40" r="28" stroke={glowColor} strokeWidth="2.5" strokeDasharray="4 2" />
        <circle cx="50" cy="40" r="20" stroke={glowColor} strokeWidth="1.5" />
        <path d="M50 12V2" stroke={glowColor} strokeWidth="2" strokeLinecap="round" />
        <path d="M50 68V95" stroke={glowColor} strokeWidth="3" strokeLinecap="round" />
        <rect x="42" y="90" width="16" height="5" rx="2" fill={glowColor} />
        <circle cx="50" cy="40" r="6" fill={glowColor} opacity="0.8" style={{ filter: `drop-shadow(0 0 8px ${glowColor})` }} />
      </svg>
    )
  },
  orb: {
    name: "Gravity Orb",
    svg: (glowColor) => (
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="24" stroke={glowColor} strokeWidth="3" style={{ filter: `drop-shadow(0 0 12px ${glowColor})` }} fill="rgba(255,255,255,0.03)" />
        <ellipse cx="50" cy="50" rx="38" ry="12" stroke={glowColor} strokeWidth="1.5" transform="rotate(-20 50 50)" strokeDasharray="5 3" />
        <ellipse cx="50" cy="50" rx="34" ry="8" stroke={glowColor} strokeWidth="1" transform="rotate(30 50 50)" />
        <circle cx="30" cy="30" r="3" fill={glowColor} />
        <circle cx="72" cy="65" r="2" fill={glowColor} />
      </svg>
    )
  },
  helmet: {
    name: "Quantum Helmet",
    svg: (glowColor) => (
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 45C22 28.5 34.5 16 50 16C65.5 16 78 28.5 78 45C78 54.5 74 62.5 68 67.5V76C68 79.5 65 82 61.5 82H38.5C35 82 32 79.5 32 76V67.5C26 62.5 22 54.5 22 45Z" stroke={glowColor} strokeWidth="2.5" fill="rgba(255,255,255,0.01)" />
        <path d="M28 45C28 32.8 37.8 23 50 23C62.2 23 72 32.8 72 45C72 49 70 55 65 59H35C30 55 28 49 28 45Z" fill={glowColor} opacity="0.25" stroke={glowColor} strokeWidth="1.5" />
        <rect x="40" y="65" width="20" height="4" rx="2" fill={glowColor} opacity="0.6" />
        <line x1="32" y1="82" x2="22" y2="92" stroke={glowColor} strokeWidth="2" strokeLinecap="round" />
        <line x1="68" y1="82" x2="78" y2="92" stroke={glowColor} strokeWidth="2" strokeLinecap="round" />
      </svg>
    )
  },
  ring: {
    name: "Infinity Ring",
    svg: (glowColor) => (
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 20C28 20 20 35 20 50C20 65 28 80 50 80C72 80 80 65 80 50C80 35 72 20 50 20Z" stroke={glowColor} strokeWidth="2.5" />
        <path d="M20 50C20 58 24 72 42 75C60 78 72 65 80 50C72 42 60 22 42 25C24 28 20 42 20 50Z" stroke={glowColor} strokeWidth="1.5" strokeDasharray="3 3" />
        <circle cx="50" cy="50" r="10" stroke={glowColor} strokeWidth="2" />
      </svg>
    )
  }
};

const COLOR_PRESETS = [
  { name: "Cyber Cyan", value: "#00f3ff", extra: 0.0 },
  { name: "Magic Magenta", value: "#ff0055", extra: 15.0 },
  { name: "Krypton Green", value: "#00ff66", extra: 10.0 },
  { name: "Helium Orange", value: "#ff9900", extra: 12.0 },
  { name: "Electric Blue", value: "#0066ff", extra: 5.0 }
];

export default function Home() {
  const [activeTab, setActiveTab] = useState('customizer'); // 'customizer' or 'admin'
  const [selectedPreset, setSelectedPreset] = useState('lamp');
  const [size, setSize] = useState(100); // 50 to 150%
  const [glowColor, setGlowColor] = useState('#00f3ff');
  const [designText, setDesignText] = useState('GALXY');
  const [floatIntensity, setFloatIntensity] = useState(5); // 0 to 10
  const [rotationAngle, setRotationAngle] = useState(0); // -180 to 180 deg
  const [price, setPrice] = useState(99.0);
  
  // Admin Data
  const [savedConfigs, setSavedConfigs] = useState([]);
  const [adminSettings, setAdminSettings] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  // Toast
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

  // 3D Parallax Tilt Effects
  const previewRef = useRef(null);
  const tiltX = useMotionValue(0);
  const tiltY = useMotionValue(0);
  
  const rotateX = useTransform(tiltY, [-200, 200], [15, -15]);
  const rotateY = useTransform(tiltX, [-200, 200], [-15, 15]);

  const handleMouseMove = (e) => {
    if (!previewRef.current) return;
    const rect = previewRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    tiltX.set(x);
    tiltY.set(y);
  };

  const handleMouseLeave = () => {
    tiltX.set(0);
    tiltY.set(0);
  };

  // Toast Trigger
  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Fetch API Base URL
  const API_URL = 'http://localhost:5000/api';

  // Fetch Pricing settings & Saved configurations
  const loadAdminData = async () => {
    try {
      const settingsRes = await fetch(`${API_URL}/admin/settings`);
      const settingsData = await settingsRes.json();
      if (settingsData.success) {
        setAdminSettings(settingsData.settings);
      }

      const configRes = await fetch(`${API_URL}/config`);
      const configData = await configRes.json();
      if (configData.success) {
        setSavedConfigs(configData.configurations);
      }
    } catch (e) {
      console.warn("Failed to contact backend API. Running in local fallback demo mode.", e);
    }
  };

  // Real-time Pricing Fetch
  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const res = await fetch(`${API_URL}/price`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            size,
            glow_color: glowColor,
            design_text: designText,
            float_intensity: floatIntensity
          })
        });
        const data = await res.json();
        if (data.success) {
          setPrice(data.price);
        }
      } catch (e) {
        // Fallback calculations in React if API is down
        let computed = 99.0;
        if (adminSettings) {
          computed = adminSettings.base_price;
          if (size > 100) {
            computed += (size - 100) * adminSettings.size_price_per_percent;
          }
          // check color extra
          const normColor = glowColor.toLowerCase();
          let colorCost = 0.0;
          for (const [key, val] of Object.entries(adminSettings.color_prices)) {
            if (key.toLowerCase() === normColor) {
              colorCost = val;
              break;
            }
          }
          computed += colorCost;
          computed += designText.length * adminSettings.text_price_per_char;
          computed += floatIntensity * adminSettings.float_price_per_level;
        } else {
          // Static local fallback math
          if (size > 100) computed += (size - 100) * 1.0;
          const foundPreset = COLOR_PRESETS.find(c => c.value === glowColor);
          if (foundPreset) computed += foundPreset.extra;
          computed += designText.length * 2.0;
          computed += floatIntensity * 5.0;
        }
        setPrice(Math.round(computed * 100) / 100);
      }
    };

    const timer = setTimeout(fetchPrice, 150); // Debounced price fetching
    return () => clearTimeout(timer);
  }, [size, glowColor, designText, floatIntensity, adminSettings]);

  useEffect(() => {
    loadAdminData();
  }, [activeTab]);

  // Save Configuration
  const handleSaveConfig = async () => {
    setIsSaving(true);
    const newConfig = {
      preset: selectedPreset,
      preset_name: PRESETS[selectedPreset].name,
      size,
      glow_color: glowColor,
      design_text: designText,
      float_intensity: floatIntensity,
      rotation_angle: rotationAngle,
      price
    };

    try {
      const res = await fetch(`${API_URL}/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      const data = await res.json();
      if (data.success) {
        triggerToast("Configuration saved successfully!");
        // Refresh configs list
        setSavedConfigs(prev => [data.configuration, ...prev]);
      } else {
        triggerToast("Failed to save configuration.");
      }
    } catch (e) {
      // Local fallback saving for offline mode
      const mockSaved = { ...newConfig, id: Math.random().toString(36).substr(2, 9) };
      setSavedConfigs(prev => [mockSaved, ...prev]);
      triggerToast("Saved configuration locally (Offline Fallback)!");
    } finally {
      setIsSaving(false);
    }
  };

  // Delete Configuration
  const handleDeleteConfig = async (id) => {
    try {
      const res = await fetch(`${API_URL}/config/${id}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (data.success) {
        setSavedConfigs(prev => prev.filter(c => c.id !== id));
        triggerToast("Design deleted.");
      }
    } catch (e) {
      setSavedConfigs(prev => prev.filter(c => c.id !== id));
      triggerToast("Deleted local entry.");
    }
  };

  // Update Settings from Admin Panel
  const handleUpdateSettings = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const updated = {
      base_price: parseFloat(formData.get('base_price')),
      size_price_per_percent: parseFloat(formData.get('size_price_per_percent')),
      text_price_per_char: parseFloat(formData.get('text_price_per_char')),
      float_price_per_level: parseFloat(formData.get('float_price_per_level')),
      color_prices: {
        "#00f3ff": parseFloat(formData.get('color_cyan')),
        "#ff0055": parseFloat(formData.get('color_magenta')),
        "#00ff66": parseFloat(formData.get('color_green')),
        "#ff9900": parseFloat(formData.get('color_orange')),
        "#0066ff": parseFloat(formData.get('color_blue'))
      }
    };

    try {
      const res = await fetch(`${API_URL}/admin/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updated)
      });
      const data = await res.json();
      if (data.success) {
        setAdminSettings(data.settings);
        triggerToast("Pricing matrices updated successfully!");
      }
    } catch (e) {
      setAdminSettings(updated);
      triggerToast("Updated settings locally!");
    }
  };

  // Floating speed mapping (higher intensity floats faster)
  const floatDuration = floatIntensity > 0 ? (3.5 - (floatIntensity * 0.2)) : 0;
  
  // Glow style formatting
  const shadowGlow = `0 0 25px ${glowColor}, 0 0 50px ${glowColor}44`;

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="brand-logo">
          GALXY
        </div>
        <nav className="nav-links">
          <button 
            className={`nav-btn ${activeTab === 'customizer' ? 'active' : ''}`}
            onClick={() => setActiveTab('customizer')}
          >
            Customizer
          </button>
          <button 
            className={`nav-btn ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => setActiveTab('admin')}
          >
            Admin Panel
          </button>
        </nav>
      </header>

      {activeTab === 'customizer' ? (
        <div className="dashboard-grid">
          {/* Live Preview Area */}
          <div 
            className="preview-card" 
            ref={previewRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{ '--glow-color-glow': `${glowColor}1c` }}
          >
            <div className="preview-mesh"></div>
            
            <div className="floating-container">
              <motion.div
                className="product-wrapper"
                animate={{
                  y: floatIntensity > 0 ? [0, -floatIntensity * 3.5, 0] : 0
                }}
                transition={{
                  y: floatIntensity > 0 ? {
                    duration: floatDuration,
                    repeat: Infinity,
                    ease: "easeInOut"
                  } : {}
                }}
                style={{
                  rotateX: rotateX,
                  rotateY: rotateY,
                  transformStyle: 'preserve-3d',
                }}
              >
                <motion.div
                  className="product-art"
                  animate={{
                    rotateY: rotationAngle,
                    scale: size / 100
                  }}
                  transition={{
                    type: "spring",
                    stiffness: 90,
                    damping: 15
                  }}
                  style={{
                    filter: `drop-shadow(0 0 20px ${glowColor})`,
                    transformStyle: 'preserve-3d'
                  }}
                >
                  {PRESETS[selectedPreset].svg(glowColor)}
                  
                  {designText && (
                    <div 
                      className="product-text-overlay"
                      style={{
                        color: '#ffffff',
                        textShadow: `0 0 8px ${glowColor}, 0 0 15px ${glowColor}aa`,
                      }}
                    >
                      {designText}
                    </div>
                  )}
                </motion.div>
              </motion.div>
            </div>

            {/* Glowing Shadow Ring underneath */}
            <motion.div 
              className="glow-shadow-ring"
              animate={{
                scale: floatIntensity > 0 ? [1, 0.8, 1] : 1,
                opacity: floatIntensity > 0 ? [0.6, 0.35, 0.6] : 0.6
              }}
              transition={{
                duration: floatDuration,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              style={{
                '--glow-color-glow': glowColor
              }}
            />
            
            <div className="product-label">
              Suspended {PRESETS[selectedPreset].name}
            </div>
          </div>

          {/* Configuration Controls Sidebar */}
          <div className="customizer-panel">
            <div>
              <h2 className="section-title">
                Configure Design
                <span className="section-title-badge">Active</span>
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Design a custom high-performance floating neon showcase module.
              </p>
            </div>

            {/* Choose Base Preset */}
            <div className="option-group">
              <div className="option-label">
                Select Decor Shape
                <span className="option-value">{PRESETS[selectedPreset].name}</span>
              </div>
              <div className="product-presets">
                {Object.entries(PRESETS).map(([key, item]) => (
                  <button
                    key={key}
                    className={`preset-btn ${selectedPreset === key ? 'active' : ''}`}
                    onClick={() => setSelectedPreset(key)}
                  >
                    <div style={{ width: '28px', height: '28px' }}>
                      {key === 'lamp' && (
                        <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="8" r="6" /><rect x="11" y="14" width="2" height="8" /></svg>
                      )}
                      {key === 'orb' && (
                        <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="7" /><circle cx="12" cy="12" r="10" stroke="currentColor" fill="none" strokeWidth="1" /></svg>
                      )}
                      {key === 'helmet' && (
                        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>
                      )}
                      {key === 'ring' && (
                        <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="9" stroke="currentColor" fill="none" strokeWidth="3"/></svg>
                      )}
                    </div>
                    {item.name.split(' ')[0]}
                  </button>
                ))}
              </div>
            </div>

            {/* Select Glow Color */}
            <div className="option-group">
              <div className="option-label">
                Neon Glow Color
                <span className="option-value" style={{ color: glowColor }}>
                  {COLOR_PRESETS.find(c => c.value === glowColor)?.name || "Custom"}
                </span>
              </div>
              <div className="color-swatches">
                {COLOR_PRESETS.map((preset) => (
                  <div
                    key={preset.value}
                    className={`swatch ${glowColor === preset.value ? 'active' : ''}`}
                    style={{ 
                      backgroundColor: preset.value,
                      '--swatch-color': preset.value
                    }}
                    onClick={() => setGlowColor(preset.value)}
                    title={`${preset.name} (${preset.extra > 0 ? `+$${preset.extra}` : 'Included'})`}
                  />
                ))}
              </div>
            </div>

            {/* Custom Overlay Text */}
            <div className="option-group">
              <div className="option-label">
                Custom Engraving / Design Text
                <span className="option-value">{designText.length} Chars</span>
              </div>
              <input
                type="text"
                className="text-input-field"
                value={designText}
                onChange={(e) => setDesignText(e.target.value.toUpperCase().slice(0, 12))}
                placeholder="ENTER ENGRAVING TEXT"
              />
            </div>

            {/* Product Size */}
            <div className="option-group">
              <div className="option-label">
                Product Scale Dimensions
                <span className="option-value">{size}%</span>
              </div>
              <input
                type="range"
                className="slider-input"
                min="50"
                max="150"
                value={size}
                style={{ '--accent-color': glowColor }}
                onChange={(e) => setSize(parseInt(e.target.value))}
              />
            </div>

            {/* Rotation Angle */}
            <div className="option-group">
              <div className="option-label">
                Yaw Rotation Angle
                <span className="option-value">{rotationAngle}°</span>
              </div>
              <input
                type="range"
                className="slider-input"
                min="-180"
                max="180"
                value={rotationAngle}
                style={{ '--accent-color': glowColor }}
                onChange={(e) => setRotationAngle(parseInt(e.target.value))}
              />
            </div>

            {/* Floating Height / Intensity */}
            <div className="option-group">
              <div className="option-label">
                Floating Height & Frequency
                <span className="option-value">Level {floatIntensity}</span>
              </div>
              <input
                type="range"
                className="slider-input"
                min="0"
                max="10"
                value={floatIntensity}
                style={{ '--accent-color': glowColor }}
                onChange={(e) => setFloatIntensity(parseInt(e.target.value))}
              />
            </div>

            {/* Pricing Section */}
            <div className="pricing-box">
              <div className="price-details">
                <span className="price-title">Dynamic Price Quote</span>
                <span className="price-amount">{price.toFixed(2)}</span>
              </div>
              <button 
                className="action-btn"
                onClick={handleSaveConfig}
                disabled={isSaving}
                style={{
                  background: `linear-gradient(135deg, ${glowColor} 0%, #0044ff 100%)`,
                  boxShadow: `0 0 20px ${glowColor}44`
                }}
              >
                {isSaving ? "Saving..." : "Save Design"}
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Admin Dashboard View */
        <div className="admin-container">
          <div className="admin-grid">
            {/* Saved Customer Configurations */}
            <div className="admin-card">
              <h2 className="section-title">Saved Configurations</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                Manage design visualizations sent in by customers.
              </p>
              
              <div className="admin-table-container">
                {savedConfigs.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', padding: '1rem 0' }}>No saved configurations found.</p>
                ) : (
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>Text</th>
                        <th>Glow</th>
                        <th>Float</th>
                        <th>Price</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {savedConfigs.map((config) => (
                        <tr key={config.id}>
                          <td style={{ fontWeight: 600 }}>{config.preset_name} ({config.size}%)</td>
                          <td><code>{config.design_text || '-'}</code></td>
                          <td>
                            <span style={{ 
                              display: 'inline-block',
                              width: '12px',
                              height: '12px',
                              borderRadius: '50%',
                              backgroundColor: config.glow_color,
                              marginRight: '0.5rem',
                              verticalAlign: 'middle',
                              boxShadow: `0 0 5px ${config.glow_color}`
                            }} />
                            {config.glow_color}
                          </td>
                          <td>Lvl {config.float_intensity}</td>
                          <td style={{ fontWeight: 700, color: 'var(--accent-color)' }}>${config.price?.toFixed(2)}</td>
                          <td>
                            <button 
                              className="admin-delete-btn"
                              onClick={() => handleDeleteConfig(config.id)}
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            {/* Pricing Parameters & Multipliers */}
            <div className="admin-card">
              <h2 className="section-title">Pricing Matrix Manager</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Adjust variables used in backend API dynamic pricing updates.
              </p>

              <form className="settings-form" onSubmit={handleUpdateSettings}>
                <div className="settings-row">
                  <span style={{ fontWeight: 500 }}>Base Floating Product Price</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="base_price" 
                      className="settings-input"
                      defaultValue={adminSettings?.base_price ?? 99.0}
                    />
                  </div>
                </div>

                <div className="settings-row">
                  <span style={{ fontWeight: 500 }}>Dimension Cost (per % above 100%)</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="size_price_per_percent" 
                      className="settings-input"
                      defaultValue={adminSettings?.size_price_per_percent ?? 1.0}
                    />
                  </div>
                </div>

                <div className="settings-row">
                  <span style={{ fontWeight: 500 }}>Engraving Cost (per letter)</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="text_price_per_char" 
                      className="settings-input"
                      defaultValue={adminSettings?.text_price_per_char ?? 2.0}
                    />
                  </div>
                </div>

                <div className="settings-row">
                  <span style={{ fontWeight: 500 }}>Floating Lift Cost (per level)</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="float_price_per_level" 
                      className="settings-input"
                      defaultValue={adminSettings?.float_price_per_level ?? 5.0}
                    />
                  </div>
                </div>

                <h3 style={{ fontSize: '1rem', marginTop: '0.8rem', borderBottom: '1px solid var(--panel-border)', paddingBottom: '0.5rem' }}>
                  Glow Premium Modifiers
                </h3>

                <div className="settings-row">
                  <span>Cyber Cyan Color Cost</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="color_cyan" 
                      className="settings-input"
                      defaultValue={adminSettings?.color_prices?.["#00f3ff"] ?? 0.0}
                    />
                  </div>
                </div>

                <div className="settings-row">
                  <span>Magic Magenta Color Cost</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="color_magenta" 
                      className="settings-input"
                      defaultValue={adminSettings?.color_prices?.["#ff0055"] ?? 15.0}
                    />
                  </div>
                </div>

                <div className="settings-row">
                  <span>Krypton Green Color Cost</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="color_green" 
                      className="settings-input"
                      defaultValue={adminSettings?.color_prices?.["#00ff66"] ?? 10.0}
                    />
                  </div>
                </div>

                <div className="settings-row">
                  <span>Helium Orange Color Cost</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="color_orange" 
                      className="settings-input"
                      defaultValue={adminSettings?.color_prices?.["#ff9900"] ?? 12.0}
                    />
                  </div>
                </div>

                <div className="settings-row">
                  <span>Electric Blue Color Cost</span>
                  <div className="settings-input-group">
                    <span>$</span>
                    <input 
                      type="number" 
                      step="0.01" 
                      name="color_blue" 
                      className="settings-input"
                      defaultValue={adminSettings?.color_prices?.["#0066ff"] ?? 5.0}
                    />
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="action-btn"
                  style={{
                    marginTop: '1rem',
                    background: 'linear-gradient(135deg, #00ff66 0%, #0099ff 100%)',
                    boxShadow: '0 0 20px rgba(0, 255, 102, 0.15)'
                  }}
                >
                  Save Settings Matrix
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Dynamic Floating Toast System */}
      <div className={`toast ${showToast ? 'show' : ''}`}>
        <span className="toast-success-icon">✓</span>
        <span>{toastMessage}</span>
      </div>
    </div>
  );
}
