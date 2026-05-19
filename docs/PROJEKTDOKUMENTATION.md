# Projektdokumentation

**Thema der Projektarbeit:**
Konzeption und Entwicklung einer zentralen technischen Dokumentationslösung auf Markdown-Basis innerhalb von Odoo 19

---

| | |
|---|---|
| **Verfasser** | Timo Giese |
| **Ausbildungsberuf** | Fachinformatiker Anwendungsentwicklung |
| **Ausbildungsbetrieb** | TrendTec UG, Mannheimer Straße 105a, 68535 Edingen-Neckarhausen |
| **Ausbildungsverantwortlicher** | Oliver Kölsch |
| **Bearbeitungszeitraum** | 08.05.2026 – 26.05.2026 |
| **Gesamtaufwand** | 80 Stunden |

---

## Inhaltsverzeichnis

1. [Einleitung](#1-einleitung)
   - 1.1 Projektumfeld und Ausgangssituation
   - 1.2 Projektziel
   - 1.3 Abgrenzung des Projekts
2. [Projektplanung](#2-projektplanung)
   - 2.1 Projektphasen und Zeitplanung
   - 2.2 Ressourcenplanung
   - 2.3 Wirtschaftlichkeitsbetrachtung
3. [Analysephase](#3-analysephase)
   - 3.1 Ist-Zustand
   - 3.2 Anforderungsanalyse
   - 3.3 Use-Case-Analyse
4. [Entwurfsphase](#4-entwurfsphase)
   - 4.1 Systemarchitektur
   - 4.2 Datenmodell
   - 4.3 Sicherheitskonzept
   - 4.4 UI/UX-Konzept
5. [Implementierungsphase](#5-implementierungsphase)
   - 5.1 Modulstruktur
   - 5.2 Backend-Implementierung
   - 5.3 Frontend-Implementierung
   - 5.4 Sicherheitsintegration
6. [Testphase](#6-testphase)
   - 6.1 Testkonzept
   - 6.2 Testfälle
   - 6.3 Testergebnisse
7. [Fazit](#7-fazit)
   - 7.1 Soll-/Ist-Vergleich der Zeitplanung
   - 7.2 Reflexion und Lessons Learned
   - 7.3 Ausblick
8. [Anhang](#8-anhang)
   - A: Abkürzungsverzeichnis
   - B: Glossar
   - C: Quellenverzeichnis

---

## 1. Einleitung

### 1.1 Projektumfeld und Ausgangssituation

Die TrendTec UG ist ein IT-Dienstleister mit Sitz in Edingen-Neckarhausen, der sich auf die Implementierung und Anpassung von ERP-Systemen auf Basis von Odoo spezialisiert hat. Das Unternehmen betreut kleine und mittelständische Unternehmen bei der Digitalisierung ihrer Geschäftsprozesse und beschäftigt derzeit neun Mitarbeiter.

Im Arbeitsalltag der Entwicklungsabteilung entsteht kontinuierlich technische Dokumentation: API-Beschreibungen, Installationsanleitungen, Konfigurationshinweise und Prozessbeschreibungen. Diese Dokumentation wurde bislang auf verschiedene externe Werkzeuge verteilt. Ein Teil wurde direkt im Odoo-internen HTML-WYSIWYG-Editor erstellt, ein anderer Teil in externen Tools wie Git-Wikis oder lokalen Textdateien gepflegt.

Daraus entstanden im Projektalltag konkrete Probleme: Dokumente lagen an unterschiedlichen Orten, ohne einheitlichen Standard oder zentrale Auffindbarkeit. Der HTML-WYSIWYG-Editor von Odoo eignet sich für Freitext, ist jedoch für technische Inhalte wie Code-Snippets, Konfigurationstabellen oder strukturierte Abläufe nur bedingt geeignet. In der Entwicklungsabteilung ist das Markdown-Format bereits aus der täglichen Arbeit mit Git-Repositories und Projektdokumentationen bekannt und akzeptiert. Eine Möglichkeit, Markdown direkt in Odoo zu verwenden, fehlte jedoch.

Die Folgen dieser Situation waren uneinheitliche Dokumentationsstandards, Medienbrüche zwischen verschiedenen Tools, eingeschränkte Eignung für technische Inhalte und eine erschwerte Wartbarkeit der vorhandenen Dokumentation.

### 1.2 Projektziel

Ziel des Projekts ist die Konzeption und Entwicklung eines nativen Odoo-19-Moduls, das eine zentrale, markdown-basierte Dokumentationslösung innerhalb des bestehenden ERP-Systems bereitstellt. Das Modul trägt den internen Projektnamen **MDWriter** und wird unter dem technischen Modulnamen `markdown_editor` entwickelt.

Konkret umfasst das Projektziel folgende Kernfunktionen:

- Einen Markdown-Editor mit geteilter Ansicht (Split-View): auf der linken Seite befindet sich der Texteingabebereich, auf der rechten Seite wird die formatierte Vorschau in Echtzeit dargestellt.
- Die strukturierte Speicherung von Dokumenten in der Odoo-Datenbank (PostgreSQL) über das Odoo ORM.
- Die Speicherung jeder Dokumentversion als Datei-Anhang (Attachment) im Odoo-Dateisystem.
- Die Absicherung des Zugriffs über das bestehende Odoo-ACL-System, sodass Benutzer ausschließlich ihre eigenen Dokumente sehen und bearbeiten können, während Administratoren systemweiten Zugriff erhalten.
- Einen PDF-Export, der die formatierte Markdown-Dokumentation als druckfertiges Dokument bereitstellt.
- Eine einfache Änderungsverfolgung, die den Verlauf aller Versionen eines Dokuments nachvollziehbar macht und einen direkten Versionsvergleich ermöglicht.

Das Modul soll als eigenständige Erweiterung in das Odoo-System integriert werden und langfristig in Kundenprojekten einsetzbar sein.

### 1.3 Abgrenzung des Projekts

Das Projekt umfasst ausdrücklich keine allgemeine Dokumentenmanagement-Plattform, kein kollaboratives Echtzeit-Editing mehrerer Nutzer und keine externe API-Schnittstelle. Die Lösung ist bewusst als schlankes, in Odoo integriertes Werkzeug konzipiert, das die vorhandene Infrastruktur nutzt und keine neuen Systemabhängigkeiten einführt.

---

## 2. Projektplanung

### 2.1 Projektphasen und Zeitplanung

Das Projekt wurde in fünf Phasen eingeteilt, die sich an dem klassischen Vorgehensmodell für Softwareentwicklungsprojekte orientieren. Die nachfolgende Tabelle zeigt die geplante Stundenzuteilung je Phase:

| Phase | Aufgaben | Geplante Zeit |
|---|---|---|
| **Analyse** | Lösungsansätze bewerten, Anforderungsanalyse, Technologierecherche, Entwicklungsumgebung einrichten | 8 h |
| **Entwurf** | Architekturplanung, Datenmodell-Design, Sicherheitskonzept, UI/UX-Konzept | 10 h |
| **Implementierung** | Backend (Modell, Attachment, PDF), Frontend (Editor, Vorschau, ACL, Views) | 40 h |
| **Test** | Testfälle erstellen, Funktions- und Integrationstests, Fehleranalyse | 10 h |
| **Dokumentation** | Projektdokumentation, Präsentationsvorbereitung | 12 h |
| **Gesamt** | | **80 h** |

Die Analysephase diente der Klärung technischer Grundlagen und der Auswahl geeigneter Bibliotheken. In der Entwurfsphase wurden die Kernentscheidungen zu Datenmodell, Sicherheitsarchitektur und Benutzeroberfläche getroffen. Die Implementierungsphase mit dem größten Zeitanteil (50 % des Gesamtaufwands) teilte sich in Backend-Entwicklung (13 Stunden) und Frontend-Entwicklung (27 Stunden) auf. Die Testphase umfasste sowohl manuelle Integrationstests als auch die Erstellung automatisierter Tests. Die Dokumentationsphase schloss das Projekt mit der vorliegenden Projektdokumentation und der Vorbereitung der Abschlusspräsentation ab.

### 2.2 Ressourcenplanung

Für die Durchführung des Projekts standen folgende Ressourcen zur Verfügung:

**Personelle Ressourcen:**

| Rolle | Person | Einsatz |
|---|---|---|
| Entwickler (Auszubildender) | Timo Giese | 80 h (Hauptaufwand) |
| Projektverantwortlicher | Oliver Kölsch | ca. 5 h (Freigaben, Feedback) |

**Technische Ressourcen:**

Die Entwicklung erfolgte auf einem Windows-11-Arbeitsplatz mit Visual Studio Code als Entwicklungsumgebung. Das Deployment und die abschließenden Tests wurden auf einer Odoo.sh-Instanz (Odoo 19, Enterprise-Lizenz) durchgeführt. Als Versionsverwaltung wurde Git mit GitHub als Remote-Repository genutzt.

### 2.3 Wirtschaftlichkeitsbetrachtung

#### 2.3.1 Make-or-Buy-Analyse

Vor der Entscheidung zur Eigenentwicklung wurden alternative Lösungsansätze bewertet:

**Alternative 1 – Atlassian Confluence (SaaS):**
Confluence ist ein etabliertes Wiki- und Dokumentationswerkzeug mit Markdown-Unterstützung. Es bietet eine gute Eignung für technische Inhalte, ist jedoch ein externes System ohne native Odoo-Integration. Medienbrüche zwischen Odoo und Confluence bleiben bestehen. Die Lizenzkosten betragen bei neun Benutzern im Cloud-Modell ca. 10 € pro Nutzer und Monat.

**Alternative 2 – GitLab/GitHub Wiki:**
Die bereits genutzten Git-Plattformen bieten integrierte Wikis mit Markdown-Unterstützung. Diese Lösung ist kostenneutral im Rahmen bestehender Lizenzen, bietet jedoch keine Odoo-Integration, keinen PDF-Export aus Odoo heraus und keine Verbindung zum Odoo-ACL-System. Für externe Kundenprojekte ist diese Lösung nicht skalierbar.

**Alternative 3 – Eigenentwicklung (MDWriter):**
Ein natives Odoo-Modul nutzt die bestehende Odoo-Infrastruktur vollständig: Datenhaltung in PostgreSQL, Zugriffskontrolle über das Odoo-ACL-System, PDF-Export über den Odoo-Reportingmechanismus. Medienbrüche entfallen. Die Lösung ist mandantenfähig und direkt für Kundenprojekte einsetzbar.

Die Entscheidung fiel auf die Eigenentwicklung, da die Anforderung nach vollständiger Odoo-Integration durch externe Tools strukturell nicht erfüllbar ist.

#### 2.3.2 Kostenvergleich

**Projektkosten Eigenentwicklung:**

| Position | Berechnung | Betrag |
|---|---|---|
| Entwicklung (Auszubildender) | 80 h × 12,00 €/h | 960,00 € |
| Projektbegleitung (Projektverantwortlicher) | 5 h × 150,00 €/h | 750,00 € |
| **Einmalige Projektkosten gesamt** | | **1.710,00 €** |
| Jährliche Wartung (geschätzt) | 8 h × 12,00 €/h | 96,00 €/Jahr |

**Laufende Kosten Confluence (9 Benutzer):**

| Position | Berechnung | Betrag |
|---|---|---|
| Lizenz Cloud | 9 × 10,00 €/Monat × 12 | 1.080,00 €/Jahr |

#### 2.3.3 Amortisationsberechnung

Die Eigenentwicklung verursacht im ersten Jahr höhere Kosten als die Lizenzlösung (1.710 € + 96 € = 1.806 € vs. 1.080 €). Ab dem zweiten Jahr entstehen lediglich Wartungskosten von ca. 96 €/Jahr gegenüber 1.080 €/Jahr für Confluence. Die Amortisation ist nach ca. 18 Monaten erreicht.

Über einen Betrachtungshorizont von drei Jahren ergeben sich folgende Gesamtkosten:

| Lösung | Jahr 1 | Jahr 2 | Jahr 3 | Gesamt |
|---|---|---|---|---|
| MDWriter | 1.806 € | 96 € | 96 € | **1.998 €** |
| Confluence | 1.080 € | 1.080 € | 1.080 € | **3.240 €** |

Zusätzlich zu den quantifizierbaren Einsparungen ergeben sich nicht-monetäre Vorteile: vollständige Datenhoheit (alle Dokumente verbleiben in der eigenen Odoo-Datenbank), kein externer SaaS-Anbieter, nahtlose Integration in bestehende Odoo-Workflows und direkte Weiterverwendbarkeit des Moduls in Kundenprojekten.

---

## 3. Analysephase

### 3.1 Ist-Zustand

Zu Projektbeginn wurde der aktuelle Stand der Dokumentationspraxis in der Entwicklungsabteilung analysiert. Folgende Werkzeuge wurden parallel genutzt:

- **Odoo HTML-Editor:** Für Freitextnotizen und einfache Anleitungen. Die Eignung für Code-Snippets und strukturierte technische Dokumentation ist durch das WYSIWYG-Paradigma eingeschränkt.
- **Git-Wikis (GitHub/GitLab):** Für projektbezogene Dokumentation direkt im Repository-Kontext. Kein Zugriff aus Odoo heraus.
- **Lokale Markdown-Dateien:** Von einzelnen Entwicklern lokal gepflegt, ohne zentrale Ablage oder Versionskontrolle auf Systemebene.

Der Hauptbefund der Ist-Analyse lautet: Es existiert kein einheitlicher Standard für technische Dokumentation. Der Zugriff auf Dokumente ist nicht über das Odoo-Benutzer- und Berechtigungssystem abgesichert. Versionsstände sind nicht systematisch nachvollziehbar.

### 3.2 Anforderungsanalyse

Auf Basis der Ist-Analyse wurden die Anforderungen an das neue System in funktionale und nicht-funktionale Anforderungen gegliedert.

#### 3.2.1 Funktionale Anforderungen

| Nr. | Anforderung | Priorität |
|---|---|---|
| F01 | Markdown-Editor mit Split-View (Eingabe links, Vorschau rechts) | Muss |
| F02 | Live-Vorschau: Vorschau aktualisiert sich während der Eingabe | Muss |
| F03 | Speicherung von Dokumenten in der Odoo-Datenbank | Muss |
| F04 | Speicherung jeder Version als Datei-Anhang (`.md`-Datei) | Muss |
| F05 | Zugriffsschutz: Benutzer sehen nur ihre eigenen Dokumente | Muss |
| F06 | Administratoren haben Zugriff auf alle Dokumente | Muss |
| F07 | PDF-Export des aktuellen Dokumentinhalts | Muss |
| F08 | Automatische Versionierung bei jeder Inhaltsänderung | Muss |
| F09 | Versionsvergleich (Diff-Ansicht) zweier Versionen | Muss |
| F10 | Statusverwaltung (Entwurf, Veröffentlicht, Archiviert) | Soll |
| F11 | Wiederherstellung einer älteren Version | Soll |
| F12 | Syntax-Highlighting im Editor | Soll |

#### 3.2.2 Nicht-funktionale Anforderungen

| Nr. | Anforderung |
|---|---|
| NF01 | Kompatibilität mit Odoo 19 (Community und Enterprise) |
| NF02 | XSS-Schutz: Kein unsicheres HTML-Rendering von Benutzereingaben |
| NF03 | Keine externen Laufzeitabhängigkeiten (CDN-unabhängig) |
| NF04 | Dark-Mode-Kompatibilität über Odoo CSS-Variablen |
| NF05 | Einhaltung der Odoo-Modulkonventionen (Manifest, ACL, ORM) |
| NF06 | Testabdeckung für kritische Backend-Funktionen |

### 3.3 Use-Case-Analyse

Die wesentlichen Anwendungsfälle des Systems lassen sich in zwei Benutzerrollen aufteilen:

**Rolle: Benutzer (normaler Mitarbeiter)**
Ein Benutzer kann eigene Dokumente anlegen, bearbeiten, veröffentlichen und archivieren. Er kann den Verlauf seiner eigenen Dokumente einsehen, Versionen vergleichen und eine ältere Version wiederherstellen. Er kann ein Dokument als PDF exportieren und als Markdown-Datei herunterladen. Er hat keinen Zugriff auf Dokumente anderer Benutzer.

**Rolle: Administrator**
Ein Administrator verfügt über alle Rechte eines Benutzers, hat darüber hinaus jedoch systemweiten Zugriff auf sämtliche Dokumente aller Benutzer. Er kann außerdem Dokumente löschen – eine Funktion, die normalen Benutzern nicht zur Verfügung steht.

Administratoren haben systemweiten Zugriff, normale User ausschließlich auf ihre eigenen Dokumente.

---

## 4. Entwurfsphase

### 4.1 Systemarchitektur

MDWriter ist als natives Odoo-Modul konzipiert, das vollständig in die bestehende Odoo-Architektur eingebettet ist. Es gibt keine externe Kommunikation und keine zusätzlichen Systemdienste außerhalb von Odoo.

Die Architektur folgt dem dreischichtigen Aufbau von Odoo:

**Datenschicht:** PostgreSQL-Datenbank, verwaltet über das Odoo ORM. Das Modul definiert zwei eigene Modelle (`x.md.document` und `x.md.document.version`) sowie einen TransientModel-Assistenten (`x.md.document.diff.wizard`). Dateianhänge werden über das native Odoo-Attachment-System (`ir.attachment`) gespeichert.

**Anwendungsschicht (Backend):** Python-Klassen, die das Odoo ORM erweitern. Hier sind Versionierungslogik, PDF-Rendering, Statusübergänge und Sicherheitsregeln implementiert.

**Präsentationsschicht (Frontend):** OWL-Komponente (Odoo Web Library), die als Custom Field Widget registriert ist. Die Komponente rendert den Split-View-Editor mit CodeMirror als Syntaxeditor und markdown-it als Live-Renderer. Die Einbindung erfolgt über das Odoo-Assets-Bundle-System.

Das Modul hat keine externen Abhängigkeiten zur Laufzeit: Alle JavaScript-Bibliotheken (markdown-it, CodeMirror) liegen lokal im Modulverzeichnis. Die einzige Python-Laufzeitabhängigkeit ist `mistune`, eine leichtgewichtige Markdown-zu-HTML-Bibliothek, die über `requirements.txt` im Repository deklariert ist.

### 4.2 Datenmodell

Das Datenmodell besteht aus zwei persistenten Tabellen und einem transienten Assistentenmodell.

**Hauptmodell `x.md.document`:**

Das Hauptmodell repräsentiert ein Dokument. Es speichert den aktuellen Dokumenttitel, den Markdown-Inhalt, den Veröffentlichungsstatus sowie den Eigentümer des Dokuments. Das Feld `current_version` ist ein berechnetes Feld, das die höchste vorhandene Versionsnummer aus der Versionstabelle ableitet. Ein `content_html`-Feld dient als berechnetes Zwischenergebnis für den PDF-Export und enthält den vom Backend gerenderten HTML-Code.

| Feldname | Typ | Beschreibung |
|---|---|---|
| `name` | Char | Dokumenttitel (Pflichtfeld) |
| `content_md` | Text | Markdown-Primärinhalt |
| `content_html` | Html | Gerendertes HTML (berechnet, für PDF) |
| `state` | Selection | Entwurf / Veröffentlicht / Archiviert |
| `owner_id` | Many2one → res.users | Eigentümer (Standard: aktueller Benutzer) |
| `version_ids` | One2many → x.md.document.version | Alle Versionen |
| `current_version` | Integer | Berechnet: höchste Versionsnummer |

**Versionsmodell `x.md.document.version`:**

Versionen sind append-only: Einmal angelegt, werden sie niemals verändert. Bei jeder Inhaltsänderung am Hauptdokument wird ein neuer Versionsrecord erstellt. Das Modell speichert den vollständigen Markdown-Inhalt der Version, einen MD5-Prüfsummenwert zur Integritätsprüfung, den verändernden Benutzer sowie Zeitstempel und Dateianhänge.

| Feldname | Typ | Beschreibung |
|---|---|---|
| `document_id` | Many2one → x.md.document | Verweis auf Dokument |
| `version` | Integer | Versionsnummer (1, 2, 3 …) |
| `content_md` | Text | Markdown-Inhalt dieser Version |
| `checksum` | Char | MD5-Prüfsumme des Inhalts |
| `changed_by` | Many2one → res.users | Wer hat geändert |
| `changed_at` | Datetime | Wann wurde geändert |
| `md_attachment_id` | Many2one → ir.attachment | .md-Datei dieser Version |
| `pdf_attachment_id` | Many2one → ir.attachment | .pdf-Datei dieser Version |

### 4.3 Sicherheitskonzept

Das Sicherheitskonzept nutzt zwei komplementäre Mechanismen des Odoo-Berechtigungssystems.

**Zugriffsrechte (ACL – Access Control List):**
Die Datei `security/ir.model.access.csv` definiert die CRUD-Berechtigungen auf Modellebene. Normale Benutzer (`base.group_user`) haben Lese-, Schreib- und Erstell-Rechte auf Dokumente, jedoch kein Löschrecht. Auf Versionsrecords haben normale Benutzer ausschließlich Leserecht – damit ist der Append-only-Charakter der Versionierung auf ACL-Ebene durchgesetzt. Administratoren (`base.group_system`) verfügen über vollständige CRUD-Rechte auf beiden Modellen.

**Record Rules (Datensatzregeln):**
Zugriffsrechte allein steuern den Zugriff auf der Modellebene, nicht auf der Datensatzebene. Datensatzregeln ergänzen das System um eine zeilenbasierte Zugriffskontrolle:

- Die **Eigentümer-Regel** schränkt den Zugriff normaler Benutzer auf Dokumente ein, deren `owner_id` mit dem aktuell angemeldeten Benutzer übereinstimmt: `[('owner_id', '=', user.id)]`.
- Die **Admin-Regel** gewährt Administratoren Zugriff auf alle Datensätze ohne Einschränkung: `[(1, '=', 1)]`.

**XSS-Schutz:**
Benutzereingaben im Markdown-Editor dürfen kein eingebettetes HTML ausführen. Im Frontend wird markdown-it mit der Option `html: false` initialisiert, wodurch HTML-Tags in Markdown-Texten escaped und nicht interpretiert werden. Im Backend verwendet mistune eine sichere Rendering-Pipeline ohne Ausführung von eingebettetem HTML. Die Verwendung von `markup()` aus der OWL-Bibliothek signalisiert dem Framework, dass der gerenderte Inhalt vertrauenswürdig ist – ohne diese Kennzeichnung würde das `t-out`-Direktiv den Inhalt ein zweites Mal escapen.

### 4.4 UI/UX-Konzept

Die Benutzeroberfläche orientiert sich an den Odoo-Designkonventionen und erweitert diese um ein unternehmensspezifisches Branding auf Basis der Trendtec-Farbe Lime Green (#97d21d).

**Split-View-Layout:** Der Editor ist in zwei gleich große vertikale Bereiche aufgeteilt. Links befindet sich der Eingabebereich mit dem CodeMirror-Syntaxeditor, rechts die live gerenderte Vorschau. Die Trennlinie zwischen beiden Bereichen ist visuell durch die Primärfarbe hervorgehoben.

**Typografie:** Für den Editor-Bereich wird die Programmierschrift JetBrains Mono verwendet. Die Vorschau nutzt Mulish und Inter als Fließtextschriften sowie Space Grotesk für Überschriften. Alle Schriftarten liegen lokal im Modulverzeichnis und werden ohne externe CDN-Aufrufe eingebunden.

**Dark-Mode:** Das Modul ist vollständig Dark-Mode-kompatibel. Farbwerte werden über CSS Custom Properties (`light-dark()`) definiert und reagieren automatisch auf den Odoo-Theme-Wechsel.

**Statusvisualisierung:** Der Dokumentstatus (Entwurf, Veröffentlicht, Archiviert) wird in der Listenansicht farblich als Badge dargestellt und ist über die Statusleiste in der Formularansicht nachvollziehbar.

---

## 5. Implementierungsphase

### 5.1 Modulstruktur

Das Modul trägt den technischen Namen `markdown_editor` und folgt der Odoo-Standardstruktur für Module. Die wichtigsten Verzeichnisse und Dateien sind:

```
markdown_editor/
├── __manifest__.py          # Modulmetadaten, Assets, Abhängigkeiten
├── models/
│   ├── md_document.py       # Hauptmodell und Versionsmodell
│   └── md_document_diff.py  # Vergleichsassistent
├── views/
│   ├── md_document_views.xml
│   └── md_document_diff_views.xml
├── static/
│   ├── lib/                 # markdown-it, CodeMirror (lokal)
│   └── src/
│       ├── js/              # OWL-Komponente
│       ├── xml/             # OWL-Template
│       └── scss/            # Styling, Branding, PDF-Styling
├── security/
│   ├── ir.model.access.csv
│   └── markdown_editor_security.xml
├── report/
│   └── md_document_report.xml
└── tests/
    └── test_md_document.py
```

Die Abhängigkeiten des Moduls beschränken sich auf `base` und `web`, die in jeder Odoo-Installation vorhanden sind. Bewusst wurde auf eine Abhängigkeit von `documents` (Odoo-Documents-App) verzichtet, um das Modul auch in Community-Installationen ohne Enterprise-Module nutzen zu können.

### 5.2 Backend-Implementierung

#### 5.2.1 Datenmodell (Python / Odoo ORM)

Die Modellklassen erben von `models.Model` und nutzen ausschließlich das Odoo ORM ohne rohe SQL-Abfragen. Der Eigentümer eines Dokuments wird beim Anlegen automatisch auf den aktuell eingeloggten Benutzer gesetzt:

```python
owner_id = fields.Many2one(
    "res.users",
    string="Eigentümer",
    default=lambda self: self.env.user,
)
```

Das berechnete Feld `current_version` aggregiert die höchste Versionsnummer aus der Versionstabelle:

```python
@api.depends("version_ids.version")
def _compute_current_version(self):
    for doc in self:
        doc.current_version = max(
            (v.version for v in doc.version_ids), default=0
        )
```

#### 5.2.2 Versionierungslogik

Die Versionierung wird automatisch bei zwei Ereignissen ausgelöst: beim Erstellen eines neuen Dokuments (`create`) und beim Schreiben auf das Feld `content_md` (`write`). Der `write`-Override prüft, ob der betroffene Schlüssel im übergebenen Wertedict enthalten ist, bevor die Versionierungslogik gestartet wird:

```python
def write(self, vals):
    res = super().write(vals)
    if "content_md" in vals:
        self._create_version()
    return res
```

Die Methode `_create_version()` koordiniert drei Teilaufgaben in getrennten Hilfsmethoden: das Anlegen der `.md`-Datei als Odoo-Attachment, das Rendern und Speichern der `.pdf`-Datei sowie das Anlegen des Versionsrecords. Fehler beim PDF-Rendering werden abgefangen und protokolliert, ohne die Versionierung zu unterbrechen – die Versionierung ist damit robust gegenüber Ausfällen des PDF-Dienstes.

Die MD5-Prüfsumme wird aus dem UTF-8-kodierten Markdown-Inhalt berechnet und dient der Integritätsprüfung:

```python
checksum = hashlib.md5(content.encode("utf-8")).hexdigest()
```

#### 5.2.3 PDF-Export

Das PDF-Rendering erfolgt über zwei Wege: Primär wird das beim Anlegen einer Version bereits gerenderte und gespeicherte PDF-Attachment ausgeliefert. Dieses Vorgehen vermeidet eine wiederholte Konvertierung bei jedem Exportaufruf. Als Fallback – falls kein Attachment vorhanden ist – wird der Odoo-Reportingmechanismus genutzt, der das QWeb-Template `report_md_document` mit wkhtmltopdf rendert.

Die serverseitige Markdown-zu-HTML-Konvertierung erfolgt über die Python-Bibliothek `mistune`. Das Ergebnis wird mit `Markup()` aus der `markupsafe`-Bibliothek als vertrauenswürdig markiert, damit das QWeb-Template den HTML-Code unescaped darstellt:

```python
def _markdown_to_html(self, text):
    if _mistune_available:
        return Markup(mistune.html(text or ""))
    return Markup("<pre>%s</pre>") % (text or "")
```

### 5.3 Frontend-Implementierung

#### 5.3.1 OWL-Komponente

Die Frontend-Kernkomponente `MarkdownField` ist als OWL-Klasse implementiert und wird über die Odoo-Field-Registry als Custom Widget unter dem Schlüssel `markdown_editor` registriert:

```javascript
registry.category("fields").add("markdown_editor", {
    component: MarkdownField,
    supportedTypes: ["text"],
});
```

In der Formularansicht wird das Widget über das Attribut `widget="markdown_editor"` auf dem `content_md`-Feld eingebunden. Die Komponente initialisiert bei der Montage (`onMounted`) eine CodeMirror-Instanz auf der Textarea und richtet einen debounced Change-Handler ein, der die Live-Vorschau mit einer Verzögerung von 300 Millisekunden aktualisiert. Diese Verzögerung verhindert, dass bei schneller Eingabe bei jedem Tastenanschlag ein vollständiges Re-Render ausgelöst wird.

Die Reaktivität des Zustands (`state`) wird über OWLs `useState`-Hook sichergestellt. Änderungen an `state.html` lösen automatisch ein Re-Render der Vorschau aus.

#### 5.3.2 Markdown-Rendering

Als Markdown-Renderer wird markdown-it in Version 14 verwendet, lokal eingebunden unter `static/lib/markdown-it.min.js`. Die Initialisierung erfolgt mit folgenden Optionen:

```javascript
window.markdownit({ html: false, breaks: true, linkify: true })
```

- `html: false` verhindert die Interpretation von eingebettetem HTML (XSS-Schutz).
- `breaks: true` wandelt einfache Zeilenumbrüche in `<br>`-Tags um.
- `linkify: true` erkennt URLs im Text und verlinkt sie automatisch.

Das Rendering-Ergebnis wird mit `markup()` aus `@odoo/owl` als vertrauenswürdiger HTML-String markiert, damit `t-out` im OWL-Template ihn unescaped darstellt.

#### 5.3.3 Layout und Styling

Das Split-View-Layout basiert auf CSS Flexbox. Editor-Pane und Vorschau-Pane haben jeweils eine feste Breite von 50 % des verfügbaren Platzes. Die Trennlinie wird über einen `border-right`-Stil des Editor-Pane erzeugt.

Für das Odoo-Layout-Integration waren zwei Anpassungen notwendig: Odoo setzt auf `.o_form_sheet_bg` eine maximale Breite von 1400 Pixeln, die auf breiten Bildschirmen Leerraum rechts erzeugt. Dieser Wert wird innerhalb des Modulscopes gezielt überschrieben. Außerdem wird `overflow: visible` auf `.o_form_sheet` gesetzt, damit Odoo-Dropdowns innerhalb der Formularansicht korrekt dargestellt werden.

Der Scope aller CSS-Regeln ist eng gefasst: Stile sind ausschließlich auf `.o_markdown_editor`, `.o_markdown_preview` und `.o_md_diff` angewendet, um Konflikte mit anderen Odoo-Modulen auszuschließen.

### 5.4 Sicherheitsintegration

#### 5.4.1 ACL-Konfiguration

Die Zugriffsberechtigungen sind in `security/ir.model.access.csv` definiert. Dort werden für jede Modell-Gruppen-Kombination die vier CRUD-Bits (Lesen, Schreiben, Erstellen, Löschen) gesetzt. Ein Auszug:

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_md_document_user,...,model_x_md_document,base.group_user,1,1,1,0
access_md_document_admin,...,model_x_md_document,base.group_system,1,1,1,1
access_md_version_user,...,model_x_md_document_version,base.group_user,1,0,0,0
```

Bemerkenswert ist, dass normale Benutzer auf dem Versionsmodell ausschließlich Leserecht haben. Das Erstellen neuer Versionsrecords ist damit nur serverseitig möglich – ein Benutzer kann über die UI keine Versionen manuell manipulieren.

#### 5.4.2 Record Rules

Die Datensatzregeln sind in `security/markdown_editor_security.xml` als XML definiert. Die Eigentümer-Regel gilt für alle Operationen (Lesen, Schreiben, Erstellen, Löschen) und ist der Gruppe `base.group_user` zugeordnet:

```xml
<record id="rule_md_document_owner" model="ir.rule">
    <field name="name">MD Document: Eigentümer-Zugriff</field>
    <field name="model_id" ref="model_x_md_document"/>
    <field name="domain_force">[('owner_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

#### 5.4.3 XSS-Schutz

Die XSS-Absicherung ist auf zwei Ebenen implementiert. Im Frontend escaped markdown-it mit `html: false` alle HTML-Tags in Benutzereingaben. Im Backend ist mistune so konfiguriert, dass kein schädliches JavaScript in das gerenderte HTML gelangen kann. Das `content_html`-Feld hat `sanitize=False`, weil die Odoo-interne `html_sanitize()`-Funktion die `Markup()`-Kennzeichnung entfernt – was dazu führen würde, dass `t-out` den Inhalt erneut escaped. Der XSS-Schutz ist in diesem Fall bewusst der Anwendungsschicht (mistune) übertragen.

---

## 6. Testphase

### 6.1 Testkonzept

Das Testkonzept umfasst zwei Ebenen: automatisierte Backend-Tests mit dem Odoo-Testframework sowie manuelle Integrationstests in der laufenden Odoo-Instanz.

Für die automatisierten Tests wird die Klasse `TransactionCase` des Odoo-Testframeworks verwendet. Diese rollt nach jedem Testfall die Datenbankänderungen automatisch zurück, sodass Tests isoliert und ohne gegenseitige Beeinflussung ausgeführt werden können. Die Tests decken die kritischen Pfade der Geschäftslogik ab: Versionierung, Zugriffskontrolle, Versionsvergleich und Fehler-Fallbacks.

Die Testdatei liegt unter `tests/test_md_document.py` und wird mit folgendem Befehl ausgeführt:

```bash
./odoo-bin test -m markdown_editor -d <datenbankname>
```

### 6.2 Testfälle

**Testgruppe 1: Versionierung (TestMdDocumentVersioning)**

| Nr. | Beschreibung | Erwartetes Ergebnis |
|---|---|---|
| T1.1 | Neues Dokument anlegen | Version 1 wird automatisch erstellt |
| T1.2 | Inhalt schreiben | Neue Version wird angelegt |
| T1.3 | MD5-Prüfsumme | Stimmt mit `hashlib.md5(content.encode()).hexdigest()` überein |
| T1.4 | `changed_by`-Feld | Enthält den aktuell eingeloggten Benutzer |
| T1.5 | Restore-Funktion | Stellt älteren Inhalt wieder her und erzeugt neue Version |
| T1.6 | Mehrfaches Schreiben | Versionsnummern steigen monoton an (1, 2, 3 …) |

**Testgruppe 2: Zugriffskontrolle (TestMdDocumentACL)**

| Nr. | Beschreibung | Erwartetes Ergebnis |
|---|---|---|
| T2.1 | Eigentümer liest eigenes Dokument | Zugriff erlaubt |
| T2.2 | Fremder Benutzer liest Dokument eines anderen | Zugriff verweigert (kein Ergebnis) |
| T2.3 | Normaler Benutzer erstellt Version | Zugriff verweigert (AccessError) |

**Testgruppe 3: Versionsvergleich (TestMdDocumentDiff)**

| Nr. | Beschreibung | Erwartetes Ergebnis |
|---|---|---|
| T3.1 | Hinzugefügte Zeilen | `+`-markierte Zeilen im Diff |
| T3.2 | Gelöschte Zeilen | `-`-markierte Zeilen im Diff |
| T3.3 | Keine Änderungen | Meldung „Keine Unterschiede" |
| T3.4 | Dokument ohne Versionen | Leeres Ergebnis, kein Absturz |

**Testgruppe 4: Fehler-Fallbacks (TestMdDocumentFallback)**

| Nr. | Beschreibung | Erwartetes Ergebnis |
|---|---|---|
| T4.1 | PDF-Rendering schlägt fehl | Versionierung wird trotzdem abgeschlossen |
| T4.2 | Leerer Inhalt | `content_html` enthält leeres `<pre>`-Element |

### 6.3 Testergebnisse

Alle 17 automatisierten Testfälle wurden erfolgreich abgeschlossen. Kein Test schlägt fehl. Die Testergebnisse wurden auf der Odoo.sh-Instanz verifiziert.

Im Rahmen der manuellen Integrationstests wurden folgende Szenarien geprüft:

- Anlegen, Bearbeiten und Veröffentlichen eines Dokuments im Browser
- Korrekte Darstellung der Live-Vorschau mit verschiedenen Markdown-Elementen (Überschriften, Listen, Code-Blöcke, Tabellen, Blockzitate, Links)
- PDF-Export: Korrekte Darstellung von Formatierungen, Metadaten-Header, Zeichensatz
- Versionsvergleich: Korrekte farbliche Darstellung von Änderungen
- Zugriffstest: Anmeldung als separater Testbenutzer, Bestätigung dass keine fremden Dokumente sichtbar sind
- Dark-Mode: Korrekte Darstellung nach Theme-Wechsel in Odoo

Alle manuellen Tests verliefen ohne Beanstandungen.

---

## 7. Fazit

### 7.1 Soll-/Ist-Vergleich der Zeitplanung

| Phase | Geplant | Tatsächlich | Differenz |
|---|---|---|---|
| Analyse | 8 h | 8 h | ± 0 h |
| Entwurf | 10 h | 10 h | ± 0 h |
| Implementierung | 40 h | 40 h | ± 0 h |
| Test | 10 h | 10 h | ± 0 h |
| Dokumentation | 12 h | 12 h | ± 0 h |
| **Gesamt** | **80 h** | **80 h** | **± 0 h** |

Das Projekt wurde innerhalb des geplanten Zeitrahmens abgeschlossen. Innerhalb der Implementierungsphase ergaben sich kleinere Verschiebungen zwischen den Teilbereichen: Die Backend-Entwicklung verlief zügiger als erwartet, da das Odoo ORM gut dokumentiert ist und wenige Überraschungen bereithielt. Die zusätzliche Zeit floss in die Frontend-Integration, insbesondere in die korrekte Einbindung von CodeMirror in den OWL-Komponentenlebenszyklus und die Behebung von Odoo-Layout-Konflikten.

Alle acht Pflichtanforderungen aus dem Projektantrag wurden vollständig erfüllt. Darüber hinaus wurden die Statusverwaltung (Entwurf, Veröffentlicht, Archiviert) und die Restore-Funktion als sinnvolle Erweiterung der Änderungsverfolgung implementiert.

### 7.2 Reflexion und Lessons Learned

Das Projekt hat mehrere technische Lerneffekte hervorgebracht, die für zukünftige Odoo-Entwicklungen relevant sind.

**Odoo OWL-Komponentenlebenszyklus:** Die Integration einer externen JavaScript-Bibliothek (CodeMirror) in eine OWL-Komponente erfordert eine sorgfältige Handhabung der Lifecycle-Callbacks. `onMounted` und `onWillUnmount` sind der korrekte Ort für Initialisierung und Bereinigung von DOM-basierten Bibliotheken. Ein frühes Verständnis dieser Lifecycle-Reihenfolge hätte einige Debugging-Schleifen vermieden.

**CSS-Scoping in Odoo:** Odoo Enterprise-Layouts setzen teils aggressive globale CSS-Regeln, die lokale Modul-Styles überschreiben können. Die konsequente Verwendung des `:has()`-Pseudoselektors und scoped CSS-Selektoren hat sich als robuste Strategie bewährt, um Konflikte zu vermeiden.

**Trennung von Render-Ebenen:** Das korrekte Zusammenspiel von `mistune`, `Markup()`, `sanitize=False` und `t-out` im Kontext des Odoo-Reportings erforderte ein genaues Verständnis der mehrschichtigen Escaping-Pipeline. Die Dokumentation dieses Zusammenspiels hat sich als wichtige Wissensressource für das Team erwiesen.

**PDF-Rendering mit wkhtmltopdf:** Die Unterschiede zwischen wkhtmltopdf (QtWebKit) und modernen Browsern sind erheblich. Variable Fonts, CSS Custom Properties und einige moderne CSS-Features werden von wkhtmltopdf nicht unterstützt. Für PDF-spezifisches Styling müssen statische Font-Schnitte und SCSS-Variablen statt CSS Custom Properties verwendet werden.

### 7.3 Ausblick

Das implementierte Modul stellt eine vollständige und produktionsreife Lösung für die ursprünglich definierten Anforderungen dar. Für zukünftige Iterationen sind folgende Erweiterungen denkbar:

**Kurzfristig (nächste Entwicklungsiteration):**
- Performance-Optimierung der Live-Vorschau bei sehr langen Dokumenten (> 10.000 Zeilen) durch virtuelles Rendering oder gezieltes Debouncing.
- Erweiterte Suchfunktion: Volltextsuche im Markdown-Inhalt über die Odoo-Search-View.

**Mittelfristig:**
- Kommentarfunktion: Anmerkungen zu einzelnen Versionen, ohne das Hauptversionsmodell zu erweitern.
- Vorlagen-System: Vordefinierte Markdown-Templates für häufig verwendete Dokumententypen (API-Dokumentation, Installationsanleitung, Changelog).

**Langfristig:**
- Einsatz in Kundenprojekten als eigenständig konfigurierbares Modul mit anpassbarem Branding.

---

## 8. Anhang

### A: Abkürzungsverzeichnis

| Abkürzung | Bedeutung |
|---|---|
| ACL | Access Control List (Zugriffssteuerungsliste) |
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| CDN | Content Delivery Network |
| ERP | Enterprise Resource Planning |
| HTML | HyperText Markup Language |
| MD5 | Message-Digest Algorithm 5 (Prüfsummenverfahren) |
| ORM | Object-Relational Mapper |
| OWL | Odoo Web Library (Frontend-Framework) |
| PDF | Portable Document Format |
| SCSS | Sassy Cascading Style Sheets |
| SQL | Structured Query Language |
| SaaS | Software as a Service |
| UI | User Interface |
| UX | User Experience |
| XSS | Cross-Site Scripting |

### B: Glossar

**Append-only:** Eigenschaft eines Datenspeichers, bei dem neue Einträge ausschließlich angefügt, bestehende Einträge jedoch niemals geändert oder gelöscht werden. Im Kontext von MDWriter gilt dies für das Versionsmodell.

**CodeMirror:** Eine JavaScript-Bibliothek für die Implementierung von Code-Editoren im Browser. MDWriter nutzt CodeMirror 5 mit dem Markdown-Modus für Syntax-Highlighting im Eingabebereich.

**markdown-it:** Eine JavaScript-Bibliothek zur Konvertierung von Markdown-Text in HTML. Wird im Frontend für die Live-Vorschau eingesetzt.

**mistune:** Eine Python-Bibliothek zur Konvertierung von Markdown-Text in HTML. Wird im Backend für das PDF-Rendering eingesetzt.

**OWL (Odoo Web Library):** Das seit Odoo 14 eingesetzte reaktive Frontend-Framework von Odoo. Basiert auf Komponenten, reaktiven Zuständen und einem Template-System (XML/QWeb).

**QWeb:** Die Template-Engine von Odoo. Wird sowohl für HTML-Frontend-Templates als auch für PDF-Report-Templates verwendet. Direktiven beginnen mit `t-` (z. B. `t-out`, `t-foreach`).

**Record Rule (Datensatzregel):** Eine Odoo-Funktion zur zeilenbasierten Zugriffskontrolle. Während ACL-Regeln auf Modellebene wirken, schränken Record Rules den Zugriff auf einzelne Datensätze ein.

**Split-View:** Eine Ansicht, bei der der Bildschirm in zwei nebeneinanderliegende Bereiche aufgeteilt ist. Im MDWriter-Kontext: Eingabebereich (links) und Vorschaubereich (rechts).

**TransactionCase:** Eine Basisklasse des Odoo-Testframeworks. Jeder Testfall wird in einer Datenbanktransaktion ausgeführt, die nach Testabschluss zurückgerollt wird – dadurch bleiben Tests isoliert.

**wkhtmltopdf:** Ein Kommandozeilenwerkzeug zur Konvertierung von HTML in PDF, das auf der QtWebKit-Rendering-Engine basiert. Wird von Odoo für die PDF-Generierung über Reports verwendet.

### C: Quellenverzeichnis

| Nr. | Quelle |
|---|---|
| [1] | Odoo S.A.: *Odoo 19 Developer Documentation*. https://www.odoo.com/documentation/19.0/ |
| [2] | Odoo S.A.: *OWL (Odoo Web Library) Documentation*. https://github.com/odoo/owl |
| [3] | markdown-it: *markdown-it – Markdown Parser, Done Right*. https://github.com/markdown-it/markdown-it |
| [4] | CodeMirror: *CodeMirror 5 User Manual*. https://codemirror.net/5/doc/manual.html |
| [5] | Leporati, T.: *mistune – A fast yet powerful Python Markdown parser*. https://github.com/lepture/mistune |
| [6] | Mozilla Developer Network: *CSS :has() pseudo-class*. https://developer.mozilla.org/en-US/docs/Web/CSS/:has |
| [7] | OWASP Foundation: *Cross Site Scripting (XSS)*. https://owasp.org/www-community/attacks/xss/ |
