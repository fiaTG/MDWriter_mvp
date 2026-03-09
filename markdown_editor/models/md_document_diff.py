import difflib
from odoo import api, fields, models


class XMdDocumentDiffWizard(models.TransientModel):
    """
    Wizard zum Vergleich zweier Versionen eines Markdown‑Dokuments.
    Berechnet einen zeilenweisen HTML‑Diff via difflib.HtmlDiff.
    """

    _name = "x.md.document.diff.wizard"
    _description = "Versionsdiff"

    document_id = fields.Many2one(
        comodel_name="x.md.document",
        string="Dokument",
        required=True,
    )
    version_from_id = fields.Many2one(
        comodel_name="x.md.document.version",
        string="Von Version",
        domain="[('document_id', '=', document_id)]",
    )
    version_to_id = fields.Many2one(
        comodel_name="x.md.document.version",
        string="Bis Version",
        domain="[('document_id', '=', document_id)]",
    )
    diff_html = fields.Html(
        string="Diff",
        compute="_compute_diff_html",
        # sanitize=False: difflib.HtmlDiff escapt den Input bereits korrekt
        sanitize=False,
    )

    @api.depends("version_from_id", "version_to_id")
    def _compute_diff_html(self):
        for rec in self:
            if rec.version_from_id and rec.version_to_id:
                a = (rec.version_from_id.content_md or "").splitlines(keepends=True)
                b = (rec.version_to_id.content_md or "").splitlines(keepends=True)
                differ = difflib.HtmlDiff(wrapcolumn=80)
                rec.diff_html = differ.make_table(
                    a,
                    b,
                    fromdesc=f"Version {rec.version_from_id.version}",
                    todesc=f"Version {rec.version_to_id.version}",
                    context=True,
                    numlines=3,
                )
            else:
                rec.diff_html = ""
