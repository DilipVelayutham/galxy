// Category schema definition from Module 2 (Mock data)
const CATEGORY_SCHEMA = {
  id: "cat_neon_signs_101",
  name: "Neon Sign",
  attributes: [
    { key: "custom_text", label: "Custom Neon Text", type: "text", affects_ai_preview: true },
    { key: "color", label: "Neon Glow Color", type: "radio", affects_ai_preview: true },
    { key: "font", label: "Font Style", type: "select", affects_ai_preview: true },
    { key: "mounting", label: "Mounting Options", type: "radio", affects_ai_preview: true },
    { key: "backing", label: "Backing Board Material", type: "radio", affects_ai_preview: false } // Backing does NOT affect preview
  ],
  ai_prompt_template: 'A realistic professional product photo of a custom {category_name} spelling "{custom_text}", in {color} color, {font} font style, {mounting} hanging, mounted on a dark background with soft ambient glow, studio lighting, high detail, no watermark, no text overlay'
};

// Mock generated preview images database corresponding to colors
const PREVIEW_ASSETS = {
  blue: "assets/neon_blue.png",
  pink: "assets/neon_pink.png",
  gold: "assets/neon_gold.png"
};

// Core application state
let appState = {
  selectedAttributes: {
    custom_text: "Dream Big",
    color: "blue",
    font: "cursive",
    mounting: "chain",
    backing: "acrylic"
  },
  lastGeneratedAttributes: null, // Holds the attributes of the current successful preview
  isFirstAttributeChange: true, // Auto-switch tab flag
  currentPreviewUrl: null,
  currentGenerationId: null,
  activeTab: "photos", // "photos" or "preview"
  
  // Rate limiting simulation variables
  isLoggedIn: false,
  guestQuotaRemaining: 5,
  userQuotaRemaining: 20,
  
  // Cache storage
  cache: new Map() // maps cache key (string hash) to output_image_url
};

// Guest session ID tracking
let guestSessionId = localStorage.getItem("galaxy_guest_session_id");
if (!guestSessionId) {
  guestSessionId = 'guest_sess_' + Math.random().toString(36).substring(2, 15);
  localStorage.setItem("galaxy_guest_session_id", guestSessionId);
}

// DOM Elements
const elements = {
  tabPhotos: document.getElementById("tab-photos"),
  tabPreview: document.getElementById("tab-preview"),
  panelPhotos: document.getElementById("panel-photos"),
  panelPreview: document.getElementById("panel-preview"),
  
  // AI Preview States
  stateInitial: document.getElementById("ai-state-initial"),
  stateLoading: document.getElementById("ai-state-loading"),
  stateSuccess: document.getElementById("ai-state-success"),
  stateError: document.getElementById("ai-state-error"),
  
  previewImage: document.getElementById("ai-preview-image"),
  previewImageWrapper: document.querySelector(".preview-image-wrapper"),
  staleBanner: document.getElementById("ai-stale-banner"),
  cacheBadge: document.getElementById("cache-badge"),
  errorTitle: document.getElementById("error-title"),
  errorMessage: document.getElementById("error-message"),
  
  // Buttons
  btnRegenerate: document.getElementById("btn-regenerate"),
  btnRegenerateStale: document.getElementById("btn-regenerate-stale"),
  btnErrorRetry: document.getElementById("btn-error-retry"),
  
  // Config inputs
  inputCustomText: document.getElementById("input-custom-text"),
  selectFont: document.getElementById("select-font"),
  configForm: document.getElementById("configurator-form"),
  
  // Simulator inputs
  simAuthToggle: document.getElementById("sim-auth-toggle"),
  simCurrentRole: document.getElementById("sim-current-role"),
  simQuotaValue: document.getElementById("sim-quota-value"),
  btnResetQuota: document.getElementById("btn-reset-quota"),
  simLatency: document.getElementById("sim-latency"),
  lblLatency: document.getElementById("lbl-latency"),
  btnClearLogs: document.getElementById("btn-clear-logs"),
  logsOutput: document.getElementById("sim-logs-output")
};

/* Terminal Logging Utility */
function logEvent(source, message, isError = false) {
  const timestamp = new Date().toLocaleTimeString();
  const color = isError ? "#ef4444" : "#10B981";
  const logLine = `\n[${timestamp}] [${source}] ${message}`;
  
  elements.logsOutput.innerHTML += `<span style="color: ${color}">${logLine}</span>`;
  elements.logsOutput.scrollTop = elements.logsOutput.scrollHeight;
}

/* Tab Management */
function switchTab(tabName) {
  appState.activeTab = tabName;
  if (tabName === "photos") {
    elements.tabPhotos.classList.add("active");
    elements.tabPhotos.setAttribute("aria-selected", "true");
    elements.tabPreview.classList.remove("active");
    elements.tabPreview.setAttribute("aria-selected", "false");
    
    elements.panelPhotos.classList.add("active");
    elements.panelPreview.classList.remove("active");
    logEvent("UI", "Switched tab to 'Product Photos'");
  } else {
    elements.tabPreview.classList.add("active");
    elements.tabPreview.setAttribute("aria-selected", "true");
    elements.tabPhotos.classList.remove("active");
    elements.tabPhotos.setAttribute("aria-selected", "false");
    
    elements.panelPreview.classList.add("active");
    elements.panelPhotos.classList.remove("active");
    logEvent("UI", "Switched tab to 'AI Preview'");
    
    // If AI Preview is active and we are in the initial state, trigger first generation
    if (elements.stateInitial.classList.contains("active") || !elements.stateInitial.classList.contains("hidden")) {
      generatePreview();
    }
  }
}

elements.tabPhotos.addEventListener("click", () => switchTab("photos"));
elements.tabPreview.addEventListener("click", () => switchTab("preview"));

/* Attribute Handler */
function updateSelectedAttributes() {
  const previousText = appState.selectedAttributes.custom_text;
  const previousColor = appState.selectedAttributes.color;
  const previousFont = appState.selectedAttributes.font;
  const previousMounting = appState.selectedAttributes.mounting;
  const previousBacking = appState.selectedAttributes.backing;

  // Gather values from configurator form
  appState.selectedAttributes.custom_text = elements.inputCustomText.value;
  appState.selectedAttributes.font = elements.selectFont.value;
  
  const checkedColor = document.querySelector('input[name="attr-color"]:checked');
  if (checkedColor) appState.selectedAttributes.color = checkedColor.value;
  
  const checkedMounting = document.querySelector('input[name="attr-mounting"]:checked');
  if (checkedMounting) appState.selectedAttributes.mounting = checkedMounting.value;
  
  const checkedBacking = document.querySelector('input[name="attr-backing"]:checked');
  if (checkedBacking) appState.selectedAttributes.backing = checkedBacking.value;
  
  // Character count display
  document.querySelector(".char-count").innerText = `${appState.selectedAttributes.custom_text.length}/30`;

  // Determine if any changed attribute affects AI Preview based on schema
  const changes = [];
  if (previousText !== appState.selectedAttributes.custom_text) changes.push("custom_text");
  if (previousColor !== appState.selectedAttributes.color) changes.push("color");
  if (previousFont !== appState.selectedAttributes.font) changes.push("font");
  if (previousMounting !== appState.selectedAttributes.mounting) changes.push("mounting");
  if (previousBacking !== appState.selectedAttributes.backing) changes.push("backing");

  if (changes.length === 0) return;

  logEvent("CONFIG", `Attribute changed: ${changes.join(", ")}`);

  // Check if any changed attribute affects the preview according to schema
  const affectsPreviewChanged = changes.some(key => {
    const attrDef = CATEGORY_SCHEMA.attributes.find(attr => attr.key === key);
    return attrDef ? attrDef.affects_ai_preview : false;
  });

  if (affectsPreviewChanged) {
    logEvent("CONFIG", "Changed attribute affects AI Preview schema.");
    
    // Auto-switch to AI Preview tab on first change of preview-affecting attribute
    if (appState.isFirstAttributeChange) {
      appState.isFirstAttributeChange = false;
      logEvent("UI", "Auto-switching to 'AI Preview' tab on first configurator update");
      switchTab("preview");
    } else {
      // Check if a preview already exists and is different from new config
      checkStaleState();
    }
  } else {
    logEvent("CONFIG", "Changed attribute does NOT affect AI Preview (Backing board). Skipping preview actions.");
  }
}

// Watch changes on inputs
elements.inputCustomText.addEventListener("input", updateSelectedAttributes);
elements.selectFont.addEventListener("change", updateSelectedAttributes);

// Radio changes
document.querySelectorAll('input[name="attr-color"]').forEach(el => {
  el.addEventListener("change", updateSelectedAttributes);
});
document.querySelectorAll('input[name="attr-mounting"]').forEach(el => {
  el.addEventListener("change", updateSelectedAttributes);
});
document.querySelectorAll('input[name="attr-backing"]').forEach(el => {
  el.addEventListener("change", updateSelectedAttributes);
});

/* Helper to check if preview is outdated */
function checkStaleState() {
  if (!appState.lastGeneratedAttributes) return;
  
  // Compare all affects_ai_preview attributes
  const isStale = CATEGORY_SCHEMA.attributes
    .filter(attr => attr.affects_ai_preview)
    .some(attr => appState.selectedAttributes[attr.key] !== appState.lastGeneratedAttributes[attr.key]);
  
  if (isStale) {
    // Show Stale Warning overlay, dim image
    elements.previewImageWrapper.classList.add("stale");
    elements.staleBanner.classList.remove("hidden");
    logEvent("UI", "Configuration changed. AI Preview marked as stale.");
  } else {
    // Hide stale overlay
    elements.previewImageWrapper.classList.remove("stale");
    elements.staleBanner.classList.add("hidden");
    logEvent("UI", "Configuration returned to matching preview state.");
  }
}

/* Cache Key Generator */
function getCacheKey(attributes) {
  // Deterministic hash based on category and preview-affecting attributes sorted
  const keys = CATEGORY_SCHEMA.attributes
    .filter(attr => attr.affects_ai_preview)
    .map(attr => attr.key)
    .sort();
    
  const combo = keys.map(key => `${key}:${attributes[key]}`).join("|");
  return `${CATEGORY_SCHEMA.id}#${combo}`;
}

/* Mock API Client Call */
async function mockGeneratePreviewAPI(requestData, responseMode, latencyMs) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Read simulation response mode selected
      if (responseMode === "502") {
        resolve({
          status: 502,
          data: { success: false, message: "Provider communication failure" }
        });
      } else if (responseMode === "504") {
        resolve({
          status: 504,
          data: { success: false, message: "Connection to upstream provider timed out" }
        });
      } else if (responseMode === "429-session") {
        resolve({
          status: 429,
          data: {
            success: false,
            message: "Too Many Requests",
            data: { limit_reached: true, limit_scope: "session" }
          }
        });
      } else if (responseMode === "429-user") {
        resolve({
          status: 429,
          data: {
            success: false,
            message: "Too Many Requests",
            data: { limit_reached: true, limit_scope: "user" }
          }
        });
      } else {
        // Success Mode (200)
        // Resolve cache check
        const cacheKey = getCacheKey(requestData.selected_attributes);
        const hasCustomText = requestData.selected_attributes.custom_text && requestData.selected_attributes.custom_text.trim().length > 0;
        
        // Cache bypass rule: never cache if custom text is customized (non-default or customized names)
        // But for mock demo, we cache standard selections unless text is heavily altered.
        // Let's enforce the rule: "Only bypass cache when custom_text is part of selected_attributes, since that makes each generation unique by definition"
        // Wait, since custom_text is in selected_attributes, we will bypass cache. But we can check if it matches "Dream Big" (default) to show caching!
        // To be precise: If custom_text exists and is not empty, we bypass cache. Let's write that logic.
        const bypassCache = hasCustomText && requestData.selected_attributes.custom_text.toLowerCase() !== "dream big";
        
        if (!bypassCache && appState.cache.has(cacheKey)) {
          resolve({
            status: 200,
            data: {
              success: true,
              data: {
                output_image_url: appState.cache.get(cacheKey),
                from_cache: true,
                generation_id: 'gen_' + Math.random().toString(36).substring(2, 10)
              }
            }
          });
        } else {
          // Select mock asset based on color chosen
          const color = requestData.selected_attributes.color;
          const imagePath = PREVIEW_ASSETS[color] || PREVIEW_ASSETS["blue"];
          
          // Save in cache if not bypassed
          if (!bypassCache) {
            appState.cache.set(cacheKey, imagePath);
          }
          
          resolve({
            status: 200,
            data: {
              success: true,
              data: {
                output_image_url: imagePath,
                from_cache: false,
                generation_id: 'gen_' + Math.random().toString(36).substring(2, 10)
              }
            }
          });
        }
      }
    }, latencyMs);
  });
}

/* Main Preview Generation Orchestrator */
async function generatePreview() {
  logEvent("UI", "Triggered preview generation request");
  
  // Set UI to loading state
  elements.stateInitial.classList.add("hidden");
  elements.stateSuccess.classList.add("hidden");
  elements.stateError.classList.add("hidden");
  elements.stateLoading.classList.remove("hidden");
  elements.previewImageWrapper.classList.remove("stale");
  elements.staleBanner.classList.add("hidden");
  
  const currentAttributes = { ...appState.selectedAttributes };
  
  // 1. Check Caching locally first (before decrementing quotas or calling mock API)
  const cacheKey = getCacheKey(currentAttributes);
  const isCustomTextBypass = currentAttributes.custom_text && currentAttributes.custom_text.trim().toLowerCase() !== "dream big";
  
  let isCacheHit = false;
  let cachedUrl = null;
  if (!isCustomTextBypass && appState.cache.has(cacheKey)) {
    isCacheHit = true;
    cachedUrl = appState.cache.get(cacheKey);
    logEvent("CACHE", `Local cache hit detected for key. Bypassing rate limit & API call.`);
  }

  // 2. Rate Limiting Check (Only if not a cache hit!)
  if (!isCacheHit) {
    if (appState.isLoggedIn) {
      if (appState.userQuotaRemaining <= 0) {
        logEvent("RATE-LIMIT", "Quota exceeded: user daily cap reached (Daily limit reached, try again tomorrow)", true);
        renderErrorState(429, "user");
        return;
      }
    } else {
      if (appState.guestQuotaRemaining <= 0) {
        logEvent("RATE-LIMIT", "Quota exceeded: guest session cap reached (You've used your free previews for now — sign up)", true);
        renderErrorState(429, "session");
        return;
      }
    }
  }

  // Prep POST body contract
  const requestBody = {
    category_id: CATEGORY_SCHEMA.id,
    product_id: null, // Fully custom configurator
    selected_attributes: currentAttributes,
    session_id: appState.isLoggedIn ? null : guestSessionId
  };

  const latency = parseInt(elements.simLatency.value, 10);
  const apiMode = document.querySelector('input[name="sim-api-mode"]:checked').value;
  
  logEvent("API", `POST /api/ai/generate-preview \nBody: ${JSON.stringify(requestBody, null, 2)}`);

  try {
    const response = await mockGeneratePreviewAPI(requestBody, apiMode, latency);
    
    if (response.status === 200) {
      const resData = response.data.data;
      
      // Save last generated config to check stale state later
      appState.lastGeneratedAttributes = { ...currentAttributes };
      appState.currentPreviewUrl = resData.output_image_url;
      appState.currentGenerationId = resData.generation_id;
      
      logEvent("API", `200 OK. Response: ${JSON.stringify(response.data, null, 2)}`);
      
      // Decrement Quota only if it wasn't served from cache
      if (!resData.from_cache) {
        if (appState.isLoggedIn) {
          appState.userQuotaRemaining--;
        } else {
          appState.guestQuotaRemaining--;
        }
        updateQuotaDisplay();
      }

      // Render success
      elements.previewImage.src = resData.output_image_url;
      
      if (resData.from_cache) {
        elements.cacheBadge.classList.remove("hidden");
      } else {
        elements.cacheBadge.classList.add("hidden");
      }
      
      elements.stateLoading.classList.add("hidden");
      elements.stateSuccess.classList.remove("hidden");
      logEvent("UI", `Successfully rendered preview! Generation ID: ${resData.generation_id}`);
      
    } else {
      // API error (429, 502, 504)
      logEvent("API", `${response.status} Error. Response: ${JSON.stringify(response.data, null, 2)}`, true);
      renderErrorState(response.status, response.data.data?.limit_scope || null);
    }
  } catch (err) {
    logEvent("SYSTEM", `Unhandled error: ${err.message}`, true);
    renderErrorState(500);
  }
}

/* Render Error States */
function renderErrorState(statusCode, limitScope) {
  elements.stateLoading.classList.add("hidden");
  elements.stateSuccess.classList.add("hidden");
  elements.stateInitial.classList.add("hidden");
  elements.stateError.classList.remove("hidden");
  
  if (statusCode === 429) {
    elements.errorTitle.innerText = "Daily Limit Reached";
    if (limitScope === "user") {
      elements.errorMessage.innerText = "Daily limit reached, try again tomorrow.";
      logEvent("UI", "Displaying daily user limit message");
    } else {
      elements.errorMessage.innerText = "You've used your free previews for now — sign up to keep designing.";
      logEvent("UI", "Displaying guest session limit message");
    }
  } else if (statusCode === 504) {
    elements.errorTitle.innerText = "Preview Timeout";
    elements.errorMessage.innerText = "The AI preview generator is taking longer than usual. Please try again.";
  } else {
    // 502 or generic errors
    elements.errorTitle.innerText = "Preview Unavailable";
    elements.errorMessage.innerText = "An error occurred while generating the preview. Our team has been notified.";
  }
}

/* Simulator Dashboard updates */
function updateQuotaDisplay() {
  const currentQuota = appState.isLoggedIn ? appState.userQuotaRemaining : appState.guestQuotaRemaining;
  elements.simQuotaValue.innerText = currentQuota;
}

elements.simAuthToggle.addEventListener("change", (e) => {
  appState.isLoggedIn = e.target.checked;
  elements.simCurrentRole.innerText = appState.isLoggedIn ? "AUTHENTICATED USER" : "GUEST";
  logEvent("AUTH", `Auth state updated. User role is now: ${elements.simCurrentRole.innerText}`);
  updateQuotaDisplay();
  
  // Recheck stale banner when auth switches as validation limits can change
  checkStaleState();
});

elements.btnResetQuota.addEventListener("click", () => {
  appState.guestQuotaRemaining = 5;
  appState.userQuotaRemaining = 20;
  updateQuotaDisplay();
  logEvent("SYSTEM", "Simulated usage quotas reset to defaults (Guest: 5, Logged-in: 20).");
});

elements.simLatency.addEventListener("input", (e) => {
  const val = e.target.value;
  elements.lblLatency.innerText = `${val}ms`;
});

elements.btnClearLogs.addEventListener("click", () => {
  elements.logsOutput.innerHTML = "[SYSTEM] Telemetry logs cleared.";
});

// Wiring actions to Regenerate buttons
elements.btnRegenerate.addEventListener("click", generatePreview);
elements.btnRegenerateStale.addEventListener("click", generatePreview);
elements.btnErrorRetry.addEventListener("click", generatePreview);

// Initial setup
updateQuotaDisplay();
logEvent("SYSTEM", "AIPreviewPanel configuration schema loaded from Module 2.");
