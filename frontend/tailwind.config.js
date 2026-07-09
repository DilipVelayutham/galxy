/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        voidBlack: '#0B0B0F',
        panelCharcoal: '#16161C',
        primaryNeon: '#FF2E8A',
        secondaryNeon: '#18E7FF',
        accentViolet: '#9B5CFF',
        accentYellow: '#FFD84D',
        textPrimary: '#F4F4F7',
        textMuted: '#8A8A97',
      }
    },
  },
  plugins: [],
}
