# Cute Language Support for VS Code

This extension provides syntax highlighting and editor configuration for Cute source files (`.ct`).

## Install locally

From this directory, package and install the extension:

```sh
cd editor/vscode-cute
npx --yes @vscode/vsce package
code --install-extension cute-language-0.1.0.vsix
```

Then open a `.ct` file. VS Code should show **Cute** in the language-mode selector.

The grammar recognizes Cute's keywords, declarations, types, comments, strings, characters, numbers (including hexadecimal and binary), builtins, operators, and delimiters.
