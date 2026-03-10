# =============================================================================
# md_document.py – Datenmodell für Markdown-Dokumente
# =============================================================================
# Diese Datei definiert die Kernmodelle des MDWriter-Moduls:
#   - XMdDocument:        Ein Markdown-Dokument (Titel, Inhalt, Status, Eigentümer)
#   - XMdDocumentVersion: Eine gespeicherte Version eines Dokuments (append-only)
#
# In Odoo werden Datenmodelle als Python-Klassen geschrieben. Jedes Modell
# entspricht einer Tabelle in der Datenbank. Odoo erstellt und verwaltet
# diese Tabellen automatisch – wir müssen nur die Felder definieren.
# =============================================================================

import base64      # Zum Kodieren von Dateien (z.B. Anhänge als Text speichern)
import hashlib     # Zum Erstellen von MD5-Prüfsummen (Fingerabdruck eines Textes)
import logging     # Zum Schreiben von Log-Meldungen (z.B. Warnungen)

# mistune ist eine externe Python-Bibliothek, die Markdown in HTML umwandelt.
# try/except: Falls mistune nicht installiert ist, wird _mistune_available auf False gesetzt,
# und der Rest des Programms läuft trotzdem – nur der PDF-Export zeigt dann reinen Text.
try:
    import mistune
    _mistune_available = True
except ImportError:
    _mistune_available = False

# Markup schützt HTML-Strings vor doppeltem Escaping (wichtig für XSS-Schutz).
from markupsafe import Markup

# Odoo-spezifische Imports:
# - api:    Dekoratoren wie @api.depends (automatische Neuberechnung von Feldern)
# - fields: Feldtypen (Char, Text, Integer, Many2one usw.)
# - models: Basisklassen für Odoo-Modelle
from odoo import api, fields, models

# Logger für diese Datei. __name__ ist der Modulname (z.B. "markdown_editor.models.md_document").
# So kann man in den Odoo-Logs genau sehen, woher eine Meldung kommt.
_logger = logging.getLogger(__name__)


# =============================================================================
# Klasse: XMdDocument
# =============================================================================
# Eine Klasse in Python ist eine Vorlage (Blueprint) für Objekte.
# Hier erbt XMdDocument von models.Model – das macht sie zu einem Odoo-Modell.
# "Erben" bedeutet: Diese Klasse bekommt alle Funktionen von models.Model
# plus die eigenen Felder und Methoden, die wir hier definieren.
class XMdDocument(models.Model):
    # _name ist der technische Name des Modells in Odoo und in der Datenbank.
    _name = "x.md.document"
    _description = "Markdown Document"

    # -------------------------------------------------------------------------
    # Felder (= Spalten in der Datenbank)
    # -------------------------------------------------------------------------
    # Jedes Feld entspricht einer Spalte in der Datenbanktabelle.
    # Odoo erstellt diese Spalten automatisch beim Installieren des Moduls.

    name = fields.Char(string="Titel", required=True)   # Pflichtfeld: Dokumenttitel
    content_md = fields.Text(string="Markdown‑Inhalt")  # Der eigentliche Markdown-Text

    # Selection: Dropdown-Feld mit festen Auswahlmöglichkeiten.
    # Jedes Paar ist ("gespeicherter_wert", "Anzeigename").
    state = fields.Selection([
        ("draft", "Entwurf"),
        ("published", "Veröffentlicht"),
        ("archived", "Archiviert"),
    ], default="draft")

    # Many2one: Verknüpfung zu einem anderen Modell (hier: Benutzer).
    # "default=lambda self: self.env.user" setzt automatisch den angemeldeten User.
    # Lambda ist eine Mini-Funktion ohne Namen – hier: "gib den aktuellen User zurück".
    owner_id = fields.Many2one(
        comodel_name="res.users",
        string="Eigentümer",
        default=lambda self: self.env.user,
    )

    # One2many: Liste aller Versionen, die zu diesem Dokument gehören.
    # inverse_name zeigt auf das Feld in der Versions-Klasse, das zurückverweist.
    version_ids = fields.One2many(
        comodel_name="x.md.document.version",
        inverse_name="document_id",
        string="Versionen",
    )

    # Computed fields werden nicht direkt eingegeben, sondern automatisch berechnet.
    # store=True bedeutet: Das Ergebnis wird in der Datenbank gespeichert (nicht nur im Speicher).
    current_version = fields.Integer(
        string="Aktuelle Version",
        compute="_compute_current_version",
        store=True,
    )
    content_html = fields.Html(
        string="HTML-Vorschau",
        compute="_compute_content_html",
        sanitize=True,  # Odoo bereinigt das HTML automatisch (Schutz vor XSS-Angriffen)
    )

    # -------------------------------------------------------------------------
    # Computed-Field-Methoden
    # -------------------------------------------------------------------------

    # @api.depends sagt Odoo: "Berechne dieses Feld neu, wenn sich version_ids.version ändert."
    # self ist die Referenz auf das aktuelle Objekt (wie "ich" in einer natürlichen Sprache).
    # In Odoo kann self auch eine ganze Liste von Datensätzen sein – deshalb die for-Schleife.
    @api.depends("version_ids.version")
    def _compute_current_version(self):
        for doc in self:
            # max() mit default=0: Wenn keine Versionen vorhanden sind, ist das Maximum 0.
            # .mapped("version") gibt eine Liste aller Versionsnummern zurück.
            doc.current_version = max(doc.version_ids.mapped("version"), default=0)

    @api.depends("content_md")
    def _compute_content_html(self):
        for doc in self:
            if not doc.content_md:
                doc.content_html = ""
                continue  # Überspringe den Rest der Schleife für dieses Dokument

            if _mistune_available:
                # mistune.html() wandelt Markdown-Text in HTML-Code um.
                # Markup() sagt Odoo/Jinja: "Dieses HTML ist sicher – nicht nochmal escapen."
                doc.content_html = Markup(mistune.html(doc.content_md))
            else:
                _logger.warning("mistune nicht installiert — PDF zeigt rohen Markdown-Text")
                # %s ist ein Platzhalter – Markup ersetzt ihn sicher durch den Inhalt.
                doc.content_html = Markup("<pre>%s</pre>") % doc.content_md

    # -------------------------------------------------------------------------
    # Versionierungs-Hilfsmethoden (private, Konvention: Unterstrich am Anfang)
    # -------------------------------------------------------------------------

    def _create_md_attachment(self, record, content, version_num):
        """Speichert den Markdown-Text als .md-Datei in Odoo (als Attachment/Anhang)."""
        # base64.b64encode() kodiert den Text als Base64 – Odoo speichert Anhänge so.
        # .encode("utf-8") wandelt den Python-String in Bytes um (nötig für base64).
        return self.env["ir.attachment"].sudo().create({
            # f-String: geschweifte Klammern werden durch den Variablenwert ersetzt
            "name": f"{record.name}_v{version_num}.md",
            "datas": base64.b64encode(content.encode("utf-8")),
            "mimetype": "text/markdown",
            "res_model": record._name,  # Verknüpfung: Anhang gehört zu diesem Modell
            "res_id": record.id,        # Verknüpfung: Anhang gehört zu diesem Datensatz
        })

    def _create_pdf_attachment(self, record, version_num):
        """Rendert und speichert einen PDF-Report als Anhang. Gibt False zurück bei Fehler."""
        try:
            # self.env.ref() sucht eine XML-Referenz (hier: den Report-Eintrag).
            # raise_if_not_found=False: Kein Fehler, wenn der Report nicht existiert.
            report = self.env.ref("markdown_editor.md_document_pdf", raise_if_not_found=False)
            if not report:
                return False  # Kein Report definiert – nichts zu tun

            # Den PDF-Report für diesen Datensatz rendern.
            # _ ist eine Konvention für "diesen Wert brauchen wir nicht" (hier: Content-Type).
            pdf_bytes, _ = self.env["ir.actions.report"]._render_qweb_pdf(
                "markdown_editor.md_document_pdf", res_ids=[record.id]
            )
            return self.env["ir.attachment"].sudo().create({
                "name": f"{record.name}_v{version_num}.pdf",
                "datas": base64.b64encode(pdf_bytes),
                "mimetype": "application/pdf",
                "res_model": record._name,
                "res_id": record.id,
            })
        except (OSError, ValueError, Exception) as e:
            # OSError:    wkhtmltopdf nicht installiert oder Prozess-Fehler
            # ValueError: ungültige Report-Konfiguration
            # Exception:  alle anderen unerwarteten Fehler (breit, aber mit Logging)
            # In allen Fällen: nur warnen und False zurückgeben – Versionierung läuft weiter.
            _logger.warning("PDF render failed for record %s v%s: %s", record.id, version_num, e)
            return False

    def _create_version(self):
        """Legt eine neue append-only Version an. Wird bei create/write ausgelöst.

        Append-only bedeutet: Versionen werden nur hinzugefügt, nie verändert.
        So bleibt die vollständige Änderungshistorie immer erhalten.
        """
        # .sudo() umgeht die normalen Zugriffsrechte – nötig, weil normale User
        # keine Versions-Datensätze direkt anlegen dürfen (ACL), das System aber schon.
        Version = self.env["x.md.document.version"].sudo()

        # self kann mehrere Datensätze enthalten (z.B. beim Massenimport).
        for record in self:
            content = record.content_md or ""  # Falls leer: leeren String verwenden
            next_version = record.current_version + 1

            md_att = self._create_md_attachment(record, content, next_version)
            pdf_att = self._create_pdf_attachment(record, next_version)

            Version.create({
                "document_id": record.id,
                "version": next_version,
                "content_md": content,
                # MD5-Prüfsumme: eindeutiger "Fingerabdruck" des Inhalts.
                # So kann man später prüfen, ob sich der Inhalt verändert hat.
                "checksum": hashlib.md5(content.encode("utf-8")).hexdigest(),
                "changed_by": self.env.user.id,  # Wer hat die Änderung gemacht?
                "changed_at": fields.Datetime.now(),
                "md_attachment_id": md_att.id,
                # Ternärer Ausdruck: "pdf_att.id wenn pdf_att existiert, sonst False"
                "pdf_attachment_id": pdf_att.id if pdf_att else False,
            })

    # -------------------------------------------------------------------------
    # Status-Aktionen (werden von den Buttons im Form-View aufgerufen)
    # -------------------------------------------------------------------------

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_publish(self):
        self.write({"state": "published"})

    def action_archive_doc(self):
        self.write({"state": "archived"})

    def action_download_md(self):
        """Lädt die .md-Datei der aktuellen Version herunter.

        Gibt eine act_url-Aktion zurück – Odoo öffnet die URL im Browser,
        der ?download=true-Parameter löst den Datei-Download aus.
        target="new" öffnet einen neuen Tab, damit man auf der Seite bleibt.
        """
        self.ensure_one()
        # Aktuelle Version über die gespeicherte Versionsnummer finden
        latest = self.version_ids.filtered(lambda v: v.version == self.current_version)
        if not latest or not latest.md_attachment_id:
            return False
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{latest.md_attachment_id.id}?download=true",
            "target": "new",
        }

    def action_open_diff(self):
        """Öffnet den Versionsdiff-Wizard für dieses Dokument.

        Gibt ein Dictionary zurück, das Odoo anweist, ein neues Fenster zu öffnen.
        Das ist das Standard-Muster für Odoo-Aktionen.
        """
        self.ensure_one()  # Sicherheitscheck: Diese Methode funktioniert nur für genau 1 Datensatz
        return {
            "type": "ir.actions.act_window",
            "res_model": "x.md.document.diff.wizard",
            "view_mode": "form",
            "target": "new",   # "new" = Dialog-Fenster statt neue Seite
            "context": {"default_document_id": self.id},  # Dokument vorausfüllen
        }

    # -------------------------------------------------------------------------
    # ORM-Hooks: Odoo ruft diese Methoden automatisch auf
    # -------------------------------------------------------------------------

    # @api.model_create_multi ermöglicht das Erstellen mehrerer Datensätze auf einmal.
    # vals_list ist eine Liste von Dictionaries (ein Dictionary pro neuem Datensatz).
    @api.model_create_multi
    def create(self, vals_list):
        # super() ruft die Originalversion von create() aus models.Model auf.
        # Das ist nötig, damit Odoo alle normalen Dinge beim Erstellen macht.
        records = super().create(vals_list)
        records._create_version()  # Danach: erste Version anlegen
        return records

    def write(self, vals):
        # vals ist ein Dictionary mit den geänderten Feldern, z.B. {"content_md": "neuer Text"}
        res = super().write(vals)
        # Nur wenn der Markdown-Inhalt geändert wurde, eine neue Version anlegen.
        # "in" prüft, ob ein Key in einem Dictionary vorhanden ist.
        if "content_md" in vals:
            self._create_version()
        return res


# =============================================================================
# Klasse: XMdDocumentVersion
# =============================================================================
# Speichert den Zustand eines Dokuments zu einem bestimmten Zeitpunkt.
# Versionen sind append-only: Einmal angelegt, werden sie nie mehr verändert.
# Das sichert die Integrität der Änderungshistorie.
class XMdDocumentVersion(models.Model):
    _name = "x.md.document.version"
    _description = "Markdown Document Version"
    _order = "version desc"  # Neueste Version zuerst in Listen anzeigen

    # Pflichtfeld: Jede Version gehört zu genau einem Dokument.
    # ondelete="cascade": Wenn das Dokument gelöscht wird, werden alle Versionen mitgelöscht.
    document_id = fields.Many2one(
        comodel_name="x.md.document",
        string="Dokument",
        required=True,
        ondelete="cascade",
    )
    version = fields.Integer(string="Version", required=True)  # 1, 2, 3, ...
    content_md = fields.Text(string="Markdown‑Inhalt")        # Snapshot des Inhalts
    checksum = fields.Char(string="Checksumme", size=32)      # MD5-Hash (32 Zeichen)
    changed_by = fields.Many2one(comodel_name="res.users", string="Geändert von")
    changed_at = fields.Datetime(string="Geändert am")
    md_attachment_id = fields.Many2one(comodel_name="ir.attachment", string="Markdown‑Anhang")
    pdf_attachment_id = fields.Many2one(comodel_name="ir.attachment", string="PDF‑Anhang")

    def action_restore(self):
        """Stellt diesen Versionsstand im Dokument wieder her.

        Wichtig: Restore löscht keine anderen Versionen – es schreibt den alten Inhalt
        zurück, was automatisch eine neue Version erzeugt. Die Historie bleibt vollständig.
        """
        self.ensure_one()
        # write() auf dem übergeordneten Dokument → löst _create_version() aus (via ORM-Hook)
        self.document_id.write({"content_md": self.content_md})
        # Zurück zur Form-Ansicht des Dokuments navigieren
        return {
            "type": "ir.actions.act_window",
            "res_model": "x.md.document",
            "res_id": self.document_id.id,
            "view_mode": "form",
            "target": "current",
        }
