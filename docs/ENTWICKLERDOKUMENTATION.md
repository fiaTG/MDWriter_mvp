# Entwicklerdokumentation: MDWriter Odoo 19 Modul

**Projekt:** MDWriter – Markdown Editor für Odoo 19
**Modulversion:** 19.0.1.1.0
**Autor:** Timo Giese
**Datum:** März 2026
**Status:** In Entwicklung (MVP funktionsfähig)

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
│   └── md_document.py                      # Modelle: x.md.document, x.md.document.version
├── views/
│   └── md_document_views.xml               # Form-, List-, Search-Views, Menü
├── static/
│   ├── description/
│   │   └── icon.png                        # Modul-Icon
│   ├── lib/
│   │   └── markdown-it.min.js              # Markdown-Renderer (lokal, kein CDN)
│   └── src/
│       ├── js/
│       │   └── markdown_editor.js          # OWL-Komponente MarkdownField
│       ├── scss/
│       │   └── markdown_editor.scss        # Split-View-Layout, Odoo-Layout-Fixes
│       └── xml/
│           └── markdown_editor_templates.xml  # OWL-Template für MarkdownField
├── security/
│   ├── ir.model.access.csv                 # ACL-Definitionen
│   └── markdown_editor_security.xml        # Record Rules
└── report/
    └── md_document_report.xml              # QWeb PDF-Template + Report-Action
```

---

## 3. Datenmodell

### 3.1 x.md.document (Hauptmodell)

Dateiname: [models/md_document.py](../markdown_editor/models/md_document.py)

| Feld | Typ | Beschreibung |
|---|---|---|
| `name` | Char | Dokumenttitel (required) |
| `content_md` | Text | Markdown-Primärinhalt |
| `content_html` | Html | Gerendertes HTML (computed, sanitize=True) – für PDF |
| `state` | Selection | draft / published / archived |
| `owner_id` | Many2one → res.users | Eigentümer (default: aktueller User) |
| `version_ids` | One2many → x.md.document.version | Alle Versionen |
| `current_version` | Integer | Computed: höchste Versionsnummer |

Erbt: `mail.thread`, `mail.activity.mixin` (Chatter + Aktivitäten)

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

`_create_version()` erstellt pro Dokument:
1. Markdown-Attachment (`.md`-Datei)
2. PDF-Attachment via QWeb-Report (bei Fehler: nur Warnung, kein Absturz)
3. Version-Record mit Checksum (MD5)

### 3.4 PDF-Rendering (Backend)

Das computed field `content_html` wandelt Markdown serverseitig in HTML um:

```python
@api.depends("content_md")
def _compute_content_html(self):
    for doc in self:
        if _mistune_available:
            doc.content_html = mistune.html(doc.content_md)
        else:
            doc.content_html = "<pre>%s</pre>" % (doc.content_md or "")
```

`sanitize=True` auf dem Html-Field aktiviert Odoos eingebaute HTML-Sanitization vor der Speicherung.

---

## 4. Frontend

### 4.1 OWL-Komponente: MarkdownField

Dateiname: [static/src/js/markdown_editor.js](../markdown_editor/static/src/js/markdown_editor.js)

Die Komponente wird als Odoo Field Widget registriert und über `widget="markdown_editor"` in Views eingebunden.

**Initialisierung:**

```javascript
import { Component, useState, markup } from "@odoo/owl";

this.md = window.markdownit
    ? window.markdownit({ html: false, xhtmlOut: false, breaks: true, linkify: true })
    : null;
this.state = useState({
    value: initial,
    html: this.md ? markup(this.md.render(initial)) : markup(initial)
});
```

- `html: false` – eingebettetes HTML in Markdown wird escaped (XSS-Schutz)
- `breaks: true` – einzelne Zeilenumbrüche erzeugen `<br>`
- `linkify: true` – URLs werden automatisch verlinkt
- `markup()` aus `@odoo/owl` markiert den String als sicheres HTML für `t-out`

**XSS-Schutz:** `markdown-it({ html: false })` escaped eingebettetes HTML. `markup()` signalisiert OWL, dass der Inhalt sicher gerendert werden darf — ohne `markup()` würde `t-out` den Inhalt escapen.

**Input-Handler:**

```javascript
_onInput(ev) {
    const value = ev.target.value;
    this.state.value = value;
    this.state.html = this.md ? markup(this.md.render(value)) : markup(value);
    this.props.record.update({ [this.props.name]: value });
}
```

Kein direktes `innerHTML` mehr — das Rendering läuft rein reaktiv über OWL State + `t-out`.

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

**Fonts:**

Alle Fonts liegen lokal unter `static/src/fonts/` — kein CDN.

| Font | Verwendung | Datei |
|---|---|---|
| JetBrains Mono | Editor-Textarea | `JetBrains_Mono/JetBrainsMono-VariableFont_wght.ttf` |
| Inter | Preview-Bereich | `Inter/Inter-VariableFont_opsz,wght.ttf` |

Variable Fonts decken alle Gewichte (100–800 / 100–900) in einer Datei ab.
Fallback: `monospace` (Editor), System-Fonts (Preview).

Weitere Fonts im Repo (Fira Code, Space Grotesk) sind verfügbar aber nicht aktiv eingebunden.

**Odoo Enterprise Layout-Fix:**
```scss
.o_form_renderer:has(.o_markdown_editor) {
    flex-direction: column !important;
}
```
Ursache: Odoo Enterprise überschreibt `flex-direction` auf `row`, was den Editor neben den Chatter rendert. Der Fix ist mit `:has()` gezielt auf Views mit dem Editor begrenzt.

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
- **Backend:** `content_html` field mit `sanitize=True` – Odoo sanitized HTML vor Speicherung
- **PDF-Template:** `t-raw` auf `doc.content_html` – Inhalt ist bereits sanitized

---

## 6. PDF-Export

### 6.1 Funktionsweise

1. User klickt im ⚙️-Menü auf "Markdown Dokument"
2. Odoo ruft `ir.actions.report` auf (`binding_model_id = x.md.document`)
3. Report rendert QWeb-Template `markdown_editor.report_md_document`
4. Template ruft `doc.content_html` auf → computed field mit `mistune.html(content_md)`
5. `wkhtmltopdf` konvertiert HTML → PDF

### 6.2 Template-Struktur

```xml
<template id="report_md_document">
    <t t-call="web.html_container">        <!-- Pflicht: liefert <main>-Element -->
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">  <!-- Odoo-Header/Footer -->
                <div class="page">
                    <h1><t t-esc="doc.name"/></h1>
                    <div t-raw="doc.content_html"/>
                </div>
            </t>
        </t>
    </t>
</template>
```

`web.html_container` ist in Odoo 19 zwingend nötig – ohne ihn schlägt `_prepare_html` mit `IndexError: list index out of range` fehl (erwartet `//main` im DOM).

### 6.3 Python-Dependency: mistune

Eingebunden via `requirements.txt` im Repo-Root (wird von Odoo.sh automatisch installiert):
```
mistune
```

Fallback: Falls `mistune` nicht verfügbar, zeigt PDF den rohen Markdown-Text als `<pre>`.

---

## 7. Views

### 7.1 Form View

- Titel als `oe_title`
- `content_md` mit `widget="markdown_editor"` (Split-View)
- Notebook mit zwei Tabs:
  - **Metadaten:** owner_id, current_version, create_date, write_date
  - **Versionen:** Liste aller Versionen (read-only) mit Version, User, Datum, Checksum, Attachments
- Chatter (mail_thread + mail_activity)
- State-Statusbar: draft → published → archived

### 7.2 List View

Spalten: Name, Eigentümer (Avatar), Status (Badge), Aktuelle Version, Zuletzt geändert

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
| Diff-View | ❌ Offen | Vergleich zwischen zwei Versionen im Frontend |
| Restore-Funktion | ❌ Offen | Ältere Version wiederherstellen |
| Syntax-Highlighting | ❌ Offen | Highlighting im Textarea (würde CodeMirror o.ä. erfordern) |
| Automatisierte Tests | ❌ Offen | ACL-, Versionierungs- und UI-Tests |
| Performance | ⚠️ Beobachten | Bei sehr großen Dokumenten (>10.000 Zeilen) kann Live-Preview verlangsamen |

---

## 10. Änderungsverlauf

| Version | Datum | Änderung |
|---|---|---|
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

**Letzte Aktualisierung:** 09.03.2026
