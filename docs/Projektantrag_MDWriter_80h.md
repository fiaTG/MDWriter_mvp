# Projektantrag: MDWriter - Markdown Editor für Odoo 19

## 1.0 Projektbeschreibung

### 1.1 Projekttitel
Entwicklung eines Markdown-Editors für Odoo 19

### 1.2 Kurzbeschreibung der Aufgabenstellung
Das Ziel des Projekts ist die Entwicklung eines Markdown-basierten Editors als Odoo 19 Modul. Die Anwendung umfasst einen Split-View-Editor mit Live-Vorschau und grundlegende Speicherfunktionen. Das System ermöglicht es Benutzern, strukturierte Texte in Markdown zu erstellen, zu bearbeiten und als Markdown-Datei in Odoo zu speichern. Optional werden PDF-Export und Versionierung implementiert, sofern am Ende des Projektes noch Zeit bleibt.

### 1.3 Ist-Zustand
Aktuell bietet Odoo 19 keinen nativen Markdown-Editor für strukturierte Dokumentation. Benutzer sind auf den HTML-basierten WYSIWYG-Editor angewiesen, der für technische Dokumentationen, Code-Snippets und strukturierte Inhalte ungeeignet ist. Es gibt keine zentrale Lösung für Markdown-basiertes Arbeiten im Odoo-Ökosystem.

### 1.4 Soll-Zustand
Die geplante Odoo-Erweiterung soll Benutzern eine entwicklerfreundliche Plattform bieten, die Markdown-Dokumente verwaltet. Durch einen Split-View-Editor mit Live-Vorschau wird die Erstellung strukturierter Dokumentationen effizienter gestaltet. Das Modul speichert Markdown-Dokumente in der Datenbank und ermöglicht zusätzlich den Download als .md Datei über das Odoo-Attachment-System.

### 1.5 Projektanforderungen

**Kernfunktionen (Muss):**
• Die Anwendung muss sich nahtlos in Odoo 19 integrieren.
• Ein Split-View-Editor (Markdown links, Live-Vorschau rechts) ist erforderlich.
• Speicherung von Markdown-Inhalt im Datenmodell.
• Grundlegende Zugriffskontrolle über Odoo ACL.
• Die Anwendung soll mit Python 3.11+, OWL (Odoo Web Library) und PostgreSQL als Odoo-Datenbank für Speicherung der Dokumente verwendet werden.


**Optionale Funktionen (Nice-to-have):**
• PDF-Export mit professionellem Layout.
• Automatische Versionierung mit Checksummen.
• Vollständiger Audittrail mit Diff-Ansicht.
• Dark-Mode-Unterstützung.
• Syntax-Highlighting im Editor.

---

## 2.0 Projektphasen / Zeitplan

### 2.1 Vorgehensweise
Für das Projekt wird ein agiles Entwicklungsverfahren angewendet, das regelmäßige Feedbackgespräche mit Kollegen integriert. Dieser iterative Ansatz gewährleistet, dass mögliche Fehler oder Probleme frühzeitig identifiziert und behoben werden können. Das Projekt wird in klar definierte Phasen unterteilt, wobei jede Phase konkrete Ziele und Aufgaben umfasst. Durch sorgfältige Planung und kontinuierliches Monitoring wird sichergestellt, dass das Projekt termingerecht und in hoher Qualität abgeschlossen wird.

### 2.2 Technische Umsetzung
Die Umsetzung des Odoo-Moduls erfolgt unter Verwendung von Python (Backend), OWL/JavaScript (Frontend) und SCSS (Styling), wodurch eine performante und entwicklerfreundliche Plattform geschaffen wird. Als Datenbank wird PostgreSQL eingesetzt, um eine effiziente Speicherung und Verwaltung von Dokumenten zu gewährleisten.

• **Backend:** Entwicklung mit Python (Odoo ORM) zur Realisierung der Modelle und Speicherlogik.
• **Frontend:** OWL-Komponenten für den Markdown-Editor und Live-Vorschau mit Split-View-Oberfläche.
• **Styling:** SCSS für modernes, responsives Design.
• **Datenbank:** PostgreSQL als Grundlage für stabile Datenspeicherung (Dokumente, Attachments).

Diese technische Grundlage gewährleistet eine leistungsstarke und benutzerorientierte Odoo-Erweiterung, die die Anforderungen der Zielgruppe optimal erfüllt.

---

## 2.3 Detaillierter Zeitplan

| **Phase** | **Aufgabe** | **Zeitaufwand** |
|-----------|-------------|-----------------|
| **1. Analysephase** | 1.1 Erstellung des Projektplans und Anforderungsanalyse | 2 Stunden |
| | 1.2 Recherche Odoo 19 Module, OWL-Framework und Markdown-Libraries | 4 Stunden |
| | 1.3 Vorbereitung Entwicklungsumgebung (Odoo 19, PostgreSQL, Tools) | 2 Stunden |
| **2. Entwurfsphase** | 2.1 Datenmodell-Design (x_md_document) | 3 Stunden |
| | 2.2 UI/UX-Konzept (Split-View, Editor-Toolbar) | 5 Stunden |
| | 2.3 Sicherheitskonzept (ACL) | 2 Stunden |
| | 2.4 Architektur-Planung (OWL-Komponenten, Backend-Struktur) | 2 Stunden |
| **3. Implementierungsphase** | 3.1 Backend: Modell (md_document) mit Basis-Feldern | 6 Stunden |
| | 3.2 Backend: Speichern als Markdown-Attachment | 4 Stunden |
| | 3.3 Frontend: OWL Markdown-Editor mit Split-View | 14 Stunden |
| | 3.4 Frontend: Live-Vorschau (Markdown → HTML Rendering) | 9 Stunden |
| | 3.5 Security: Basis ACL-Integration | 4 Stunden |
| | 3.6 Views: Odoo List/Form Views und Menüs | 5 Stunden |
| **4. Abnahme und Einführung** | 4.1 Feedbackrunde mit Kollegen | 1 Stunde |
| | 4.2 Funktions-Tests (Editor, Speichern, ACL) | 4 Stunden |
| | 4.3 Fehlerbehebung und Optimierung | 5 Stunden |
| **5. Dokumentationsphase** | 5.1 Erstellung der Projektdokumentation | 7 Stunden |
| | 5.2 Erstellung von Wochenberichten | 3 Stunden |
| | 5.3 Vorbereitung und Erstellung der Präsentation | 2 Stunden |
| **Gesamtstundenanzahl:** | | **80 Stunden** |

---

## Priorisierung

**Must-Have (Projektziel):**
- Split-View Markdown-Editor
- Live-Vorschau
- Speichern in Odoo (Datenbank + Attachment)
- Basis ACL

**Should-Have (wenn Zeit):**
- PDF-Export
- Einfache Versionierung

**Nice-to-Have (optional):**
- Checksummen & Audittrail
- Dark Mode
- Syntax-Highlighting
