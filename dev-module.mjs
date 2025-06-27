#!/usr/bin/env node

import inquirer from 'inquirer';
import simpleGit from 'simple-git';
import { execSync } from 'child_process';
import chalk from 'chalk';

const git = simpleGit();
const ORIGIN = 'https://github.com/provoware/TOOL.git';

async function main() {
  console.clear();
  console.log(chalk.blue.bold('🛠 Provoware TOOL – Entwicklermodul\n'));

  const { action } = await inquirer.prompt([{
    type: 'list',
    name: 'action',
    message: 'Wähle eine Aktion:',
    choices: [
      { name: '1) Repository klonen', value: 'clone' },
      { name: '2) Erstes Setup ausführen', value: 'setup' },
      { name: '3) Dokumentation ansehen', value: 'docs' },
      { name: '4) Smoke-Test (Chromium) starten', value: 'test' },
      { name: '5) CI/CD-Beispiel generieren', value: 'ci' },
      { name: '6) Haupt-GUI starten', value: 'startgui' },
      new inquirer.Separator(),
      { name: '✖ Beenden', value: 'exit' }
    ]
  }]);

  switch (action) {
    case 'clone':
      console.log(chalk.green('\n📥 Klone das Repository…'));
      await git.clone(ORIGIN);
      console.log(chalk.green('✔ Fertig! Ordner „TOOL“ ist angelegt.\n'));
      break;

    case 'setup':
      console.log(chalk.green('\n⚙️  Führe Erst-Setup aus…'));
      execSync('bash scripts/auto_setup_validate.sh', { stdio: 'inherit' });
      console.log(chalk.green('\n✔ Setup erledigt.\n'));
      break;

    case 'docs':
      console.log(chalk.yellow('\n📖 Dokumentation im docs/-Ordner:\n'));
      console.log(' • docs/anforderungsanalyse.md');
      console.log(' • docs/funktions_elementanalyse.md');
      console.log(' • docs/gui_barrierefreiheits_audit.md\n');
      break;

    case 'test':
      console.log(chalk.green('\n🚀 Starte Smoke-Test (Chromium)…'));
      execSync('npx playwright test --project=chromium', { stdio: 'inherit' });
      console.log(chalk.green('\n✔ Smoke-Test durchgelaufen.\n'));
      break;

    case 'ci':
      console.log(chalk.magenta('\n🤖 GitHub Actions CI-Beispiel:\n'));
      console.log(`
name: CI

on: [push]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with: node-version: '18'
      - run: npm install
      - run: npm run lint
      - run: npm test
`);
      console.log(chalk.magenta('→ Speichere das als .github/workflows/ci.yml\n'));
      break;

    case 'startgui':
      console.log(chalk.green('\n🚀 Starte Haupt-GUI (Electron)…'));
      execSync('npm run start', { stdio: 'inherit' });
      console.log(chalk.green('\n✔ Haupt-GUI beendet.\n'));
      break;

    case 'exit':
      console.log(chalk.red('\n👋 Tschüss!'));
      process.exit(0);
  }

  // Pause & zurück ins Menü
  await inquirer.prompt([{ type: 'input', name: 'pause', message: 'Enter zum Zurück…' }]);
  main();
}

main();
