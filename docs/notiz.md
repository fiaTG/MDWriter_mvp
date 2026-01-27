# Odoo.sh Instanz Setup - Anleitung

## Voraussetzungen

- GitHub-Account mit eigenem Repository
- Odoo.sh Account (kostenlos unter https://www.odoo.sh/)
- SSH-Keys konfiguriert

## Schritt 1: GitHub Repository vorbereiten

### 1.1 Repository erstellen
```bash
# Auf GitHub neues Public Repository erstellen
# Beispiel: https://github.com/fiaTG/MDWriter
```

### 1.2 SSH-Key für GitHub generieren (falls nicht vorhanden)
```bash
ssh-keygen -t ed25519 -C "deine-email@github.com"
# Key-Pfad: ~/.ssh/id_ed25519
```

### 1.3 Public Key zu GitHub hinzufügen
1. GitHub → Settings → SSH and GPG keys
2. New SSH key
3. Content von `~/.ssh/id_ed25519.pub` kopieren
4. Title: "Odoo.sh Development"
5. Speichern

### 1.4 Repository im odoo Branch strukturieren
```
MDWriter/
├── markdown_editor/          # Odoo Modul
│   ├── __manifest__.py
│   ├── models/
│   ├── views/
│   ├── static/
│   └── security/
├── .gitignore               # Python/Odoo Standard
├── README.md
└── __init__.py              # Optional
```

## Schritt 2: Odoo.sh Setup

### 2.1 Odoo.sh Instanz erstellen
1. Login auf https://www.odoo.sh/
2. "Create Project" oder "New Database"
3. Optionen:
   - **Project Name:** MDWriter Development
   - **Branch:** main (oder custom)
   - **Version:** Odoo 19
   - **Database Name:** mdwriter-dev

### 2.2 GitHub Repository verbinden

#### Option A: Via SSH (empfohlen)
1. Odoo.sh Dashboard → Repository Settings
2. "Connect to GitHub"
3. SSH URL eingeben:
   ```
   git@github.com:fiaTG/MDWriter.git
   ```
4. SSH-Key zu Odoo.sh hinzufügen:
   - Odoo.sh SSH-Key kopieren (Dashboard → SSH Keys)
   - Zu GitHub hinzufügen (Settings → Deploy Keys)
   - Write access aktivieren

#### Option B: Via HTTPS
```
https://github.com/fiaTG/MDWriter.git
```
(Weniger sicher, aber schneller für Public Repos)

### 2.3 Branch konfigurieren
1. Repository Settings → Branches
2. Hauptbranch: `main`
3. Staging/Production Branch: optional

## Schritt 3: Instanz initialisieren

### 3.1 Modules installieren
1. Odoo.sh Console öffnen (Terminal Icon)
2. Standard Odoo-Modul installieren:
   ```bash
   # Im Odoo Environment
   odoo-bin -d mdwriter-dev -i markdown_editor --stop-after-init
   ```

### 3.2 Dependencies installieren (falls benötigt)
```bash
pip install markdown2 weasyprint
```

### 3.3 Database initialisieren
1. Dashboard → Database → Initialize
2. Wartet auf Module-Installation
3. Automatisch bei Git-Commit

## Schritt 4: Entwicklungs-Workflow

### 4.1 Lokal entwickeln
```bash
# Clone Repo lokal
git clone git@github.com:fiaTG/MDWriter.git
cd MDWriter

# Branch erstellen
git checkout -b feature/neue-funktion

# Code ändern
# ...

# Commit & Push
git add .
git commit -m "feat: neue Feature hinzugefügt"
git push origin feature/neue-funktion
```

### 4.2 Odoo.sh automatische Updates
- Jeder Push zu `main` triggert automatisches Update
- Odoo.sh pullt automatisch
- Module werden neu installiert/upgedatet
- Database wird migriert

### 4.3 Pull Requests mergen
```bash
# Feature Branch → Main
git checkout main
git pull origin main
git merge feature/neue-funktion
git push origin main
```

## Schritt 5: Debugging & Logs

### 5.1 Logs anschauen
1. Odoo.sh Dashboard → Logs
2. Real-time Monitoring
3. Filter nach Module: `markdown_editor`

### 5.2 Database-Shell
```bash
# Odoo.sh Console
psql -U odoo -d mdwriter-dev
```

### 5.3 Odoo Shell
```bash
odoo-bin shell -d mdwriter-dev
# Python REPL mit Odoo API
```

## Schritt 6: Security & Keys

### 6.1 SSH-Keys bei Odoo.sh
1. Settings → SSH Keys
2. Eigene SSH-Keys verwalten
3. Public Key zu GitHub Deploy Keys hinzufügen

### 6.2 Database Backup
1. Dashboard → Backups
2. Automatisch täglich
3. Manual Backup erstellen vor größeren Changes

### 6.3 .gitignore Setup
```
# .gitignore für Odoo
*.pyc
__pycache__/
*.egg-info/
.DS_Store
*.swp
*.swo
*~
.vscode/
.idea/
node_modules/
```

## Schritt 7: Produktion (Optional)

### 7.1 Production Branch
```bash
git checkout -b production
# oder via GitHub: create branch `production`
```

### 7.2 Odoo.sh Production Instanz
1. Separate Instanz erstellen für Production
2. Branch: `production`
3. Separate Database
4. Regelmäßige Backups

### 7.3 Deployment Pipeline
```
Development (main) → Staging (dev) → Production (production)
     ↓                   ↓              ↓
  Testing          Testing         Live
```

## Tipps & Best Practices

### Git Workflow
- Feature Branches für neue Features
- Pull Requests für Code Review
- Main Branch = Stable Version
- Production Branch = Live Version

### Odoo.sh Limits
- Storage: Je nach Plan (meist 1-10GB)
- Memory: Automatisch skalierend
- Databases: Unbegrenzt pro Account
- Modules: Unbegrenzt

### Security Checklist
- ✅ SSH-Keys konfiguriert
- ✅ Deploy Keys zu GitHub
- ✅ .gitignore korrekt
- ✅ Sensitive Data nicht in Git
- ✅ Database Backups aktiviert
- ✅ Access Control konfiguriert

### Troubleshooting

**Problem: Module wird nicht installiert**
```bash
# Force reinstall
odoo-bin -d mdwriter-dev -i markdown_editor --force-reinstall
```

**Problem: Git-Push triggert kein Update**
- Deploy Key Check
- Branch richtig konfiguriert?
- SSH-Key im GitHub hinterlegt?

**Problem: Database Migration fehlgeschlagen**
- Logs checken
- Letzte Version in Git für Rollback
- Support kontaktieren

## Ressourcen

- [Odoo.sh Dokumentation](https://www.odoo.sh/documentation)
- [GitHub Deploy Keys](https://docs.github.com/en/developers/overview/managing-deploy-keys)
- [Odoo 19 Entwickler-Docs](https://www.odoo.com/documentation/19.0)

---

**Hinweis:** Diese Anleitung ist für MDWriter Odoo 19 Module optimiert.
