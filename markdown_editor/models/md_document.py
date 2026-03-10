import base64
import hashlib
import logging
from datetime import datetime

try:
    import mistune
    _mistune_available = True
except ImportError:
    _mistune_available = False

from markupsafe import Markup
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class XMdDocument(models.Model):
    """
    Hauptmodell für Markdown‑Dokumente.

    Dieses Modell speichert den aktuellen Markdown‑Inhalt und verwaltet
    Versionen sowie zugehörige Attachments. Jede Änderung am
    Inhalt führt zu einer neuen Version in ``x.md.document.version``.
    """

    _name = "x.md.document"
    _description = "Markdown Document"

    name = fields.Char(string="Titel", required=True)
    content_md = fields.Text(string="Markdown‑Inhalt")
    state = fields.Selection([
        ("draft", "Entwurf"),
        ("published", "Veröffentlicht"),
        ("archived", "Archiviert"),
    ], default="draft")
    owner_id = fields.Many2one(
        comodel_name="res.users",
        string="Eigentümer",
        default=lambda self: self.env.user,
    )
    version_ids = fields.One2many(
        comodel_name="x.md.document.version",
        inverse_name="document_id",
        string="Versionen",
    )
    current_version = fields.Integer(
        string="Aktuelle Version",
        compute="_compute_current_version",
        store=True,
    )
    content_html = fields.Html(
        string="HTML-Vorschau",
        compute="_compute_content_html",
        sanitize=True,
    )

    @api.depends("version_ids.version")
    def _compute_current_version(self):
        for doc in self:
            if doc.version_ids:
                doc.current_version = max(doc.version_ids.mapped("version"))
            else:
                doc.current_version = 0

    @api.depends("content_md")
    def _compute_content_html(self):
        for doc in self:
            if not doc.content_md:
                doc.content_html = ""
            elif _mistune_available:
                doc.content_html = Markup(mistune.html(doc.content_md))
            else:
                _logger.warning("mistune nicht installiert — PDF zeigt rohen Markdown-Text")
                doc.content_html = Markup("<pre>%s</pre>") % (doc.content_md or "")

    def _create_version(self):
        """
        Erzeugt eine neue Version des Dokuments. Diese Methode wird
        automatisch beim Erstellen und Aktualisieren eines Dokumentes
        aufgerufen. Sie speichert den Markdown‑Inhalt als Attachment
        und erzeugt optional einen PDF‑Attachment über einen QWeb‑Report.
        """
        # sudo(): Versionierung ist ein System-Mechanismus.
        # Normale User haben kein perm_create auf x.md.document.version,
        # aber das System muss bei jedem Speichern eine Version anlegen.
        Attachment = self.env["ir.attachment"].sudo()
        Version = self.env["x.md.document.version"].sudo()

        for record in self:
            # Bestimme die nächste Versionsnummer
            next_version = record.current_version + 1
            md_content = record.content_md or ""
            checksum = hashlib.md5(md_content.encode("utf-8")).hexdigest()

            # Markdown als Attachment speichern
            md_name = f"{record.name}_v{next_version}.md"
            md_attachment = Attachment.create({
                "name": md_name,
                "datas": base64.b64encode(md_content.encode("utf-8")),
                "mimetype": "text/markdown",
                "res_model": record._name,
                "res_id": record.id,
            })

            # Versuche, einen PDF‑Report zu rendern. Falls dies fehlschlägt,
            # wird das PDF‑Attachment leer bleiben. Die tatsächliche
            # PDF‑Konvertierung erfolgt mittels eines QWeb‑Reports.
            pdf_attachment = False
            try:
                # Odoo 19: _render_qweb_pdf(report_ref, res_ids) statt report._render_qweb_pdf(ids)
                Report = self.env["ir.actions.report"]
                report_exists = self.env.ref("markdown_editor.md_document_pdf", raise_if_not_found=False)
                if report_exists:
                    pdf_bytes, _content_type = Report._render_qweb_pdf(
                        "markdown_editor.md_document_pdf", res_ids=[record.id]
                    )
                    pdf_name = f"{record.name}_v{next_version}.pdf"
                    pdf_attachment = Attachment.create({
                        "name": pdf_name,
                        "datas": base64.b64encode(pdf_bytes),
                        "mimetype": "application/pdf",
                        "res_model": record._name,
                        "res_id": record.id,
                    })
            except Exception as e:
                _logger.warning("PDF render failed: %s", e)

            # Neue Version anlegen
            Version.create({
                "document_id": record.id,
                "version": next_version,
                "content_md": md_content,
                "checksum": checksum,
                "changed_by": self.env.user.id,
                "changed_at": fields.Datetime.now(),
                "md_attachment_id": md_attachment.id,
                "pdf_attachment_id": pdf_attachment.id if pdf_attachment else False,
            })

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_publish(self):
        self.write({"state": "published"})

    def action_archive_doc(self):
        self.write({"state": "archived"})

    def action_open_diff(self):
        """Öffnet den Versionsdiff-Wizard für dieses Dokument."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "x.md.document.diff.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_document_id": self.id},
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._create_version()
        return records

    def write(self, vals):
        res = super().write(vals)
        # Bei jeder Änderung des Markdown‑Inhalts eine neue Version erzeugen
        if "content_md" in vals:
            self._create_version()
        return res


class XMdDocumentVersion(models.Model):
    """
    Versionierungsmodell für Markdown‑Dokumente.
    Jede Änderung an ``x.md.document`` erzeugt einen neuen Datensatz
    in diesem Modell. Versionen sind append‑only und enthalten
    Referenzen auf die gespeicherten Attachments.
    """

    _name = "x.md.document.version"
    _description = "Markdown Document Version"
    _order = "version desc"

    document_id = fields.Many2one(
        comodel_name="x.md.document",
        string="Dokument",
        required=True,
        ondelete="cascade",
    )
    version = fields.Integer(string="Version", required=True)
    content_md = fields.Text(string="Markdown‑Inhalt")
    checksum = fields.Char(string="Checksumme", size=32)
    changed_by = fields.Many2one(
        comodel_name="res.users",
        string="Geändert von",
    )
    changed_at = fields.Datetime(string="Geändert am")
    md_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Markdown‑Anhang",
    )
    pdf_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="PDF‑Anhang",
    )

    def action_restore(self):
        """
        Stellt den Markdown‑Inhalt dieser Version im übergeordneten Dokument
        wieder her. Löst dabei automatisch eine neue Version aus (via write).
        """
        self.ensure_one()
        self.document_id.write({"content_md": self.content_md})
        return {
            "type": "ir.actions.act_window",
            "res_model": "x.md.document",
            "res_id": self.document_id.id,
            "view_mode": "form",
            "target": "current",
        }