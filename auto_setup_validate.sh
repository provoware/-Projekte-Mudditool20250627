#!/usr/bin/env bash
set -euo pipefail

SCRIPT_VERSION="1.0.4"
echo "▶ Running setup & validate script v${SCRIPT_VERSION}"

# 1) Im Projekt-Root?
if [[ ! -f package.json ]]; then
  echo "✗ package.json nicht gefunden. Initialisiere npm-Projekt..."
  npm init -y
fi

# 2) package.json updaten
echo "▶ Aktualisiere package.json..."
npm pkg set main=src/main.js
npm pkg set 'scripts.start'="electron ."
npm pkg set 'scripts.test:gui'="playwright test --project=chromium"

# 3) Dependencies installieren
echo "▶ Installiere Dependencies..."
npm install
npm install --save-dev electron @playwright/test playwright

# 4) Electron-Entry-Point anlegen
if [[ ! -f src/main.js ]]; then
  echo "▶ Erstelle src/main.js..."
  mkdir -p src
  cat > src/main.js << 'EOF'
const { app, BrowserWindow } = require('electron');
function createWindow() {
  const win = new BrowserWindow({ width: 800, height: 600, webPreferences: { nodeIntegration: true }});
  win.loadFile('index.html');
}
app.whenReady().then(createWindow);
EOF
fi

# 5) index.html anlegen
if [[ ! -f index.html ]]; then
  echo "▶ Erstelle index.html..."
  cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>MuddiTool</title></head>
<body><h1>Welcome to MuddiTool</h1></body>
</html>
EOF
fi

# 6) Playwright-Config für Chromium
echo "▶ Erstelle playwright.config.ts..."
cat > playwright.config.ts << 'EOF'
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'tests',
  timeout: 30 * 1000,
  expect: { timeout: 5000 },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
});
EOF

# 7) Chromium-Smoke-Test anlegen
echo "▶ Erstelle Chromium-Smoke-Test..."
mkdir -p tests/gui
cat > tests/gui/html.spec.ts << 'EOF'
import { test, expect } from '@playwright/test';
import path from 'path';

test('index.html lädt und zeigt den Titel', async ({ page }) => {
  const file = path.resolve(process.cwd(), 'index.html');
  await page.goto('file://' + file);
  await expect(page).toHaveTitle(/MuddiTool/);
});
EOF

# 8) Markdown-Linting (MD031 ignoriert)
if command -v markdownlint &> /dev/null; then
  echo "▶ Prüfe docs/*.md (MD031 deaktiviert)…"
  markdownlint --disable MD031 docs/*.md
  echo "  ✔ Markdown-Lint OK"
else
  echo "⚠ markdownlint nicht installiert — übersprungen."
fi

# 9) Chromium-Smoke-Test ausführen
echo "▶ Starte Chromium-Smoke-Test…"
if npx playwright test --project=chromium; then
  echo "✔ Playwright-Tests bestanden"
else
  echo "✖ Playwright-Tests fehlgeschlagen"
  exit 1
fi

echo "✅ Setup & Validate v${SCRIPT_VERSION} abgeschlossen."
