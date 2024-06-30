/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/static/**/*.js',
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1D4ED8',
        secondary: '#9333EA',
        background: {
          light: '#F3F4F6',
          dark: '#111111',
        },
        text: {
          light: '#1F2937',
          dark: '#111111',
        },
      },
    },
  },
  plugins: [
    require("flowbite/plugin")
  ]
}
