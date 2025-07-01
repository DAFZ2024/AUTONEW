/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../**/templates/**/*.html',
    '../**/static/**/*.js',
    '../../**/static/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
      },
      colors: {
        'primary': {
          DEFAULT: '#667eea',
          50: '#f0f3ff',
          100: '#e0e8ff',
          500: '#667eea',
          600: '#5a6fd8',
          700: '#764ba2',
        },
        'secondary': {
          DEFAULT: '#764ba2',
          500: '#764ba2',
        }
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-decoration-1': 'linear-gradient(45deg, #667eea, #764ba2)',
        'gradient-decoration-2': 'linear-gradient(45deg, #f093fb, #f5576c)',
      },
      animation: {
        'rotate': 'rotate 20s linear infinite',
        'rotate-reverse': 'rotate 25s linear infinite reverse',
        'float': 'float 6s ease-in-out infinite',
        'spin-slow': 'spin 1s linear infinite',
        'slideIn': 'slideIn 0.3s ease-out',
      },
      keyframes: {
        rotate: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        float: {
          '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
          '33%': { transform: 'translate(30px, -30px) rotate(120deg)' },
          '66%': { transform: 'translate(-20px, 20px) rotate(240deg)' },
        },
        slideIn: {
          'from': {
            opacity: '0',
            transform: 'translateY(-10px)',
          },
          'to': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
      },
      boxShadow: {
        'custom': '0 20px 60px rgba(0, 0, 0, 0.1)',
        'button': '0 4px 15px rgba(102, 126, 234, 0.3)',
        'button-hover': '0 8px 25px rgba(102, 126, 234, 0.4)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
