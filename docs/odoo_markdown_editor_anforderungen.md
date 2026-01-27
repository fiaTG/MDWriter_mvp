# Technische Anforderungsliste -- Odoo Markdown Editor App (Odoo 19)

## 1. Ziel & Scope

### Ziel

-   Markdown-basierter Editor in Odoo
-   Split View: Editor links, Live-Vorschau rechts
-   Speicherung als Markdown-Datei in Odoo
-   PDF-Konvertierung und Speicherung in Odoo
-   Audittrail und Versionierung
-   Eigene UI via OWL + SCSS

### Nicht-Ziele

-   Kein WYSIWYG-HTML-Editor
-   Kein externes Filesystem als Primary Storage

## 2. Benutzerrollen & Use Cases

### Rollen

-   Reader
-   Editor
-   Admin

### Use Cases

-   Dokument erstellen, bearbeiten, speichern
-   Live-Vorschau
-   PDF generieren
-   Versionen einsehen
-   Audittrail prüfen

## 3. Funktionale Anforderungen

### Editor

-   OWL Markdown Editor
-   Live Preview
-   Autosave
-   Split Layout

### Speicherung

-   Markdown im Datenmodell
-   Markdown als Attachment (.md)
-   PDF als Attachment (.pdf)

## 4. Datenmodell

### x_md_document

-   name
-   content_md
-   state
-   owner_id
-   current_version

### x_md_document_version

-   document_id
-   version
-   content_md
-   checksum
-   changed_by
-   changed_at
-   md_attachment_id
-   pdf_attachment_id

## 5. Sicherheit

-   ACL + Record Rules
-   Attachment-Sicherheit
-   XSS-Schutz
-   Append-only Versionierung
-   Hash/Checksum

## 6. Audittrail

-   Jede Änderung erzeugt Version
-   UI History View
-   Diff + Restore
-   Exportfähig

## 7. UI/Frontend

-   OWL Komponenten
-   Eigenes SCSS
-   Dark Mode kompatibel
-   Performance Optimierung

## 8. PDF Rendering

-   Markdown → HTML → PDF
-   Layout CSS
-   Versionierte Speicherung

## 9. Tests

-   ACL Tests
-   Versionierungs Tests
-   UI Tests
-   Security Tests

## 10. Deployment

-   Odoo 19 kompatibel
-   Upgradefähig
-   Konfigurierbar
