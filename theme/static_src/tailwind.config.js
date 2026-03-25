/**
 * This is a standard Tailwind v3 configuration file.
 */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../polls/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'cosmic-bg': '#0B0F19',
        'cosmic-accent': '#06b6d4',
        'cosmic-cyan': '#22d3ee',
        'cosmic-glass': 'rgba(11, 15, 25, 0.7)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 3s ease-in-out infinite',
        'fade-in': 'fade-in 0.8s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-15px)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(6, 182, 212, 0.2), 0 0 20px rgba(34, 211, 238, 0.1)' },
          '50%': { boxShadow: '0 0 25px rgba(6, 182, 212, 0.4), 0 0 40px rgba(34, 211, 238, 0.2)' },
        },
        'fade-in': {
          'from': { opacity: '0', transform: 'translateY(20px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [
    require('daisyui'),
  ],
}
