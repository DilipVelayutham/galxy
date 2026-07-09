/**
 * Mock data for development when backend APIs are unavailable.
 *
 * Reflects GALXY's actual product model:
 *  - type: 'pre_designed' | 'fully_custom' (NOT a generic Physical/Digital list)
 *  - category_id referencing a real category document (categories carry
 *    attribute_schema, accent_color, hero_image -- see mockCategories below)
 *  - snake_case field names matching the documented API contract
 *  - default_attributes as a structured object keyed by the category's
 *    attribute_schema, not a single free-text string
 */

// Categories are real documents, each with the metadata the public module
// needs (attribute_schema drives the structured default_attributes inputs;
// accent_color / hero_image are used by the public gallery/configurator).
export const mockCategories = [
  {
    _id: 'cat_001',
    name: 'Apparel',
    slug: 'apparel',
    accent_color: '#FF2E8A',
    hero_image: 'https://picsum.photos/seed/cat-apparel/800/400',
    attribute_schema: [
      { key: 'color', label: 'Color', type: 'select', options: ['Black', 'White', 'Burgundy', 'Volt Green'] },
      { key: 'size', label: 'Size', type: 'select', options: ['S', 'M', 'L', 'XL'] },
      { key: 'material', label: 'Material', type: 'text' },
    ],
  },
  {
    _id: 'cat_002',
    name: 'Electronics Accessories',
    slug: 'electronics-accessories',
    accent_color: '#6C5CE7',
    hero_image: 'https://picsum.photos/seed/cat-electronics/800/400',
    attribute_schema: [
      { key: 'color', label: 'Color', type: 'select', options: ['Midnight Black', 'Pearl White', 'Titanium Grey'] },
      { key: 'warranty_months', label: 'Warranty (months)', type: 'number' },
      { key: 'battery_life_hrs', label: 'Battery Life (hrs)', type: 'slider', min: 0, max: 72 },
    ],
  },
  {
    _id: 'cat_003',
    name: 'Home & Living',
    slug: 'home-living',
    accent_color: '#22C55E',
    hero_image: 'https://picsum.photos/seed/cat-home/800/400',
    attribute_schema: [
      { key: 'finish', label: 'Finish', type: 'text' },
      { key: 'dimensions', label: 'Dimensions', type: 'text' },
    ],
  },
  {
    _id: 'cat_004',
    name: 'Fitness & Wellness',
    slug: 'fitness-wellness',
    accent_color: '#F59E0B',
    hero_image: 'https://picsum.photos/seed/cat-fitness/800/400',
    attribute_schema: [
      { key: 'color', label: 'Color', type: 'select', options: ['Ocean Teal', 'Charcoal', 'Coral'] },
      { key: 'size', label: 'Size', type: 'text' },
    ],
  },
];

export const getMockCategoriesResponse = () => ({
  success: true,
  data: { categories: mockCategories },
});

export const mockProducts = [
  {
    _id: 'prod_001',
    title: 'Quantum Pro Wireless Headphones',
    slug: 'quantum-pro-wireless-headphones',
    category_id: 'cat_002',
    type: 'pre_designed',
    base_price: 4999,
    description:
      'Premium wireless headphones with active noise cancellation, 40-hour battery life, and Hi-Res Audio certification. Features adaptive EQ and multi-device connectivity.',
    specifications: 'Driver: 40mm | Frequency: 20Hz-40kHz | Battery: 40hrs | ANC: Adaptive | Bluetooth: 5.3 | Weight: 250g',
    default_attributes: { color: 'Midnight Black', warranty_months: 12, battery_life_hrs: 40 },
    stock_status: 'in_stock',
    tags: ['wireless', 'headphones', 'anc', 'premium', 'bluetooth'],
    is_featured: true,
    is_active: true,
    images: [
      { _id: 'img_001', url: 'https://picsum.photos/seed/headphones1/400/400', isThumbnail: true },
      { _id: 'img_002', url: 'https://picsum.photos/seed/headphones2/400/400', isThumbnail: false },
      { _id: 'img_003', url: 'https://picsum.photos/seed/headphones3/400/400', isThumbnail: false },
    ],
    rating_avg: 4.7,
    rating_count: 328,
    createdAt: '2025-11-15T10:30:00Z',
    updatedAt: '2026-06-20T14:22:00Z',
  },
  {
    _id: 'prod_002',
    title: 'NeoFlex Ultra Track Jacket',
    slug: 'neoflex-ultra-track-jacket',
    category_id: 'cat_001',
    type: 'pre_designed',
    base_price: 7499,
    description:
      'Performance track jacket with a breathable, quick-dry shell and a relaxed athletic fit. Part of GALXY\'s pre-designed core line.',
    specifications: 'Shell: Ripstop | Lining: Mesh | Fit: Relaxed | Weight: 320g',
    default_attributes: { color: 'Volt Green', size: 'M', material: 'Ripstop Polyester' },
    stock_status: 'in_stock',
    tags: ['jacket', 'performance', 'track'],
    is_featured: true,
    is_active: true,
    images: [
      { _id: 'img_004', url: 'https://picsum.photos/seed/jacket-track1/400/400', isThumbnail: true },
      { _id: 'img_005', url: 'https://picsum.photos/seed/jacket-track2/400/400', isThumbnail: false },
    ],
    rating_avg: 4.5,
    rating_count: 189,
    createdAt: '2025-12-01T08:00:00Z',
    updatedAt: '2026-06-18T11:00:00Z',
  },
  {
    _id: 'prod_003',
    title: 'Custom Studio Hoodie',
    slug: 'custom-studio-hoodie',
    category_id: 'cat_001',
    type: 'fully_custom',
    base_price: 2999,
    description:
      'Fully custom hoodie base for admins to configure per-order: color, print placement, and fabric weight are all buyer-selectable at checkout.',
    specifications: 'Fabric: 320gsm Fleece | Fit: Oversized | Print: DTG',
    default_attributes: { color: 'Black', size: 'L', material: '80% Cotton, 20% Poly' },
    stock_status: 'low_stock',
    tags: ['hoodie', 'custom', 'streetwear'],
    is_featured: false,
    is_active: true,
    images: [
      { _id: 'img_006', url: 'https://picsum.photos/seed/hoodie1/400/400', isThumbnail: true },
      { _id: 'img_007', url: 'https://picsum.photos/seed/hoodie2/400/400', isThumbnail: false },
    ],
    rating_avg: 4.3,
    rating_count: 542,
    createdAt: '2026-01-10T09:30:00Z',
    updatedAt: '2026-06-25T16:45:00Z',
  },
  {
    _id: 'prod_004',
    title: 'Aurora Silk Blend Bomber',
    slug: 'aurora-silk-blend-bomber',
    category_id: 'cat_001',
    type: 'pre_designed',
    base_price: 3299,
    description:
      'Luxurious silk-blend bomber jacket with premium satin lining, ribbed cuffs, and a modern relaxed fit.',
    specifications: 'Material: 60% Silk, 40% Polyester | Lining: Satin | Care: Dry Clean',
    default_attributes: { color: 'Burgundy', size: 'L', material: '60% Silk, 40% Polyester' },
    stock_status: 'in_stock',
    tags: ['jacket', 'silk', 'premium', 'fashion'],
    is_featured: false,
    is_active: true,
    images: [
      { _id: 'img_008', url: 'https://picsum.photos/seed/jacket1/400/400', isThumbnail: true },
    ],
    rating_avg: 4.8,
    rating_count: 67,
    createdAt: '2026-02-20T12:00:00Z',
    updatedAt: '2026-06-10T09:30:00Z',
  },
  {
    _id: 'prod_005',
    title: 'ProGrip Yoga Mat Premium',
    slug: 'progrip-yoga-mat-premium',
    category_id: 'cat_004',
    type: 'pre_designed',
    base_price: 1899,
    description:
      'Extra-thick 6mm natural rubber yoga mat with alignment markings and non-slip texture on both sides. Eco-friendly, PVC- and latex-free.',
    specifications: 'Material: Natural Rubber | Thickness: 6mm | Size: 183x68cm | Weight: 2.5kg',
    default_attributes: { color: 'Ocean Teal', size: 'Standard' },
    stock_status: 'in_stock',
    tags: ['yoga', 'mat', 'fitness', 'eco-friendly'],
    is_featured: false,
    is_active: true,
    images: [
      { _id: 'img_009', url: 'https://picsum.photos/seed/yogamat/400/400', isThumbnail: true },
    ],
    rating_avg: 4.6,
    rating_count: 412,
    createdAt: '2026-03-05T14:00:00Z',
    updatedAt: '2026-06-28T10:15:00Z',
  },
  {
    _id: 'prod_006',
    title: 'Nebula Wireless Charging Pad',
    slug: 'nebula-wireless-charging-pad',
    category_id: 'cat_002',
    type: 'pre_designed',
    base_price: 1499,
    description:
      '15W fast wireless charging pad with an aircraft-grade aluminum frame and per-edge ambient RGB lighting.',
    specifications: 'Output: 15W | Frame: Aluminum | Cable: USB-C detachable',
    default_attributes: { color: 'Titanium Grey', warranty_months: 18, battery_life_hrs: 0 },
    stock_status: 'in_stock',
    tags: ['charging', 'wireless', 'accessory'],
    is_featured: true,
    is_active: true,
    images: [
      { _id: 'img_010', url: 'https://picsum.photos/seed/chargingpad1/400/400', isThumbnail: true },
      { _id: 'img_011', url: 'https://picsum.photos/seed/chargingpad2/400/400', isThumbnail: false },
    ],
    rating_avg: 4.4,
    rating_count: 256,
    createdAt: '2026-04-12T16:30:00Z',
    updatedAt: '2026-06-22T08:45:00Z',
  },
  {
    _id: 'prod_007',
    title: 'Custom Fit Everyday Tee',
    slug: 'custom-fit-everyday-tee',
    category_id: 'cat_001',
    type: 'fully_custom',
    base_price: 899,
    description:
      'Fully custom base tee -- buyers choose fabric weight, neckline, and print placement at checkout. No default color/size is fixed at the catalog level.',
    specifications: 'Fabric options: 180gsm / 220gsm Combed Cotton | Neckline: Crew or V',
    default_attributes: { color: 'White', size: 'M', material: '100% Combed Cotton' },
    stock_status: 'out_of_stock',
    tags: ['tee', 'custom', 'basics'],
    is_featured: false,
    is_active: false,
    images: [
      { _id: 'img_012', url: 'https://picsum.photos/seed/tee1/400/400', isThumbnail: true },
    ],
    rating_avg: 4.9,
    rating_count: 1023,
    createdAt: '2026-01-25T11:00:00Z',
    updatedAt: '2026-06-15T13:20:00Z',
  },
  {
    _id: 'prod_008',
    title: 'Titanium Travel Backpack 40L',
    slug: 'titanium-travel-backpack-40l',
    category_id: 'cat_002',
    type: 'pre_designed',
    base_price: 5299,
    description:
      'Expandable 40L travel backpack with TSA-approved laptop compartment, anti-theft zippers, and waterproof fabric.',
    specifications: 'Capacity: 40L (expandable) | Material: 900D Waterproof | Laptop: Up to 17" | Weight: 1.8kg',
    default_attributes: { color: 'Midnight Black', warranty_months: 24, battery_life_hrs: 0 },
    stock_status: 'in_stock',
    tags: ['backpack', 'travel', 'waterproof', 'laptop'],
    is_featured: true,
    is_active: true,
    images: [
      { _id: 'img_013', url: 'https://picsum.photos/seed/backpack1/400/400', isThumbnail: true },
      { _id: 'img_014', url: 'https://picsum.photos/seed/backpack2/400/400', isThumbnail: false },
    ],
    rating_avg: 4.2,
    rating_count: 178,
    createdAt: '2026-03-18T15:00:00Z',
    updatedAt: '2026-06-30T07:10:00Z',
  },
  {
    _id: 'prod_009',
    title: 'Zen Bamboo Desktop Organizer',
    slug: 'zen-bamboo-desktop-organizer',
    category_id: 'cat_003',
    type: 'pre_designed',
    base_price: 899,
    description:
      'Minimalist bamboo desktop organizer with 5 compartments, phone stand, and cable management.',
    specifications: 'Material: Bamboo | Compartments: 5 | Dimensions: 30x15x12cm | Weight: 0.6kg',
    default_attributes: { finish: 'Natural Bamboo', dimensions: '30x15x12cm' },
    stock_status: 'low_stock',
    tags: ['organizer', 'desk', 'bamboo', 'minimal'],
    is_featured: false,
    is_active: true,
    images: [
      { _id: 'img_015', url: 'https://picsum.photos/seed/organizer/400/400', isThumbnail: true },
    ],
    rating_avg: 4.1,
    rating_count: 93,
    createdAt: '2026-04-01T10:00:00Z',
    updatedAt: '2026-06-26T12:30:00Z',
  },
  {
    _id: 'prod_010',
    title: 'Eclipse Noise-Cancelling Earbuds',
    slug: 'eclipse-noise-cancelling-earbuds',
    category_id: 'cat_002',
    type: 'pre_designed',
    base_price: 3499,
    description:
      'True wireless earbuds with hybrid ANC, spatial audio, and IPX5 water resistance.',
    specifications: 'Drivers: 11mm | ANC: Hybrid | Battery: 8hrs (32hrs case) | IPX5 | Bluetooth 5.3',
    default_attributes: { color: 'Pearl White', warranty_months: 12, battery_life_hrs: 8 },
    stock_status: 'in_stock',
    tags: ['earbuds', 'wireless', 'anc', 'spatial-audio'],
    is_featured: false,
    is_active: true,
    images: [
      { _id: 'img_016', url: 'https://picsum.photos/seed/earbuds1/400/400', isThumbnail: true },
      { _id: 'img_017', url: 'https://picsum.photos/seed/earbuds2/400/400', isThumbnail: false },
    ],
    rating_avg: 4.6,
    rating_count: 687,
    createdAt: '2026-05-10T09:00:00Z',
    updatedAt: '2026-07-01T15:00:00Z',
  },
  {
    _id: 'prod_011',
    title: 'Custom Statement Cap',
    slug: 'custom-statement-cap',
    category_id: 'cat_001',
    type: 'fully_custom',
    base_price: 799,
    description:
      'Fully custom snapback base -- embroidery text, thread color, and panel color are all buyer-configurable.',
    specifications: 'Panels: 6 | Closure: Snapback | Embroidery: Included',
    default_attributes: { color: 'Black', size: 'One Size', material: 'Cotton Twill' },
    stock_status: 'in_stock',
    tags: ['cap', 'custom', 'accessory'],
    is_featured: false,
    is_active: true,
    images: [
      { _id: 'img_018', url: 'https://picsum.photos/seed/cap1/400/400', isThumbnail: true },
    ],
    rating_avg: 4.3,
    rating_count: 1456,
    createdAt: '2026-02-14T08:30:00Z',
    updatedAt: '2026-06-12T16:00:00Z',
  },
  {
    _id: 'prod_012',
    title: 'Aurora Ceramic Diffuser',
    slug: 'aurora-ceramic-diffuser',
    category_id: 'cat_003',
    type: 'pre_designed',
    base_price: 1299,
    description:
      'Handcrafted ceramic aromatherapy diffuser with a soft ambient LED glow and a 300ml water tank.',
    specifications: 'Tank: 300ml | Runtime: up to 10hrs | Material: Ceramic',
    default_attributes: { finish: 'Matte White', dimensions: '12x12x18cm' },
    stock_status: 'in_stock',
    tags: ['diffuser', 'home', 'ceramic'],
    is_featured: false,
    is_active: true,
    images: [
      { _id: 'img_019', url: 'https://picsum.photos/seed/diffuser/400/400', isThumbnail: true },
    ],
    rating_avg: 4.8,
    rating_count: 234,
    createdAt: '2026-05-20T13:00:00Z',
    updatedAt: '2026-06-29T11:45:00Z',
  },
];

/**
 * Simulate API response with pagination
 * @param {object} params - Query params { page, limit, search, category_id, stock_status, is_active }
 * @returns {object} Paginated response matching API format
 */
export const getMockProductsResponse = (params = {}) => {
  const {
    page = 1,
    limit = 10,
    search = '',
    category_id = '',
    stock_status = '',
    is_active = '',
  } = params;

  let filtered = [...mockProducts];

  // Apply search filter
  if (search) {
    const searchLower = search.toLowerCase();
    filtered = filtered.filter(
      (p) =>
        p.title.toLowerCase().includes(searchLower) ||
        p.tags.some((tag) => tag.toLowerCase().includes(searchLower))
    );
  }

  // Apply category filter
  if (category_id) {
    filtered = filtered.filter((p) => p.category_id === category_id);
  }

  // Apply stock status filter
  if (stock_status) {
    filtered = filtered.filter((p) => p.stock_status === stock_status);
  }

  // Apply active status filter
  if (is_active !== '') {
    const active = is_active === 'true' || is_active === true;
    filtered = filtered.filter((p) => p.is_active === active);
  }

  // Pagination
  const total = filtered.length;
  const totalPages = Math.ceil(total / limit);
  const start = (page - 1) * limit;
  const end = start + limit;
  const products = filtered.slice(start, end);

  return {
    success: true,
    data: {
      products,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        totalPages,
        hasNextPage: page < totalPages,
        hasPrevPage: page > 1,
      },
    },
  };
};
