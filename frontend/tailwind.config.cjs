/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Standard Blue Theme for Primary Elements
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // Standard blue for primary buttons
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // Rich Gold Accent Theme
        secondary: {
          50: '#fefdf8',
          100: '#fef7e0',
          200: '#fdecc8',
          300: '#fbdfa1',
          400: '#f9d071',
          500: '#f6c042',
          600: '#d4af37', // Rich gold for accents and highlights
          700: '#b8941f',
          800: '#9c7a0c',
          900: '#7d6003',
        },
        // Navy Theme for Headers and Navigation (not buttons)
        navy: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53',
          900: '#1e2a38', // Deep navy for headers and navigation only
        },
        // Subtle Blue Theme for Login/Auth
        blue: {
          50: '#f0f7ff',
          100: '#e0efff',
          200: '#b9ddff',
          300: '#7cc4ff',
          400: '#36a7ff',
          500: '#0c8ce9', // Subtle professional blue
          600: '#0066cc',
          700: '#0052a3',
          800: '#004085',
          900: '#003366',
        },
        // Refined Background Colors
        background: {
          primary: '#f8f8f4',    // Soft ivory for main content areas
          secondary: '#ffffff',   // Pure white for cards/panels
          tertiary: '#f5f5f1',   // Subtle ivory variant
        },
        // Professional Text Colors
        text: {
          primary: '#2c2c2c',     // Charcoal for body text
          secondary: '#6b7280',   // Muted gray for secondary text
          tertiary: '#9ca3af',    // Light gray for subtle text
          inverse: '#ffffff',     // White text for dark backgrounds
          heading: '#1e2a38',     // Deep navy for headings (not buttons)
        },
        // Consistent Border Colors
        border: {
          primary: '#e5e7eb',     // Light gray borders
          secondary: '#f3f4f6',   // Subtle borders
          focus: '#d4af37',       // Gold focus states
          accent: '#1e2a38',      // Navy accent borders
        },
        // Alert Colors (Accessibility Compliant)
        success: {
          50: '#f0f9f4',
          500: '#2e7d32',
          600: '#1b5e20',
        },
        warning: {
          50: '#fff8e1',
          500: '#ed6c02',
          600: '#e65100',
        },
        error: {
          50: '#fef2f2',
          500: '#c62828',
          600: '#b71c1c',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Source Sans Pro', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'Libre Baskerville', 'Georgia', 'serif'],
      },
      fontSize: {
        // Professional Typography Scale
        'heading-xl': ['2.25rem', { lineHeight: '2.5rem', fontWeight: '700', letterSpacing: '-0.025em' }], // 36px
        'heading-lg': ['1.875rem', { lineHeight: '2.25rem', fontWeight: '600', letterSpacing: '-0.025em' }], // 30px
        'heading-md': ['1.5rem', { lineHeight: '2rem', fontWeight: '600', letterSpacing: '-0.025em' }],     // 24px
        'heading-sm': ['1.25rem', { lineHeight: '1.75rem', fontWeight: '600' }],                           // 20px
        'heading-xs': ['1.125rem', { lineHeight: '1.5rem', fontWeight: '600' }],                          // 18px
        'body-xl': ['1.125rem', { lineHeight: '1.75rem', fontWeight: '400' }],                            // 18px
        'body-lg': ['1rem', { lineHeight: '1.625rem', fontWeight: '400' }],                               // 16px
        'body-md': ['0.875rem', { lineHeight: '1.375rem', fontWeight: '400' }],                          // 14px
        'body-sm': ['0.75rem', { lineHeight: '1.125rem', fontWeight: '400' }],                           // 12px
        'caption': ['0.6875rem', { lineHeight: '1rem', fontWeight: '400' }],                             // 11px
      },
      spacing: {
        // Professional Spacing Scale
        'container': '1.5rem',    // Standard container padding
        'section': '2rem',        // Section spacing
        'component': '1.25rem',   // Component internal spacing
        'element': '0.75rem',     // Element spacing
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'slide-down': 'slideDown 0.4s ease-out',
        'bounce-subtle': 'bounceSubtle 0.6s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
      boxShadow: {
        'elegant': '0 4px 6px -1px rgba(30, 42, 56, 0.1), 0 2px 4px -1px rgba(30, 42, 56, 0.06)',
        'elegant-lg': '0 10px 15px -3px rgba(30, 42, 56, 0.1), 0 4px 6px -2px rgba(30, 42, 56, 0.05)',
        'elegant-xl': '0 20px 25px -5px rgba(30, 42, 56, 0.1), 0 10px 10px -5px rgba(30, 42, 56, 0.04)',
        'gold-glow': '0 0 20px rgba(212, 175, 55, 0.3)',
      },
    },
  },
  plugins: [],
} 