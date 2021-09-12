module.exports = {
  //mode: 'jit',
  purge: {
    enabled: true,
    content: ['../main/templates/**/*.html'],
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    space: {
      md: '1.25rem',
    },
    minHeight: {
      '44': '11rem',
    },
    
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}