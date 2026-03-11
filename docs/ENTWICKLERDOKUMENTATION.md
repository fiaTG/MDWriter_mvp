# Entwicklerdokumentation: MDWriter Odoo 19 Modul

**Projekt:** MDWriter – Markdown Editor für Odoo 19
**Modulversion:** 19.0.1.1.0
**Autor:** Timo Giese
**Datum:** März 2026
**Status:** MVP vollständig implementiert

---

## 1. Projektübersicht

### 1.1 Ziel und Zweck

MDWriter ist ein Markdown-basiertes Dokumentenmanagementsystem als natives Odoo 19 Modul. Es ermöglicht Benutzern, strukturierte technische Dokumentationen direkt in Odoo zu erstellen, zu bearbeiten und zu verwalten – ohne externe Tools.

**Kernfunktionen:**
- Split-View-Editor: Markdown links, Live-Vorschau rechts
- Automatische Versionierung bei jeder Inhaltsänderung
- PDF-Export mit formatiertem Layout
- Zugriffsschutz über Odoo ACL und Record Rules
- Dark-Mode-kompatibel durch Odoo CSS-Variablen

### 1.2 Technologie-Stack

| Komponente | Technologie | Beschreibung |
|---|---|---|
| Backend | Python 3.11+ / Odoo ORM | Modelle, Versionierung, PDF-Rendering |
| Frontend | JavaScript / OWL (Odoo Web Library) | Editor-Komponente, Live-Preview |
| Markdown Frontend | markdown-it (lokal eingebunden) | Client-seitiges Rendering für Preview |
| Markdown Backend | mistune (Python) | Server-seitiges Rendering für PDF |
| Styling | SCSS | Split-View-Layout, Odoo-Integration |
| Datenbank | PostgreSQL | Dokumente, Versionen, Attachments |

---

## 2. Modulstruktur

```
markdown_editor/
├── __init__.py
├── __manifest__.py                         # Modulmetadaten, Assets, Dependencies
├── models/
│   ├── __init__.py
│   ├── md_document.py                      # x.md.document, x.md.document.version
│   └── md_document_diff.py                 # x.md.document.diff.wizard
├── views/
│   ├── md_document_views.xml               # Form-, List-, Search-, Version-Form-Views
│   └── md_document_diff_views.xml          # Diff-Wizard-View
├── static/
│   ├── description/
│   │   ├── icon.png                        # Modul-Icon
│   │   └── icon.svg
│   ├── lib/
│   │   ├── markdown-it.min.js              # Markdown-Renderer (lokal, kein CDN)
│   │   └── codemirror/
│   │       ├── codemirror.min.js           # Syntax-Editor
│   │       ├── markdown.min.js             # Markdown-Modus
│   │       └── codemirror.min.css
│   └── src/
│       ├── js/
│       │   └── markdown_editor.js          # OWL-Komponente MarkdownField
│       ├── scss/
│       │   └── markdown_editor.scss        # Split-View, Trendtec-Branding, Odoo-Fixes
│       ├── xml/
│       │   └── markdown_editor_templates.xml  # OWL-Template
│       └── fonts/
│           ├── Mulish/                     # UI-Font (Variable Font, TTF)
│           ├── JetBrains_Mono/             # Code-Font (Variable Font, TTF)
│           └── Inter/                      # Fallback UI-Font (Variable Font, TTF)
├── security/
│   ├── ir.model.access.csv                 # ACL-Definitionen
│   └── markdown_editor_security.xml        # Record Rules
├── report/
│   └── md_document_report.xml              # QWeb PDF-Template + Report-Action
└── tests/
    └── test_md_document.py                 # TransactionCase-Tests (Versionierung, ACL, Diff)
```

---

## 3. Datenmodell

### 3.1 x.md.document (Hauptmodell)

Dateiname: [models/md_document.py](../markdown_editor/models/md_document.py)

| Feld | Typ | Beschreibung |
|---|---|---|
| `name` | Char | Dokumenttitel (required) |
| `content_md` | Text | Markdown-Primärinhalt |
| `content_html` | Html | Gerendertes HTML (computed, sanitize=False) – für PDF |
| `state` | Selection | draft / published / archived |
| `owner_id` | Many2one → res.users | Eigentümer (default: aktueller User) |
| `version_ids` | One2many → x.md.document.version | Alle Versionen |
| `current_version` | Integer | Computed: höchste Versionsnummer |

Kein `mail.thread`-Inherit — das Modul nutzt bewusst kein Odoo-Chatter-System. Änderungsverfolgung erfolgt ausschließlich über das eigene Versionierungssystem (`x.md.document.version`).

### 3.2 x.md.document.version (Versionsmodell)

**Append-only** – bestehende Records werden niemals geändert.

| Feld | Typ | Beschreibung |
|---|---|---|
| `document_id` | Many2one → x.md.document | Verweis auf Dokument (ondelete=cascade) |
| `version` | Integer | Versionsnummer (1, 2, 3 …) |
| `content_md` | Text | Markdown-Inhalt dieser Version |
| `checksum` | Char (32) | MD5-Hash des Inhalts |
| `changed_by` | Many2one → res.users | Wer hat geändert |
| `changed_at` | Datetime | Wann wurde geändert |
| `md_attachment_id` | Many2one → ir.attachment | .md-Datei dieser Version |
| `pdf_attachment_id` | Many2one → ir.attachment | .pdf-Datei dieser Version |

### 3.3 Versionierungslogik

Versionierung wird automatisch ausgelöst durch:
- `create()` → erste Version wird bei Erstellung angelegt
- `write()` auf `content_md` → neue Version bei jeder Inhaltsänderung

```python
def write(self, vals):
    res = super().write(vals)
    if "content_md" in vals:
        self._create_version()
    return res
```

`_create_version()` ist in drei Methoden aufgeteilt (Single Responsibility):

| Methode | Aufgabe |
|---|---|
| `_create_md_attachment(record, content, version_num)` | Erstellt und speichert die `.md`-Datei als Odoo-Attachment |
| `_create_pdf_attachment(record, version_num)` | Rendert und speichert die `.pdf`-Datei (bei Fehler: `False`, kein Absturz) |
| `_create_version()` | Koordiniert beide Hilfsmethoden und legt den Version-Record an |

### 3.4 PDF-Rendering (Backend)

Das computed field `content_html` wandelt Markdown serverseitig in HTML um:

```python
from markupsafe import Markup

@api.depends("content_md")
def _compute_content_html(self):
    for doc in self:
        if _mistune_available:
            doc.content_html = Markup(mistune.html(doc.content_md))
        else:
            doc.content_html = Markup("<pre>%s</pre>") % (doc.content_md or "")
```

`Markup()` aus `markupsafe` kennzeichnet den HTML-String als sicher, damit `t-out` im QWeb-Template ihn unescaped rendert. `sanitize=False` ist bewusst gesetzt: `sanitize=True` würde Odoos `html_sanitize()` auslösen, was die `Markup`-Kennzeichnung entfernt — `t-out` würde den String danach escapen statt rendern (`<h1>` → `&lt;h1&gt;`). XSS-Schutz erfolgt stattdessen durch `html:false` in markdown-it (Frontend) und `mistune` (erzeugt kein schädliches HTML).

---

## 4. Frontend

### 4.1 OWL-Komponente: MarkdownField

Dateiname: [static/src/js/markdown_editor.js](../markdown_editor/static/src/js/markdown_editor.js)

Die Komponente wird als Odoo Field Widget registriert und über `widget="markdown_editor"` in Views eingebunden.

**Methoden:**

| Methode | Aufgabe |
|---|---|
| `setup()` | Initialisiert markdown-it, State, CodeMirror-Ref und Lifecycle-Callbacks |
| `_render(value)` | Wandelt Markdown-Text in sicheres HTML um (DRY: zentrale Render-Logik) |
| `_updateState(value)` | Aktualisiert State + speichert Wert im Odoo-Datensatz |
| `_onInput(ev)` | Fallback-Handler wenn CodeMirror nicht geladen wurde |

```javascript
_render(value) {
    return this.md ? markup(this.md.render(value)) : markup(value);
}

_updateState(value) {
    this.state.value = value;
    this.state.html = this._render(value);
    this.props.record.update({ [this.props.name]: value });
}
```

- `html: false` – eingebettetes HTML in Markdown wird escaped (XSS-Schutz)
- `markup()` aus `@odoo/owl` markiert den String als sicheres HTML für `t-out`
- `onMounted`: Guard-Clause verhindert Fehler wenn CodeMirror nicht verfügbar ist
- `onWillUnmount`: `cm.toTextArea()` räumt CodeMirror auf (kein Memory Leak)

**XSS-Schutz:** `markdown-it({ html: false })` escaped eingebettetes HTML. `markup()` signalisiert OWL, dass der Inhalt sicher gerendert werden darf — ohne `markup()` würde `t-out` den Inhalt escapen.

### 4.2 OWL-Template

Dateiname: [static/src/xml/markdown_editor_templates.xml](../markdown_editor/static/src/xml/markdown_editor_templates.xml)

```xml
<t t-name="markdown_editor.MarkdownField">
    <div class="o_markdown_editor">
        <textarea
            t-ref="editor"
            class="o_input"
            t-on-input="_onInput"
            t-model="state.value"
            placeholder="Geben Sie hier Ihren Markdown‑Text ein..."
        />
        <div class="o_markdown_preview">
            <t t-out="state.html"/>
        </div>
    </div>
</t>
```

`t-out` mit `markup()`-gewraptem State ist der korrekte Weg in Odoo 19 — `t-raw` ist deprecated. Ohne `markup()` würde `t-out` den HTML-String escapen statt rendern.

### 4.3 Styling (SCSS)

Dateiname: [static/src/scss/markdown_editor.scss](../markdown_editor/static/src/scss/markdown_editor.scss)

**Split-View:**
- `.o_markdown_editor` – `display: flex`, `height: 600px`
- Textarea (links) und Preview (rechts) je `flex: 1 1 50%`
- `white-space` ist bewusst **nicht** gesetzt – HTML-Rendering der Preview funktioniert korrekt

**Dark-Mode:** Alle Farbwerte nutzen Odoo CSS-Variablen (`var(--o-input-bg)`, `var(--o-background-color)`, `var(--o-text-color)`, `var(--border-color)`). Dark-Mode-Kompatibilität ist dadurch automatisch gegeben – Odoos eigener Theme-Switcher wird vollständig respektiert.

**Trendtec-Branding:**

Das Modul verwendet das Trendtec Corporate Design. Die Design-Tokens sind als CSS Custom Properties definiert:

```scss
:root {
    --tt-primary:      #97d21d;                          /* Trendtec Lime Green */
    --tt-primary-dark: #638a13;                          /* Hover / aktiver State */
    --tt-primary-dim:  rgba(151, 210, 29, 0.15);        /* Selektions-Hintergrund */
    --tt-radius:       12px;
    --tt-radius-sm:    6px;
    --tt-font-ui:      'Mulish', 'Inter', sans-serif;
    --tt-font-code:    'JetBrains Mono', monospace;
}
```

Alle Odoo-eigenen CSS-Variablen (`var(--o-*)`) bleiben als Fallback erhalten → Dark-Mode-Kompatibilität.

**Fonts:**

Alle Fonts liegen lokal unter `static/src/fonts/` — kein CDN.

| Font | Verwendung | Datei |
|---|---|---|
| Mulish | UI (Preview, Labels) | `Mulish/Mulish-VariableFont_wght.ttf` |
| JetBrains Mono | Code-Editor (CodeMirror) | `JetBrains_Mono/JetBrainsMono-VariableFont_wght.ttf` |
| Inter | Fallback Preview-Font | `Inter/Inter-VariableFont_opsz,wght.ttf` |

Variable Fonts decken alle Gewichte in einer Datei ab. Italic-Varianten sind jeweils eingebunden.

**Odoo Layout-Fixes:**
```scss
.o_form_view:has(.o_markdown_editor) {
    .o_form_sheet_bg {
        flex: 1 1 auto !important;      /* füllt den Renderer vollständig */
        max-width: 100% !important;     /* überschreibt Odoос max-width: 1400px */
    }
    .o_form_sheet {
        overflow: visible !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 24px !important;
    }
}
```

Ursachen:
- Odoo setzt auf `.o_form_sheet_bg` ein `max-width: 1400px`, das auf breiten Bildschirmen Leerraum rechts erzeugt.
- Da das Modul kein `mail.thread` verwendet, ist kein `flex-direction: column` Override nötig. Der Renderer läuft im natürlichen Row-Layout, `o_form_sheet_bg` füllt automatisch die volle Breite.

### 4.4 Markdown-Library

Dateiname: [static/lib/markdown-it.min.js](../markdown_editor/static/lib/markdown-it.min.js)

- Lokal eingebunden (kein CDN) – bewusste Entscheidung für Offline-Fähigkeit und Versionsstabilität
- Wird als globale Variable `window.markdownit` geladen (UMD-Bundle, kein ESM-Import)
- Keine zusätzlichen Plugins – nur Core-Funktionalität

---

## 5. Sicherheit

### 5.1 ACL (ir.model.access.csv)

| Rolle | Read | Write | Create | Delete |
|---|---|---|---|---|
| group_user (Dokument) | ✅ | ✅ | ✅ | ❌ |
| group_system (Dokument) | ✅ | ✅ | ✅ | ✅ |
| group_user (Version) | ✅ | ❌ | ❌ | ❌ |
| group_system (Version) | ✅ | ✅ | ✅ | ✅ |

Versionen sind für normale User read-only – Append-only-Charakter ist damit auf ACL-Ebene durchgesetzt.

### 5.2 Record Rules

- **Eigentümer-Regel:** User sehen und bearbeiten nur ihre eigenen Dokumente (`owner_id = user.id`)
- **Admin-Regel:** Admins haben Zugriff auf alle Dokumente (`1 = 1`)

### 5.3 XSS-Schutz

- **Frontend:** `markdown-it({ html: false })` – HTML in Markdown wird escaped
- **Backend:** `content_html` field mit `sanitize=False` – XSS-Schutz via mistune (kein schädliches HTML) + `Markup()` (signalisiert Vertrauenswürdigkeit an QWeb)
- **PDF-Template:** `t-out` auf `doc.content_html` – `Markup()` im Python-Code signalisiert dass der Inhalt sicher ist; `t-raw` ist in Odoo 19 deprecated

---

## 6. PDF-Export

### 6.1 Funktionsweise

1. User klickt im Form-Header auf "Als PDF exportieren"
2. `action_export_pdf()` gibt `report_action(self)` zurück → Odoo löst `ir.actions.report` aus
3. Report rendert QWeb-Template `markdown_editor.report_md_document`
4. Template ruft `doc.content_html` auf → computed field mit `mistune.html(content_md)` (als `Markup()`)
5. `wkhtmltopdf` konvertiert HTML → PDF; Dateiname = `${object.name}.pdf`

### 6.2 Template-Struktur

```xml
<template id="report_md_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">  <!-- Odoo-Standard-Header/Footer, stabile wkhtmltopdf-Basis -->
                <div class="page">
                    <h1><t t-esc="doc.name"/></h1>
                    <div t-out="doc.content_html"/>
                </div>
            </t>
        </t>
    </t>
</template>
```

`web.external_layout` ist der Odoo-Standard für PDF-Reports: korrekte HTML-Struktur für wkhtmltopdf, CSS im `<head>`, automatischer Odoo-Company-Header/Footer. `web.html_container` ist zusätzlich zwingend nötig — ohne ihn schlägt `_prepare_html` fehl (`IndexError: list index out of range`).

### 6.3 Python-Dependency: mistune

Eingebunden via `requirements.txt` im Repo-Root (wird von Odoo.sh automatisch installiert):
```
mistune
```

Fallback: Falls `mistune` nicht verfügbar, zeigt PDF den rohen Markdown-Text als `<pre>`.

---

## 7. Views

### 7.1 Form View

- Titel als `oe_title` (mit grüner Trendtec-Akzentlinie)
- Header-Buttons (kontextsensitiv, `invisible`-Attribut):
  - **Veröffentlichen** (sichtbar wenn draft oder archived)
  - **Zurück zu Entwurf** (sichtbar wenn published oder archived)
  - **Archivieren** (sichtbar wenn draft oder published)
  - **Markdown herunterladen** (sichtbar sobald eine Version existiert) → lädt `.md`-Datei der aktuellen Version herunter via `action_download_md()`
- State-Statusbar: draft → published → archived (nur Anzeige, Übergänge via Buttons)
- `content_md` mit `widget="markdown_editor"` (Split-View, CodeMirror links, Preview rechts)
- Notebook mit zwei Tabs:
  - **Metadaten:** owner_id, current_version, create_date, write_date
  - **Versionen:** Liste aller Versionen (read-only) mit Version, User, Datum, Checksum, Attachments; Button "Versionen vergleichen" öffnet Diff-Wizard; Klick auf Version öffnet Detail-Form mit "Wiederherstellen"-Button
- Kein Chatter (mail.thread bewusst nicht verwendet)

Die Statusübergänge rufen Python-Methoden auf `x.md.document` auf:
```python
def action_publish(self):    self.write({"state": "published"})
def action_set_draft(self):  self.write({"state": "draft"})
def action_archive_doc(self): self.write({"state": "archived"})
```

### 7.2 List View

Spalten: Name, Eigentümer (Avatar), Status (Badge), Aktuelle Version, Zuletzt geändert

Badge-Farben werden per SCSS gesteuert (Odoo 19 erlaubt nur `decoration-success` und `decoration-warning` in `<list>`):
- **Entwurf:** Silber (`text-bg-300`, Odoo-19-spezifische Klasse)
- **Veröffentlicht:** Trendtec-Grün (`text-bg-success` → `#97d21d`)
- **Archiviert:** Dunkelgrau (`text-bg-warning` → `#5a6370`)

### 7.3 Search View

Filter: Entwürfe, Veröffentlicht, Archiviert, Meine Dokumente
Gruppierung: Nach Status, Nach Eigentümer

---

## 8. Installation

### 8.1 Odoo.sh (Deployment)

Das Deployment-Repo wird von Odoo.sh genutzt:
```bash
git clone --recurse-submodules --branch main git@github.com:fiaTG/MDWriter_mvp.git
```

Odoo.sh installiert `requirements.txt` automatisch beim Build.

### 8.2 Lokale Entwicklung

```bash
# 1. Repo clonen
git clone https://github.com/fiaTG/MDWriter.git

# 2. Python-Dependency installieren
pip install mistune

# 3. Modul in Odoo-Addons-Pfad eintragen
# odoo.conf: addons_path = ...,/pfad/zu/MDWriter

# 4. Modul installieren
./odoo-bin -u markdown_editor -d <datenbank>
```

### 8.3 Systemanforderungen

- Odoo 19 (Community oder Enterprise)
- Python 3.11+
- `mistune` (pip)
- `wkhtmltopdf` (für PDF-Generierung, wird von Odoo bereitgestellt)

---

## 9. Bekannte Einschränkungen und offene Punkte

| Thema | Status | Beschreibung |
|---|---|---|
| Diff-View | ✅ Implementiert | Wizard: zwei Versionen auswählen, unified diff (farbig, eine Spalte) |
| Restore-Funktion | ✅ Implementiert | Ältere Version wiederherstellen via Button in der Versions-Form |
| Syntax-Highlighting | ✅ Implementiert | CodeMirror 5 (Markdown-Modus), lokal eingebunden |
| Automatisierte Tests | ✅ Implementiert | TransactionCase-Tests: Versionierung, ACL, Restore, Diff |
| Performance | ⚠️ Beobachten | Bei sehr großen Dokumenten (>10.000 Zeilen) kann Live-Preview verlangsamen |

---

## 10. Änderungsverlauf

| Version | Datum | Änderung |
|---|---|---|
| 1.1.28 | 11.03.2026 | PDF-Fix: report_file=${object.name} (Mako) → object.name (Python-Ausdruck); wird von Odoo via safe_eval mit object-Kontext ausgewertet |
| 1.1.27 | 10.03.2026 | PDF-Template: Revert auf web.external_layout + doc.content_html (bewährt stabil); custom CSS-Template entfernt |
| 1.1.26 | 10.03.2026 | PDF-Fix: _get_report_html() umgeht fields.Html ORM, CSS-Werte hardcoded (kein t-esc in style-Block, verhindert arch-Sanitizer-Stripping) |
| 1.1.25 | 10.03.2026 | PDF-Fix: sanitize=False auf content_html (verhindert doppeltes Escaping durch html_sanitize), report_file=${object.name}, write_date als DD.MM.YYYY |
| 1.1.24 | 10.03.2026 | Diff-Wizard: res_id=False in action_open_diff erzwingt neuen TransientModel-Datensatz bei jedem Öffnen |
| 1.1.23 | 10.03.2026 | PDF-Template: Trendtec-Branding via QWeb t-set-Variablen (brand_primary, brand_font, brand_logo usw.), eigener Header/Footer, wkhtmltopdf-kompatibel |
| 1.1.22 | 10.03.2026 | Konsistenz: PDF + MD-Download beide im Form-Header; binding_model_id entfernt (kein Zahnrad-Eintrag mehr) |
| 1.1.21 | 10.03.2026 | PDF-Button umbenannt (→ "Als PDF exportieren"), MD-Download-Button + action_download_md() |
| 1.1.20 | 10.03.2026 | Scrollbar-Fix: CodeMirror-vscrollbar/hscrollbar gezielt gestylt (CM5 ersetzt native Scrollbars) |
| 1.1.19 | 10.03.2026 | Scrollbars gestylt: Editor, Preview, Diff in Trendtec-Grün (6px, thin, Chromium + Firefox) |
| 1.1.18 | 10.03.2026 | Test-Fix: return_value=False statt side_effect=OSError in Fallback-Test |
| 1.1.17 | 10.03.2026 | Debounce (300ms) für Live-Preview, Exception-Logging präzisiert, Fallback-Tests hinzugefügt |
| 1.1.16 | 10.03.2026 | Anfängerfreundliche Kommentare in md_document.py, md_document_diff.py, markdown_editor.js und tests/ |
| 1.1.15 | 10.03.2026 | Refactoring: _create_version aufgeteilt, _render/_updateState extrahiert, SCSS DRY-Fix, XML-Duplikat entfernt |
| 1.1.14 | 10.03.2026 | Badge-Selektor auf text-bg-300 korrigiert (Odoo-19-spezifische Klasse für Draft) |
| 1.1.13 | 10.03.2026 | Badge-Farben nach State differenziert: decoration-success/warning, SCSS-Overrides |
| 1.1.12 | 10.03.2026 | Statusübergänge: action_publish/set_draft/archive_doc + Header-Buttons mit invisible |
| 1.1.11 | 10.03.2026 | Trendtec-Branding: CSS Design Tokens, Mulish-Font, Editor-Kontrast, Preview-Typografie, Listenansicht |
| 1.1.10 | 09.03.2026 | Layout-Fix: o_form_sheet_bg max-width:1400px überschreiben, flex-direction:column Override entfernt |
| 1.1.9 | 09.03.2026 | mail.thread + mail.activity.mixin entfernt (Chatter-Panel-Injection verhindert, Layout bereinigt) |
| 1.1.8 | 09.03.2026 | Odoo-19-Fixes: groups_id in Tests entfernt, _render_qweb_pdf API korrigiert, t-raw→t-out+Markup(), icon.png hinzugefügt |
| 1.1.7 | 09.03.2026 | Automatisierte Tests: TransactionCase für Versionierung, ACL, Restore, Diff (tests/test_md_document.py) |
| 1.1.6 | 09.03.2026 | Diff-View Fix: unified_diff statt HtmlDiff, Button in Versionen-Tab, Dialog 900px, farbige Zeilen |
| 1.1.5 | 09.03.2026 | Diff-View: Wizard x.md.document.diff.wizard, difflib.unified_diff, Button in Versionen-Tab |
| 1.1.4 | 09.03.2026 | Syntax-Highlighting: CodeMirror 5 (Markdown-Modus) lokal eingebunden, OWL onMounted/onWillUnmount Integration |
| 1.1.3 | 09.03.2026 | Restore-Funktion: action_restore() in XMdDocumentVersion, "Wiederherstellen"-Button in Versions-Form-View |
| 1.1.2 | 09.03.2026 | t-raw → t-out + markup() Migration; Fonts JetBrains Mono + Inter eingebunden (Variable Fonts, lokal) |
| 1.1.1 | 09.03.2026 | Font-Integration vorbereitet (SCSS @font-face), Textarea: JetBrains Mono, Preview: Inter |
| 1.1.0 | 09.03.2026 | markdown-it integriert (Live-HTML-Preview), XSS-Fix (html:false), PDF-Export funktionsfähig (mistune + web.html_container + binding_model_id), white-space:pre-wrap entfernt |
| 1.0.9 | 11.02.2026 | Flex-System-Fix: Form Sheet auf Block-Layout, Editor-Wrapper-Klasse |
| 1.0.8 | 28.01.2026 | Layout-Fix: Overflow-Fixes, Strukturänderung Form View |
| 1.0.7 | 27.01.2026 | MEILENSTEIN 1: Modul erfolgreich installierbar auf Odoo 19 |
| 1.0.6 | 27.01.2026 | .gitignore hinzugefügt |
| 1.0.5 | 27.01.2026 | List View Fix: ungültige Decoration-Attribute entfernt |
| 1.0.4 | 27.01.2026 | Form View Fix: undefined Action Buttons entfernt |
| 1.0.3 | 27.01.2026 | Icon/Logo Integration |
| 1.0.2 | 27.01.2026 | Manifest-Fixes, Version auf 19.0.1.0.0 |
| 1.0.1 | 27.01.2026 | Odoo 19 Migration: `<tree>` → `<list>` |
| 1.0.0 | 27.01.2026 | Initial Release |

---

**Letzte Aktualisierung:** 11.03.2026 (v1.1.28)
