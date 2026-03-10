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
        sanitize=True,
    )

    @api.depends("version_ids.version")
    def _compute_current_version(self):
        for doc in self:
            doc.current_version = max(doc.version_ids.mapped("version"), default=0)

    @api.depends("content_md")
    def _compute_content_html(self):
        for doc in self:
            if not doc.content_md:
                doc.content_html = ""
                continue
            if _mistune_available:
                doc.content_html = Markup(mistune.html(doc.content_md))
            else:
                _logger.warning("mistune nicht installiert — PDF zeigt rohen Markdown-Text")
                doc.content_html = Markup("<pre>%s</pre>") % doc.content_md

    # ------------------------------------------------------------------ #
    # Versionierung                                                        #
    # ------------------------------------------------------------------ #

    def _create_md_attachment(self, record, content, version_num):
        return self.env["ir.attachment"].sudo().create({
            "name": f"{record.name}_v{version_num}.md",
            "datas": base64.b64encode(content.encode("utf-8")),
            "mimetype": "text/markdown",
            "res_model": record._name,
            "res_id": record.id,
        })

    def _create_pdf_attachment(self, record, version_num):
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
            _logger.warning("PDF render failed: %s", e)
            return False

    def _create_version(self):
        """Legt eine neue append-only Version an. Wird bei create/write ausgelöst."""
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

    # ------------------------------------------------------------------ #
    # Status-Aktionen                                                      #
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    # ORM-Hooks                                                            #
    # ------------------------------------------------------------------ #

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
        """Stellt diesen Versionsstand im Dokument wieder her (erzeugt neue Version)."""
        self.ensure_one()
        self.document_id.write({"content_md": self.content_md})
        return {
            "type": "ir.actions.act_window",
            "res_model": "x.md.document",
            "res_id": self.document_id.id,
            "view_mode": "form",
            "target": "current",
        }
