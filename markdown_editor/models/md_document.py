import base64
import hashlib
import logging

try:
    import mistune
    _mistune_available = True
except ImportError:
    _mistune_available = False

from markupsafe import Markup
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class XMdDocument(models.Model):
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
        sanitize=False,  # sanitize=True würde html_sanitize() auslösen → Markup()-Kennzeichnung
                         # geht verloren → t-out escaped statt rendert → <h1> wird &lt;h1&gt;
    )

    @api.depends("version_ids.version")
    def _compute_current_version(self):
        for doc in self:
            doc.current_version = max(doc.version_ids.mapped("version"), default=0)

    def _markdown_to_html(self, text):
        """Konvertiert Markdown-Text zu sicherem HTML-Markup."""
        if _mistune_available:
            return Markup(mistune.html(text))
        _logger.warning("mistune nicht installiert — Fallback auf Plaintext-Darstellung")
        return Markup("<pre>%s</pre>") % text

    @api.depends("content_md")
    def _compute_content_html(self):
        for doc in self:
            doc.content_html = self._markdown_to_html(doc.content_md) if doc.content_md else ""

    def _create_md_attachment(self, record, content, version_num):
        """Speichert Markdown-Text als .md-Datei (ir.attachment)."""
        encoded = base64.b64encode(content.encode("utf-8"))
        attachment = self.env["ir.attachment"].sudo().create({
            "name": f"{record.name}_v{version_num}.md",
            "datas": encoded,
            "mimetype": "text/markdown",
            "res_model": record._name,
            "res_id": record.id,
        })
        self._link_attachment_to_documents(attachment, encoded)
        return attachment

    def _create_pdf_attachment(self, record, version_num):
        """Rendert und speichert PDF-Report als Anhang. Gibt False zurück bei Fehler."""
        try:
            report = self.env.ref("markdown_editor.md_document_pdf", raise_if_not_found=False)
            if not report:
                return False
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
        except Exception as e:
            _logger.warning("PDF render failed for record %s v%s: %s", record.id, version_num, e)
            return False

    def _get_or_create_mdwriter_folder(self):
        """Gibt den MDWriter-Ordner in Documents zurück, legt ihn ggf. an."""
        try:
            Doc = self.env["documents.document"].sudo()
            folder = Doc.search([("name", "=", "MDWriter Dokumentation"), ("type", "=", "folder")], limit=1)
            return folder or Doc.create({"name": "MDWriter Dokumentation", "type": "folder"})
        except Exception as e:
            _logger.warning("MDWriter: Ordner konnte nicht angelegt werden: %s", e)
            return None

    def _link_attachment_to_documents(self, attachment, datas):
        """Legt das Attachment als documents.document im MDWriter-Ordner ab."""
        if "documents.document" not in self.env:
            return
        try:
            folder = self._get_or_create_mdwriter_folder()
            if not folder:
                return
            self.env["documents.document"].sudo().create({
                "name": attachment.name,
                "folder_id": folder.id,
                "datas": datas,
                "mimetype": attachment.mimetype,
                "type": "binary",
            })
        except Exception as e:
            _logger.warning("MDWriter: documents.document konnte nicht erstellt werden: %s", e)

    def _create_version(self):
        """Legt eine neue append-only Version an. Wird bei create/write ausgelöst."""
        # sudo() nötig: normale User dürfen keine Versions-Records direkt anlegen (ACL)
        Version = self.env["x.md.document.version"].sudo()
        for record in self:
            content = record.content_md or ""
            next_version = record.current_version + 1
            md_att = self._create_md_attachment(record, content, next_version)
            pdf_att = self._create_pdf_attachment(record, next_version)
            Version.create({
                "document_id": record.id,
                "version": next_version,
                "content_md": content,
                "checksum": hashlib.md5(content.encode("utf-8")).hexdigest(),
                "changed_by": self.env.user.id,
                "changed_at": fields.Datetime.now(),
                "md_attachment_id": md_att.id,
                "pdf_attachment_id": pdf_att.id if pdf_att else False,
            })

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_publish(self):
        self.write({"state": "published"})

    def action_archive_doc(self):
        self.write({"state": "archived"})

    def action_export_pdf(self):
        """Lädt das PDF der aktuellen Version herunter."""
        self.ensure_one()
        # version_ids ist desc sortiert → [:1] ist immer die aktuellste Version
        latest = self.version_ids[:1]
        if latest and latest.pdf_attachment_id:
            return {
                "type": "ir.actions.act_url",
                "url": f"/web/content/{latest.pdf_attachment_id.id}?download=true",
                "target": "new",
            }
        return self.env.ref("markdown_editor.md_document_pdf").report_action(self)

    def action_download_md(self):
        """Lädt die .md-Datei der aktuellen Version herunter."""
        self.ensure_one()
        latest = self.version_ids[:1]
        if not latest or not latest.md_attachment_id:
            return False
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{latest.md_attachment_id.id}?download=true",
            "target": "new",
        }

    def _get_report_html(self):
        """Gibt gerendertes HTML für den PDF-Report zurück.

        Direkter Aufruf aus dem QWeb-Template — umgeht den fields.Html ORM-Pfad,
        damit Markup() sicher als t-out-sicherer String ankommt.
        """
        self.ensure_one()
        return self._markdown_to_html(self.content_md) if self.content_md else Markup("")

    def action_open_diff(self):
        """Öffnet den Versionsdiff-Wizard."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "x.md.document.diff.wizard",
            "view_mode": "form",
            "target": "new",
            "res_id": False,  # Immer neuen Wizard anlegen (verhindert Odoo-seitiges Caching)
            "context": {"default_document_id": self.id},
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._create_version()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "content_md" in vals:
            self._create_version()
        return res


class XMdDocumentVersion(models.Model):
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
    changed_by = fields.Many2one(comodel_name="res.users", string="Geändert von")
    changed_at = fields.Datetime(string="Geändert am")
    md_attachment_id = fields.Many2one(comodel_name="ir.attachment", string="Markdown‑Anhang")
    pdf_attachment_id = fields.Many2one(comodel_name="ir.attachment", string="PDF‑Anhang")

    def action_restore(self):
        """Stellt diesen Versionsstand wieder her — erzeugt neue Version, löscht keine."""
        self.ensure_one()
        self.document_id.write({"content_md": self.content_md})
        return {
            "type": "ir.actions.act_window",
            "res_model": "x.md.document",
            "res_id": self.document_id.id,
            "view_mode": "form",
            "target": "current",
        }
