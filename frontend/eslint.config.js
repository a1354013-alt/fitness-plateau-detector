import js from '@eslint/js'
import globals from 'globals'
import vue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import tseslint from 'typescript-eslint'

export default [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      '.npm-cache/**',
      'coverage/**',
    ],
  },

  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...vue.configs['flat/recommended'],

  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
      },
    },
  },

  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      // Vue SFCs commonly use single-word component names for view files.
      'vue/multi-word-component-names': 'off',
      // Formatting rules are handled by tooling/PR review, not lint gates.
      'vue/max-attributes-per-line': 'off',
      'vue/attributes-order': 'off',
      'vue/attribute-hyphenation': 'off',
      'vue/html-indent': 'off',
      'vue/multiline-html-element-content-newline': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      // Test stubs and inline component fixtures are common in unit tests.
      'vue/one-component-per-file': 'off',
    },
  },

  {
    files: ['src/test/**/*', 'src/**/*.test.ts', 'src/**/*.spec.ts'],
    rules: {
      // Unit tests frequently stub Chart.js components as "Line"/"Bar".
      'vue/no-reserved-component-names': 'off',
    },
  },
]
