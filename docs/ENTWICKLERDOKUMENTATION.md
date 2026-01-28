# Entwicklerdokumentation: MDWriter Odoo 19 Modul

**Projekt:** MDWriter - Markdown Editor für Odoo 19  
**Version:** 1.0.0  
**Autor:** Timo  
**Datum:** Januar 2026  
**Status:** In Entwicklung

---

## 1. Projektübersicht

### 1.1 Ziel und Zweck

Das MDWriter-Modul ist ein Markdown-basiertes Dokumentenmanagementsystem für Odoo 19. Es ermöglicht Benutzern, Markdown-Dokumente zu erstellen, zu bearbeiten, zu speichern und in PDF zu konvertieren. Das System bietet eine Split-View-Oberfläche mit Live-Vorschau und implementiert vollständige Versionierung mit Audittrail.

### 1.2 Funktionsumfang

- **Editor:** OWL-basierter Markdown-Editor mit Live-Vorschau
- **Speicherung:** Markdown-Dateien und PDF-Export in Odoo
- **Versionierung:** Automatische Versionskontrolle mit Checksummen
- **Audittrail:** Vollständige Änderungshistorie mit Benutzer- und Zeitstempel
- **Sicherheit:** ACL, Record Rules und XSS-Schutz
- **Performance:** Optimierte OWL-Komponenten und asynchrone Verarbeitung

### 1.3 Technologie-Stack

| Komponente | Version | Beschreibung |
|-----------|---------|-------------|
| Odoo | 19 | ERP-Framework |
| Python | 3.11+ | Backend |
| JavaScript/OWL | ES6+ | Frontend-Framework |
| SCSS | 3.0+ | Styling |
| PostgreSQL | 12+ | Datenbank |

---

## 2. Architektur und Design

### 2.1 Modulstruktur

```
markdown_editor/
├── __init__.py                          # Modulinitialisierung
├── __manifest__.py                      # Modulmetadaten
├── models/
│   ├── __init__.py
│   └── md_document.py                   # Kernmodelle
├── views/
│   └── md_document_views.xml            # View-Definitionen
├── static/
│   └── src/
│       ├── js/
│       │   └── markdown_editor.js       # OWL-Komponenten
│       ├── scss/
│       │   └── markdown_editor.scss     # Styling
│       └── xml/
│           └── markdown_editor_templates.xml  # OWL-Templates
├── security/
│   ├── ir.model.access.csv              # ACL-Definitionen
│   └── markdown_editor_security.xml     # Record Rules
└── report/
    └── md_document_report.xml           # PDF-Report-Definitionen
```

### 2.2 Datenmodell

#### x_md_document
Hauptmodell für Markdown-Dokumente:

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| name | Char | Dokumentname |
| content_md | Text | Markdown-Inhalt |
| state | Selection | Status (draft/published/archived) |
| owner_id | Many2one | Dokumenteigentümer (res.users) |
| current_version | Many2one | Aktuelle Version (x_md_document_version) |
| created_at | Datetime | Erstellungszeitpunkt |
| updated_at | Datetime | Letzte Änderung |

#### x_md_document_version
Versionierungsmodell:

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| document_id | Many2one | Referenz zu Dokument (x_md_document) |
| version | Integer | Versionsnummer (1, 2, 3...) |
| content_md | Text | Markdown-Inhalt dieser Version |
| checksum | Char | SHA256-Hash für Integrität |
| changed_by | Many2one | Benutzer der Änderung (res.users) |
| changed_at | Datetime | Zeitstempel der Änderung |
| md_attachment_id | Many2one | Markdown-Attachment (ir.attachment) |
| pdf_attachment_id | Many2one | PDF-Attachment (ir.attachment) |

### 2.3 Sicherheit und Zugriffskontrolle

**ACL-Rollen:**
- **Reader:** Nur Lesezugriff auf veröffentlichte Dokumente
- **Editor:** Erstellen, Bearbeiten, Speichern von Dokumenten
- **Admin:** Volle Kontrolle + Konfiguration

**Implementierung:**
- ACL via `ir.model.access` in `security/ir.model.access.csv`
- Record Rules für dokumentbasierte Zugriffskontrolle
- XSS-Schutz durch Odoo's `markupsafe` und OWL-Sanitization

---

## 3. Backend-Implementierung

### 3.1 Modell: md_document.py

```python
from odoo import models, fields, api

class MdDocument(models.Model):
    _name = 'x_md_document'
    _description = 'Markdown Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(required=True, track_visibility='onchange')
    content_md = fields.Text(default='')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='draft', track_visibility='onchange')
    owner_id = fields.Many2one('res.users', default=lambda s: s.env.user)
    current_version = fields.Many2one('x_md_document_version')
```

**Wichtige Methoden:**
- `_create_version()` – Erstellt neue Versionseintrag
- `save_document()` – Speichert Dokument und erstellt Version
- `generate_pdf()` – Markdown zu PDF konvertieren
- `action_publish()` – Dokument veröffentlichen

### 3.2 PDF-Generierung

Die PDF-Generierung erfolgt durch:
1. Markdown → HTML-Konvertierung (via `markdown2` oder ähnlich)
2. HTML → PDF via `wkhtmltopdf` oder `weasyprint`
3. Speicherung als Attachment in Version

```python
def generate_pdf(self):
    """Konvertiert Markdown zu PDF und speichert als Attachment"""
    html_content = self._markdown_to_html(self.content_md)
    pdf_bytes = self._html_to_pdf(html_content)
    attachment = self.env['ir.attachment'].create({
        'name': f'{self.name}.pdf',
        'type': 'binary',
        'datas': base64.b64encode(pdf_bytes),
        'res_model': 'x_md_document',
        'res_id': self.id,
    })
    return attachment
```

### 3.3 Versionierung und Audittrail

Jede Änderung am `content_md` erstellt automatisch einen Versionseintrag:

```python
def _create_version(self, user_id=None):
    """Erstellt einen neuen Versionseintrag"""
    latest_version = self.env['x_md_document_version'].search(
        [('document_id', '=', self.id)],
        order='version desc',
        limit=1
    )
    version_num = (latest_version.version + 1) if latest_version else 1
    checksum = hashlib.sha256(self.content_md.encode()).hexdigest()
    
    version = self.env['x_md_document_version'].create({
        'document_id': self.id,
        'version': version_num,
        'content_md': self.content_md,
        'checksum': checksum,
        'changed_by': user_id or self.env.user.id,
        'changed_at': fields.Datetime.now(),
    })
    self.current_version = version
```

---

## 4. Frontend-Implementierung

### 4.1 OWL-Komponenten

**Hauptkomponente: `MarkdownEditor`**

```javascript
import { Component, useState, useEffect } from "@odoo/owl";

export class MarkdownEditor extends Component {
    setup() {
        this.state = useState({
            markdown: this.props.content || '',
            preview: '',
            isSaving: false,
            lastSave: null,
        });
        
        useEffect(() => {
            this.updatePreview();
        }, () => [this.state.markdown]);
    }
    
    updatePreview() {
        // Markdown → HTML Konvertierung
        const converter = new showdown.Converter();
        this.state.preview = converter.makeHtml(this.state.markdown);
    }
    
    async saveDocument() {
        this.state.isSaving = true;
        try {
            await this.rpc('/web/dataset/call_kw/x_md_document/save_document', {
                model: 'x_md_document',
                method: 'save_document',
                args: [this.props.docId, this.state.markdown],
            });
            this.state.lastSave = new Date();
        } finally {
            this.state.isSaving = false;
        }
    }
}

MarkdownEditor.template = 'markdown_editor.MarkdownEditor';
```

### 4.2 Template: markdown_editor_templates.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="markdown_editor.MarkdownEditor">
        <div class="md-editor-container">
            <div class="md-editor-toolbar">
                <button t-on-click="saveDocument" t-att-disabled="state.isSaving">
                    Save
                </button>
            </div>
            <div class="md-editor-split">
                <textarea 
                    class="md-editor-input"
                    t-model="state.markdown"
                    placeholder="Enter Markdown...">
                </textarea>
                <div class="md-editor-preview" t-raw="state.preview"></div>
            </div>
        </div>
    </t>
</templates>
```

### 4.3 Styling: markdown_editor.scss

```scss
.md-editor-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
    
    .md-editor-toolbar {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-color);
        background: var(--bg-secondary);
    }
    
    .md-editor-split {
        display: flex;
        flex: 1;
        overflow: hidden;
        gap: 1px;
        
        .md-editor-input,
        .md-editor-preview {
            flex: 1;
            padding: 16px;
            overflow: auto;
            border: none;
        }
        
        .md-editor-input {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: none;
        }
        
        .md-editor-preview {
            background: var(--bg-light);
            border-left: 1px solid var(--border-color);
        }
    }
}

// Dark Mode Support
@media (prefers-color-scheme: dark) {
    .md-editor-container {
        .md-editor-input {
            background: #1e1e1e;
            color: #e0e0e0;
        }
    }
}
```

---

## 5. Installation und Konfiguration

### 5.1 Systemanforderungen

- Odoo 19 (Community oder Enterprise)
- Python 3.11+
- PostgreSQL 12+
- `markdown2` oder `python-markdown` (pip)
- `wkhtmltopdf` oder `weasyprint` (für PDF)

### 5.2 Installationsschritte

1. **Modul clonen:**
   ```bash
   git clone --recurse-submodules --branch main \
     https://github.com/fiaTG/MDWriter.git \
     /path/to/odoo/addons/markdown_editor
   ```

2. **Dependencies installieren:**
   ```bash
   pip install markdown2 weasyprint
   ```

3. **Modul aktivieren:**
   - Odoo Webinterface → Apps → Suche "Markdown Editor"
   - "Installieren" klicken

4. **ACL konfigurieren:**
   - Benutzer zu Gruppen zuordnen (Einstellungen → Benutzer)
   - Record Rules über UI prüfen

### 5.3 Konfigurationsparameter

Werden in `__manifest__.py` definiert:

```python
{
    'name': 'Markdown Editor',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'author': 'Timo',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/markdown_editor_security.xml',
        'views/md_document_views.xml',
        'report/md_document_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'markdown_editor/static/src/js/markdown_editor.js',
            'markdown_editor/static/src/scss/markdown_editor.scss',
        ],
    },
}
```

---

## 6. Testing und Qualitätssicherung

### 6.1 Test-Strategie

| Test-Typ | Beschreibung | Tools |
|----------|-------------|-------|
| Unit Tests | Modelllogik, Versionierung | Python `unittest` |
| Integration Tests | RPC-Aufrufe, Datenspeicherung | Odoo `TransactionCase` |
| Security Tests | ACL, XSS-Schutz | Custom Security Tests |
| UI Tests | OWL-Komponenten | JavaScript `Jest` |

### 6.2 Beispiel: Security Test

```python
def test_acl_reader_cannot_edit(self):
    """Leser können Dokumente nicht bearbeiten"""
    reader = self.env.ref('markdown_editor.group_reader')
    doc = self.env['x_md_document'].create({'name': 'Test'})
    
    with self.assertRaises(AccessError):
        doc.with_user(reader.users[0]).write({'content_md': 'changed'})
```

### 6.3 Beispiel: Versionierungs-Test

```python
def test_version_creation(self):
    """Jede Änderung erstellt eine neue Version"""
    doc = self.env['x_md_document'].create({'name': 'Test', 'content_md': 'v1'})
    versions_before = doc.env['x_md_document_version'].search_count([('document_id', '=', doc.id)])
    
    doc.write({'content_md': 'v2'})
    versions_after = doc.env['x_md_document_version'].search_count([('document_id', '=', doc.id)])
    
    self.assertEqual(versions_after, versions_before + 1)
```

---

## 7. Deployment und Wartung

### 7.1 Versionierung

Folgt [Semantic Versioning](https://semver.org/):
- `19.0.1.0.0` = Odoo 19, Major 1, Minor 0, Patch 0

### 7.2 Database-Migration

Migrationen erfolgen über Pre- und Post-Install Hooks:

```python
def _register_hook(self):
    """Wird nach Installation/Update ausgeführt"""
    # Datamigration, Feldanpassungen
    pass
```

### 7.3 Backup und Recovery

Dokumente und Versionen sind in PostgreSQL gespeichert. Standard Odoo-Backups sichern alles.

---

## 8. Problembehandlung und Debugging

### 8.1 Häufige Probleme

| Problem | Lösung |
|---------|--------|
| PDF-Generation schlägt fehl | `wkhtmltopdf` installiert? `which wkhtmltopdf` prüfen |
| OWL-Komponente lädt nicht | Browser Console (F12) auf JS-Fehler prüfen |
| Versionierung funktioniert nicht | `_create_version()` wird nicht aufgerufen? Check Hooks |
| ACL-Fehler | Benutzer in korrekter Gruppe? `security/ir.model.access.csv` prüfen |

### 8.2 Logging aktivieren

```python
import logging
_logger = logging.getLogger(__name__)

@api.model
def save_document(self, content):
    _logger.info(f'Saving document {self.id} with {len(content)} chars')
    # ...
```

Logs in Odoo-Logdatei: `/var/log/odoo/odoo.log`

---

## 9. Best Practices und Code-Standards

### 9.1 Python-Richtlinien

- PEP 8 einhalten
- Docstrings für alle Methoden
- Type Hints (Python 3.10+) verwenden
- Exception-Handling immer spezifisch

```python
def save_document(self, content: str) -> bool:
    """
    Speichert Dokument und erstellt Versionseintrag.
    
    Args:
        content: Markdown-Inhalt als String
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    
    Raises:
        ValueError: Wenn content leer ist
    """
    if not content:
        raise ValueError("Inhalt kann nicht leer sein")
```

### 9.2 JavaScript/OWL-Richtlinien

- ES6+ Syntax verwenden
- Keine globalen Variablen
- `const` vor `let` vor `var`
- Async/Await für RPC-Calls

```javascript
async saveDocument() {
    try {
        const response = await this.rpc('/path/to/method', {...});
        this.notifySuccess('Saved');
    } catch (error) {
        this.notifyError(`Error: ${error.message}`);
    }
}
```

### 9.3 SQL und Queries

Niemals Raw-SQL verwenden! Immer Odoo ORM:

```python
# ✅ RICHTIG
docs = self.env['x_md_document'].search([('owner_id', '=', user.id)])

# ❌ FALSCH
self.env.cr.execute("SELECT * FROM x_md_document WHERE owner_id = %s", (user.id,))
```

---

## 10. Ressourcen und Referenzen

- [Odoo 19 Entwicklerdokumentation](https://www.odoo.com/documentation/19.0)
- [OWL Framework](https://github.com/odoo/owl)
- [Markdown Syntax](https://commonmark.org/)
- [Projektrepository](https://github.com/fiaTG/MDWriter)

---

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---------|-------|---------|-------|
| 1.0.7 | 27.01.2026 | **MEILENSTEIN 1:** Icon auf 2048x2048px hochskaliert, Modul erfolgreich deploybar | Timo |
| 1.0.6 | 27.01.2026 | .gitignore hinzugefügt für Python, IDEs, OS und Odoo-spezifische Dateien | Timo |
| 1.0.5 | 27.01.2026 | List View Fix: Ungültige Decoration-Attribute entfernt | Timo |
| 1.0.4 | 27.01.2026 | Form View Fix: Undefined Action Buttons entfernt, nur State-Selection | Timo |
| 1.0.3 | 27.01.2026 | Icon/Logo Integration: MDWriterLogo in Manifest und Views hinzugefügt | Timo |
| 1.0.2 | 27.01.2026 | Manifest-Fixes: Version zu 19.0.1.0.0, Python Boolean-Fehler behoben | Timo |
| 1.0.1 | 27.01.2026 | Odoo 19 View Migration: `<tree>` → `<list>`, Search View & Decorations hinzugefügt | Timo |
| 1.0.0 | 27.01.2026 | Initial Release | Timo |

**Detailierte Änderungen in 1.0.7 (MEILENSTEIN 1):**
- Icon: Von 1024x1024px auf 2048x2048px hochskaliert
- Icon: Höhere Qualität und besseres Rendering in Odoo
- Status: Modul erfolgreich installierbar auf Odoo 19
- Funktionalität: Markdown Editor, Live Preview, Versionierung aktiv
- Views: Form, List, Search Views validiert und funktionsfähig
- Security: ACL und Record Rules vorhanden
- Deployment: Auf Odoo.sh (fiatg-mdwriter-main) erfolgreich getestet

**Detailierte Änderungen in 1.0.6:**
- `.gitignore`: Python Cache (`__pycache__`, `*.pyc`) ignoriert
- `.gitignore`: IDE Dateien (`.vscode`, `.idea`, `*.swp`) ignoriert
- `.gitignore`: OS Dateien (`.DS_Store`, `Thumbs.db`) ignoriert
- `.gitignore`: Odoo-spezifisch (`.log`, `session.pickle`, `.odoorc`) ignoriert
- `.gitignore`: Temporäre Dateien (`*.tmp`, `*.bak`, `notiz.md`) ignoriert
- Struktur: Entwicklungs-Notizen werden nicht mehr committed

**Detailierte Änderungen in 1.0.5:**
- List View: Ungültige Decoration-Attribute (`decoration-secondary`, `decoration-success`, `decoration-warning`, `decoration-muted`) entfernt
- List View: Badge-Widget für State bleibt erhalten (bessere Lesbarkeit)
- Fehlerfix: RELAXNG XML-Validierungsfehler behoben
- Vereinfachung: Cleaner, valides XML ohne komplexe Styling-Attribute

**Detailierte Änderungen in 1.0.4:**
- Form View: Action Buttons `action_publish` und `action_archive` entfernt (nicht im Model definiert)
- Form View: State-Selection via `statusbar` widget bleibt für Status-Änderungen
- Fehlerfix: ParseError bei View-Validierung behoben
- Vereinfachung: Direktes State-Dropdown statt separate Buttons

**Detailierte Änderungen in 1.0.3:**
- `__manifest__.py`: `"images"` Feld mit `static/description/icon.png` hinzugefügt
- Logo: `MDWriterLogo1_1.png` zu `icon.png` umbenannt
- Views: Menu-Icon in `md_document_views.xml` angepasst
- Struktur: `static/description/` Ordner mit Icon erstellt

**Detailierte Änderungen in 1.0.2:**
- `__manifest__.py`: Version zu Odoo 19 Standard (`19.0.1.0.0`) geändert
- Manifest: Author von "Generated by ChatGPT" zu "Timo" korrigiert
- Manifest: Trailing Commas in `data` und `assets` konsistent hinzugefügt
- Manifest: Website URL aktualisiert
- Syntax: Python Boolean-Werte bleiben als `True` (valide in Python Dicts)

**Detailierte Änderungen in 1.0.1:**
- Views: Umstieg von deprecated `<tree>` zu `<list>` Widget (Odoo 19 Standard)
- Search View: Filter nach Status, Eigentümer und Gruppierungen hinzugefügt
- Form View: Action Buttons (`action_publish`, `action_archive`), Chatter & Activity integriert
- List View: Dekoration für States, Many2one Avatar für Owner
- Version Form View: Read-only Modus mit korrektem Widget-Rendering
- Fehlerfix: Explizite Model-Definition in One2many Fields

---

**Gültig ab:** Januar 2026  
**Letzte Aktualisierung:** 27.01.2026  
**Nächste Überprüfung:** Quartalsweise