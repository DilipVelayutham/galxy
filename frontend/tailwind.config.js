/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        galxy: {
          void: '#0B0B0F',
          charcoal: '#16161C',
          magenta: '#FF2E8A',
          blue: '#18E7FF',
          violet: '#9B5CFF',
          yellow: '#FFD84D',
          primary: '#F4F4F7',
          muted: '#8A8A97',
        },
        voidBlack: '#0B0B0F',
        panelCharcoal: '#16161C',
        neonPink: '#FF2E8A',
        neonBlue: '#18E7FF',
        neonViolet: '#9B5CFF',
        neonYellow: '#FFD84D',
        textPrimary: '#F4F4F7',
        textMuted: '#8A8A97',
      }
    },
  },
  plugins: [],
}
