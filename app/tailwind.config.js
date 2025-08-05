/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}"],
  purge: false,
  theme: {
    extend: {
      colors: {
      "primary": "#186FD4",
    },
    },
    container: {
      center: true,
      padding: {
        DEFAULT: '15px',
        'md': '25px'
      }
    },
  },
  plugins: [],
}

