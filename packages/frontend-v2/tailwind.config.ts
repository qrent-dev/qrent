import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#1d4ed8', // blue-700
          light: '#3b82f6', // blue-500
          dark: '#1e40af' // blue-800
        }
      },
      boxShadow: {
        card: '0 6px 24px rgba(2, 6, 23, 0.08)'
      }
    },
  },
  plugins: [],
}
export default config


