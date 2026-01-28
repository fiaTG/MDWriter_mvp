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

**Hauptkomponente: `MarkdownField`**

```javascript
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class MarkdownField extends Component {
    setup() {
        this.state = useState({
            value: this.props.record.data[this.props.name] || "",
        });

        // Debug-Output für Entwicklung
        console.log("MarkdownField mounted", {
            name: this.props.name,
            value: this.state.value,
            readonly: this.props.readonly
        });

        // KRITISCHER FIX: Entferne overflow-Constraints vom Form View
        // Dies verhindert, dass der Editor außerhalb des sichtbaren Bereichs ist
        setTimeout(() => {
            const formView = document.querySelector('.o_form_view');
            const formSheet = document.querySelector('.o_form_sheet');
            const formSheetBg = document.querySelector('.o_form_sheet_bg');

            if (formView) {
                formView.style.overflow = 'visible';
                console.log('Fixed form view overflow');
            }
            if (formSheet) {
                formSheet.style.overflow = 'visible';
                formSheet.style.minHeight = '800px';
                console.log('Fixed form sheet overflow');
            }
            if (formSheetBg) {
                formSheetBg.style.overflow = 'visible';
                console.log('Fixed form sheet bg overflow');
            }
        }, 100);
    }

    _onInput(ev) {
        const value = ev.target.value;
        this.state.value = value;
        this.props.record.update({ [this.props.name]: value });
    }
}

MarkdownField.template = "markdown_editor.MarkdownField";
MarkdownField.props = {
    record: Object,
    name: String,
    readonly: { type: Boolean, optional: true },
    id: { type: [String, Number], optional: true },
};
MarkdownField.displayName = "Markdown Editor";

// Widget im Field Registry registrieren
registry.category("fields").add("markdown_editor", {
    component: MarkdownField,
});
```

**Wichtige Änderungen (v1.0.8):**
- Overflow-Fix mit `setTimeout` für Form View Container
- Debug-Logging beim Mounten der Komponente
- Props-Definition mit `readonly` und `id` Support
- Reactive Binding über `t-model` statt `t-att-value`

### 4.2 Template: markdown_editor_templates.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="markdown_editor.MarkdownField">
        <div class="o_markdown_editor" style="width: 100%; display: flex;">
            <textarea
                t-ref="editor"
                class="o_input"
                t-on-input="_onInput"
                t-model="state.value"
                placeholder="Geben Sie hier Ihren Markdown‑Text ein..."
            />
            <div class="o_markdown_preview">
                <!-- Vorschau: Der Markdown‑Inhalt wird hier angezeigt. -->
                <t t-esc="state.value"/>
            </div>
        </div>
    </t>
</templates>
```

**Wichtige Änderungen (v1.0.8):**
- Inline-Style `width: 100%; display: flex;` für bessere Sichtbarkeit
- `t-model` Binding für reaktive Zwei-Wege-Datenbindung
- `t-esc` statt `t-raw` für XSS-Schutz (plain text preview)
- Vereinfachte Struktur ohne Toolbar (Split-View only)

### 4.3 Styling: markdown_editor.scss

```scss
// Styling für den Markdown Editor
.o_markdown_editor {
    display: flex !important;
    flex-direction: row !important;
    min-height: 600px !important;
    height: 600px !important;
    width: 100% !important;
    max-width: 100% !important;
    border: 1px solid var(--border-color);
    box-sizing: border-box !important;
    flex: 1 1 auto !important;
}

.o_markdown_editor textarea.o_input {
    flex: 1;
    min-width: 0; // Flex-Bug-Fix
    padding: 0.75rem;
    border: none;
    resize: none;
    outline: none;
    background: var(--o-input-bg);
    color: var(--o-input-color);
    font-family: monospace;
    font-size: 14px;
    line-height: 1.5;
}

.o_markdown_preview {
    flex: 1;
    min-width: 0; // Flex-Bug-Fix
    padding: 0.75rem;
    border-left: 1px solid var(--border-color);
    overflow-y: auto;
    white-space: pre-wrap;
    background: var(--o-background-color);
    color: var(--o-text-color);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    line-height: 1.5;
}

// KRITISCHER FIX: Verhindere overflow-Probleme im Form View
.o_form_view:has(.o_markdown_editor) {
    overflow: visible !important;
}

.o_form_view .o_form_sheet:has(.o_markdown_editor) {
    overflow: visible !important;
}

.o_form_sheet:has(.o_markdown_editor) {
    min-height: 800px !important;
}

// Backup für Browser ohne :has() Support
body:has(.o_markdown_editor) {
    .o_form_view {
        overflow: visible !important;

        .o_form_sheet_bg {
            overflow: visible !important;
        }

        .o_form_sheet {
            overflow: visible !important;
            min-height: 800px !important;
        }
    }
}

// Field-Widget Container
.o_field_widget.o_field_markdown_editor {
    width: 100% !important;
    display: block !important;
}

.o_field_widget[name="content_md"] {
    width: 100% !important;
    max-width: none !important;
    flex: 1 1 100% !important;
}
```

**Wichtige Änderungen (v1.0.8):**
- Aggressive `!important` Regeln für zuverlässige Darstellung
- `:has()` Selektoren für moderne Browser (Overflow-Fix)
- `min-width: 0` gegen bekannten Flexbox-Bug
- Backup-Regeln für Browser ohne `:has()` Support
- Odoo-spezifische CSS-Variablen für Theming

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
| Editor unsichtbar / nur 50px breit | **Ursache:** Form View `overflow: auto` versteckt Editor. **Fix:** JavaScript overflow-reset in `markdown_editor.js` (v1.0.8), CSS `:has()` Selektoren. DevTools öffnen als Workaround zeigt Editor temporär |
| Editor nur mit DevTools sichtbar | Gleiche Ursache wie oben. Assets neu kompilieren: `odoo-bin -u markdown_editor`, Hard-Refresh Browser (`Ctrl+Shift+R`) |
| PDF-Generation schlägt fehl | `wkhtmltopdf` installiert? `which wkhtmltopdf` prüfen |
| OWL-Komponente lädt nicht | Browser Console (F12) auf JS-Fehler prüfen. Check: "MarkdownField mounted" Log vorhanden? |
| Versionierung funktioniert nicht | `_create_version()` wird nicht aufgerufen? Check Hooks |
| ACL-Fehler | Benutzer in korrekter Gruppe? `security/ir.model.access.csv` prüfen |
| Editor-Breite nicht 100% | CSS-Kaskade überschreibt Regeln. Prüfe mit DevTools computed styles. Notfall: Mehr `!important` in `markdown_editor.scss` |

### 8.2 Logging aktivieren

**Python Backend Logging:**
```python
import logging
_logger = logging.getLogger(__name__)

@api.model
def save_document(self, content):
    _logger.info(f'Saving document {self.id} with {len(content)} chars')
    # ...
```

Logs in Odoo-Logdatei: `/var/log/odoo/odoo.log`

**JavaScript Frontend Logging (v1.0.8):**
```javascript
// In markdown_editor.js automatisch aktiviert
console.log("MarkdownField mounted", {
    name: this.props.name,
    value: this.state.value,
    readonly: this.props.readonly
});
console.log('Fixed form view overflow');
console.log('Fixed form sheet overflow');
console.log('Fixed form sheet bg overflow');
```

Browser Console öffnen: `F12` → Console Tab

**Debug-Checklist bei Editor-Problemen:**
1. Console-Log "MarkdownField mounted" vorhanden? → Komponente lädt
2. Overflow-Fix Logs vorhanden? → JavaScript-Fix aktiv
3. Computed Style prüfen: `.o_markdown_editor` hat `width: 100%`?
4. Computed Style prüfen: `.o_form_view` hat `overflow: visible`?

---

## 9. Bekannte Einschränkungen

### 9.1 Editor-Layout (Stand v1.0.8)

**Problem:** Editor wird nur ~50px breit angezeigt, obwohl CSS `width: 100%` gesetzt ist.

**Ursache:**
- Odoo Form View Container haben standardmäßig `overflow: auto`
- Dies führt dazu, dass der Editor außerhalb des sichtbaren Bereichs gerendert wird
- Beim Öffnen der DevTools ändert sich das Layout → Editor wird sichtbar

**Teilweise Lösung (implementiert in v1.0.8):**
- JavaScript-Fix: Setzt `overflow: visible` beim Editor-Mount
- CSS-Fix: `:has()` Selektoren für moderne Browser
- Workaround: Editor ist jetzt grundsätzlich sichtbar, aber Breite noch nicht optimal

**Geplante Verbesserungen:**
- Weitere CSS-Optimierungen für volle Breite
- Untersuchung alternativer Layout-Strategien (Flexbox vs. Grid)
- Mögliche Anpassung der View-Struktur

**Workaround für Entwickler:**
```javascript
// Temporary fix: Manuell im Browser Console ausführen
document.querySelector('.o_form_view').style.overflow = 'visible';
document.querySelector('.o_form_sheet').style.overflow = 'visible';
```

### 9.2 Browser-Kompatibilität

**CSS `:has()` Selector:**
- Wird für Overflow-Fixes verwendet
- **Unterstützt:** Chrome 105+, Firefox 121+, Safari 15.4+
- **Nicht unterstützt:** Ältere Browser
- **Fallback:** JavaScript-Fix in `markdown_editor.js` funktioniert überall

### 9.3 Performance-Überlegungen

- Kein Markdown-Rendering im Frontend (v1.0.8)
- Preview zeigt nur Plain Text (`t-esc` statt `t-raw`)
- Für echtes Markdown-Rendering: Library wie `marked.js` oder `showdown.js` erforderlich
- Live-Preview kann bei großen Dokumenten (>10.000 Zeilen) langsam werden

---

## 10. Best Practices und Code-Standards

### 10.1 Python-Richtlinien

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

### 10.2 JavaScript/OWL-Richtlinien

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

### 10.3 SQL und Queries

Niemals Raw-SQL verwenden! Immer Odoo ORM:

```python
# ✅ RICHTIG
docs = self.env['x_md_document'].search([('owner_id', '=', user.id)])

# ❌ FALSCH
self.env.cr.execute("SELECT * FROM x_md_document WHERE owner_id = %s", (user.id,))
```

---

## 11. Ressourcen und Referenzen

- [Odoo 19 Entwicklerdokumentation](https://www.odoo.com/documentation/19.0)
- [OWL Framework](https://github.com/odoo/owl)
- [Markdown Syntax](https://commonmark.org/)
- [Projektrepository](https://github.com/fiaTG/MDWriter)
- [CSS :has() Browser Support](https://caniuse.com/css-has)

---

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---------|-------|---------|-------|
| 1.0.8 | 28.01.2026 | Editor Layout-Fix: Vollständige Sichtbarkeit durch Overflow-Fixes und Umstrukturierung | Timo |
| 1.0.7 | 27.01.2026 | **MEILENSTEIN 1:** Icon auf 2048x2048px hochskaliert, Modul erfolgreich deploybar | Timo |
| 1.0.6 | 27.01.2026 | .gitignore hinzugefügt für Python, IDEs, OS und Odoo-spezifische Dateien | Timo |
| 1.0.5 | 27.01.2026 | List View Fix: Ungültige Decoration-Attribute entfernt | Timo |
| 1.0.4 | 27.01.2026 | Form View Fix: Undefined Action Buttons entfernt, nur State-Selection | Timo |
| 1.0.3 | 27.01.2026 | Icon/Logo Integration: MDWriterLogo in Manifest und Views hinzugefügt | Timo |
| 1.0.2 | 27.01.2026 | Manifest-Fixes: Version zu 19.0.1.0.0, Python Boolean-Fehler behoben | Timo |
| 1.0.1 | 27.01.2026 | Odoo 19 View Migration: `<tree>` → `<list>`, Search View & Decorations hinzugefügt | Timo |
| 1.0.0 | 27.01.2026 | Initial Release | Timo |

**Detailierte Änderungen in 1.0.8:**
- **View-Struktur:** Editor-Field von Notebook auf Sheet-Root verschoben für bessere Sichtbarkeit
- **Layout-Fix:** Content-Field jetzt direkt unter Titel, oberhalb des Notebooks
- **Metadaten-Tab:** Eigentümer, Version, Timestamps in neues "Metadaten"-Tab ausgelagert
- **Overflow-Fix (JavaScript):** Automatisches Entfernen von `overflow: auto` auf Form-View-Containern beim Editor-Mount
- **Overflow-Fix (CSS):** Aggressive CSS-Regeln mit `:has()` Selektoren und `!important` für moderne Browser
- **Template-Binding:** Umstellung von `t-att-value` auf `t-model` für reaktive Zwei-Wege-Bindung
- **Inline-Styles:** Wrapper-Div und Editor-Element mit `width: 100%` für volle Breite
- **CSS-Regeln:** Full-Width Rules für `.o_field_widget`, `.o_markdown_editor` mit `!important`
- **Flexbox-Fixes:** `min-width: 0` für Flex-Children gegen bekannten Flexbox-Bug
- **Debug-Logging:** Console-Logs für Mount-Events und Overflow-Fixes zur Fehlersuche
- **Browser-Kompatibilität:** Backup-CSS-Regeln für Browser ohne `:has()` Support
- **Problem:** Editor war ohne DevTools unsichtbar (50px breit) → Ursache: Form View `overflow: auto`
- **Status:** Editor jetzt sichtbar, aber noch Optimierungspotenzial bei der Breite

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
**Letzte Aktualisierung:** 28.01.2026
**Nächste Überprüfung:** Quartalsweise