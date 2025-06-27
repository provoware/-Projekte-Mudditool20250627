#!/usr/bin/env bash

# 1) Prüfen, ob Git installiert ist
if ! command -v git &> /dev/null; then
  echo "🚨 Git ist nicht installiert. Bitte installiere Git und starte das Skript erneut."
  exit 1
fi

echo "👍 Git ist installiert."

# 2) Projekt-Verzeichnis auswählen
read -p "In welchem Verzeichnis soll gearbeitet werden? (Pfad eingeben, Standard: aktuelles Verzeichnis) " proj_dir
proj_dir="${proj_dir:-$(pwd)}"
cd "$proj_dir" || { echo "🚨 Verzeichnis nicht gefunden: $proj_dir"; exit 1; }
echo "📂 Arbeitsverzeichnis: $proj_dir"

# 3) Neu initialisieren oder klonen?
read -p "Repo klonen (c) oder neues Repo initialisieren (i)? [c/i] " action
if [[ "$action" =~ ^[cC]$ ]]; then
  read -p "Gib die HTTPS- oder SSH-URL des GitHub-Repos ein: " repo_url
  git clone "$repo_url" .
  echo "✅ Repo geklont."
else
  git init
  echo "✅ Neues Git-Repo initialisiert."
  read -p "Gib die GitHub-Remote-URL ein (z.B. git@github.com:User/Repo.git): " repo_url
  git remote add origin "$repo_url"
  echo "✅ Remote 'origin' gesetzt auf $repo_url"
fi

# 4) Dateien zum Commit auswählen
read -p "Alle Dateien zum Commit hinzufügen? [j/n] " add_all
if [[ "$add_all" =~ ^[jJ]$ ]]; then
  git add .
else
  echo "➕ Füge jetzt manuell hinzu via 'git add <Datei>'. Dann ENTER drücken."
  read -p "(Wenn fertig) ENTER drücken..."
fi

# 5) Commit mit Nachricht
read -p "Commit-Nachricht eingeben: " msg
git commit -m "$msg"
echo "📝 Commit erstellt: $msg"

# 6) Backup-Branch anlegen
timestamp=$(date +%Y%m%d%H%M%S)
backup_branch="backup-$timestamp"
git branch "$backup_branch"
echo "🔖 Backup-Branch erstellt: $backup_branch"

# 7) Änderungen pushen
read -p "Branch jetzt zum Remote pushen? [j/n] " do_push
if [[ "$do_push" =~ ^[jJ]$ ]]; then
  git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
  echo "☁️ Branch gepusht und als Tracking-Branch gesetzt."
fi

# 8) Änderungen vom Remote holen
read -p "Remote-Änderungen holen: fetch (f), pull (p) oder nichts (n)? [f/p/n] " dl
if [[ "$dl" =~ ^[fF]$ ]]; then
  git fetch origin
  echo "📥 fetch abgeschlossen – deine Branches unverändert."
elif [[ "$dl" =~ ^[pP]$ ]]; then
  git pull --rebase origin "$(git rev-parse --abbrev-ref HEAD)"
  echo "📥 pull mit Rebase abgeschlossen."
else
  echo "🚫 Kein Download durchgeführt."
fi

echo "🎉 Fertig! Dein Projekt ist sicher hoch- und runterladbar – ohne Altes zu zerstören."
