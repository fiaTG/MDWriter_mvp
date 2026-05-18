# Unterschiede: Implementierung vs. IHK-Projektantrag (Online-Version)

Grundlage: IHK Online-Antrag (eingereicht 03.03.2026, Bearbeitungszeitraum 08.05.–26.05.2026)

---

## Pflichtanforderungen laut Antrag

| Anforderung | Quelle im Antrag | Status |
|---|---|---|
| Markdown-Editor mit Split-View und Live-Vorschau | Projektziel, Zeitplanung Frontend | ✅ |
| Strukturierte Speicherung in Odoo-Datenbank | Projektziel | ✅ |
| Speicherung als Attachment | Zeitplanung Backend (4 h) | ✅ |
| Absicherung über Odoo-ACL | Projektziel, Zeitplanung Frontend (4 h) | ✅ |
| Odoo Views & Menüs | Zeitplanung Frontend (5 h) | ✅ |
| PDF-Export | Projektziel, Zeitplanung Backend (3 h) | ✅ |
| Einfache Änderungsverfolgung | Projektziel explizit | ✅ |
| Testfälle zur Validierung funktionaler Anforderungen | Zeitplanung Test (2 h) | ✅ |

**Wichtig:** Im IHK-Antrag sind PDF-Export und Änderungsverfolgung **Pflicht** — nicht optional wie in der älteren PDF-Version.

---

## Was über den Antrag hinausgeht

### Zurückbauen empfohlen — schwer erklärbar, kein Bezug zum Antrag

| Feature | Aufwand Rückbau | Begründung |
|---|---|---|
| **9 markdown-it Plugins** (emoji, footnote, containers, abbr, deflist, ins, mark, sub, sup) | Gering | Antrag fordert Markdown-Editor, nicht erweitertes Markdown |
| **Typographer** (Smartquotes, Gedankenstriche) | Minimal | Kein Bezug zum Antrag |
| **Focus Mode** | Gering | UI-Extra, nicht im UI/UX-Konzept des Antrags |
| **Documents-Integration** (.md in Odoo Documents App) | Gering | Nicht im Antrag — funktioniert, aber erhöht Erklärungsaufwand |
| **Draggable Splitter + Snap-Buttons (◀/▶)** | Mittel | Split-View war gefordert — interaktive Größenanpassung nicht |
| **Scroll-Synchronisation** (Editor ↔ Preview bidirektional) | Mittel | Nicht im Antrag, erhöht Erklärungsaufwand |
| **Scroll-to-top Button + Fortschrittsbalken** | Gering | Nicht im Antrag |

### Behalten — sinnvoll und gut erklärbar

| Feature | Begründung |
|---|---|
| **Diff-View** (Versionsvergleich) | „Einfache Änderungsverfolgung" aus dem Antrag — zeigt den Mehrwert |
| **Restore-Funktion** | Gehört logisch zur Änderungsverfolgung |
| **Statusübergänge** (Entwurf / Veröffentlicht / Archiviert) | Passt zu ACL-Konzept und Dokumenten-Workflow |
| **MD5-Checksummen** | Einfach erklärbar: Datenintegrität, 1 Zeile Code |
| **Automatisierte Tests** | Direkt aus Zeitplanung „Testfälle zur Validierung" |
| **Trendtec-Branding + Design Tokens** | Teil des UI/UX-Konzepts, Unternehmensidentität |
| **Dark Mode** | Kommt durch Odoo CSS-Variablen fast gratis, gut demonstrierbar |
| **4 Custom Fonts** | Begründbar als Teil des Branding-Konzepts |
| **Documents-Integration** | Funktioniert stabil — „.md direkt aus Odoo Documents abrufbar" ist ein konkreter Mehrwert |

---

## Minimale Prüfungsversion (100% Antrag + gut begründbare Extras)

```
Pflicht (direkt aus Antrag):
✅ Split-View Editor (CodeMirror + Live-Vorschau)
✅ Speicherung in Odoo-Datenbank + Attachment
✅ ACL + Record Rules
✅ Odoo Views & Menüs
✅ PDF-Export
✅ Einfache Änderungsverfolgung (Versionsliste + Diff)
✅ Testfälle / automatisierte Tests

Behalten als sinnvoller Ausbau:
+ Restore-Funktion
+ Statusübergänge
+ Trendtec-Branding / Dark Mode

Entfernen:
- 9 markdown-it Plugins
- Typographer
- Focus Mode
- Draggable Splitter / Snap-Buttons
- Scroll-Synchronisation
- Scroll-to-top / Fortschrittsbalken
```

---

## Hinweis zur Präsentation

Der Antrag nennt **80 Stunden** — davon 40h Implementierung.
Beim Vorstellen den Fokus auf die 8 Pflichtanforderungen legen.
Diff-View und Restore als **Vertiefung der Änderungsverfolgung** positionieren, nicht als Extra.
Features die nicht im Antrag stehen (Plugins, Focus Mode etc.) am besten gar nicht erwähnen.
