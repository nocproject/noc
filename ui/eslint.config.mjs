// @ts-check

import eslint from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      "indent": [
        "error",
        2,
        {
          "SwitchCase": 1,
          "ArrayExpression": "first",
          "ObjectExpression": "first",
          "MemberExpression": "off",
          "FunctionDeclaration": {
            "parameters": "first",
            "body": 1,
          },
          "CallExpression": {
            "arguments": "first",
          },
          "outerIIFEBody": 0,
          "ignoreComments": false,
          "flatTernaryExpressions": true,
          "VariableDeclarator": 1,
        },
      ],
      "comma-dangle": [
        "error",
        "always-multiline",
      ],
      "space-before-function-paren": [
        "error",
        "never",
      ],
      "keyword-spacing": [
        "error",
        {
          "after": false,
          "overrides": {
            "return": {
              "after": true,
            },
            "var": {
              "after": true,
            },
            "case": {
              "after": true,
            },
            "from": {
              "after": true,
            },
            "import": {
              "after": true,
            },
            "const": {
              "after": true,
            },
            "let": {
              "after": true,
            },
          },
        },
      ],
      "key-spacing": [
        "error",
        {
          "afterColon": true,
        },
      ],
      "object-curly-spacing": [
        "error",
        "never",
        {
          "objectsInObjects": true,
        },
      ],
      "space-in-parens": [
        "error",
        "never",
      ],
      "space-before-blocks": [
        "error",
        "never",
      ],
      "quotes": ["error", "double", {"avoidEscape": true, "allowTemplateLiterals": true}],
      "no-multi-spaces": "error",
      // '@typescript-eslint/no-unsafe-argument': 'error',
      // '@typescript-eslint/no-unsafe-assignment': 'error',
      // '@typescript-eslint/no-unsafe-call': 'error',
      // '@typescript-eslint/no-unsafe-member-access': 'error',
      // '@typescript-eslint/no-unsafe-return': 'error',
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        "Ext": "readonly",
        "NOC": "readonly",
        "__": "readonly",
        "Viz": "readonly",
        "joint": "readonly",
        "L": "readonly",
      },
    },
  },
);
