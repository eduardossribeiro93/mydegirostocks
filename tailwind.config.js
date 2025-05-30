/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{html,js,py}",
    "./assets/**/*.{html,js,css}",
    "./components/**/*.{html,js,py}",
    "./*.py",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0f172a',  // Dark blue
          light: '#1e293b',
          lighter: '#334155',
          dark: '#0a0f1a',
        },
        secondary: {
          DEFAULT: '#64748b',  // Slate
          light: '#94a3b8',
          lighter: '#cbd5e1',
          dark: '#475569',
        },
        accent: {
          DEFAULT: '#3b82f6',  // Blue
          light: '#60a5fa',
          lighter: '#93c5fd',
          dark: '#2563eb',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'heading-1': ['2.5rem', { lineHeight: '3rem', fontWeight: '700' }],
        'heading-2': ['2rem', { lineHeight: '2.5rem', fontWeight: '600' }],
        'heading-3': ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }],
        'body': ['1rem', { lineHeight: '1.5rem' }],
        'body-lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'body-sm': ['0.875rem', { lineHeight: '1.25rem' }],
      }
    },
  },
  plugins: [],
  darkMode: 'class',
} 