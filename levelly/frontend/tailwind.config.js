/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // LEVELLY Design System
        emerald: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        levelly: {
          bg: '#F7F5F2',        // Warm neutral background
          primary: '#065f46',   // Deep emerald
          'primary-light': '#10b981',
          text: '#1C1917',      // Dark charcoal
          'text-secondary': '#78716C',
          success: '#15803D',   // Soft green healthy state
          warning: '#D97706',   // Amber warning
          danger: '#DC2626',    // Red for serious risk
          card: '#FFFFFF',
          border: '#E7E5E0',
          'safety': '#059669',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'card': '0 1px 4px 0 rgba(0,0,0,0.06), 0 2px 16px 0 rgba(0,0,0,0.04)',
        'card-hover': '0 4px 16px 0 rgba(0,0,0,0.10)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'bounce-soft': 'bounceSoft 0.5s ease-out',
        'coin-drop': 'coinDrop 0.8s ease-in-out',
        'piggy-shake': 'piggyShake 0.6s ease-in-out',
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
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        coinDrop: {
          '0%': { transform: 'translateY(-30px)', opacity: '0' },
          '60%': { transform: 'translateY(5px)', opacity: '1' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        piggyShake: {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(-3deg)' },
          '75%': { transform: 'rotate(3deg)' },
        },
      },
    },
  },
  plugins: [],
}
