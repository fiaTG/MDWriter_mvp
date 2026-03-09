import difflib
import html as html_mod
from odoo import api, fields, models


class XMdDocumentDiffWizard(models.TransientModel):
    """
    Wizard zum Vergleich zweier Versionen eines Markdown‑Dokuments.
    Erzeugt einen Unified‑Diff als farbiges HTML (eine Spalte, lesbar
    in jedem Dialog). Zeileninhalt wird via html.escape() gesichert.
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
        sanitize=False,  # Inhalt wird manuell via html.escape() gesichert
    )

    @api.depends("version_from_id", "version_to_id")
    def _compute_diff_html(self):
        for rec in self:
            if not (rec.version_from_id and rec.version_to_id):
                rec.diff_html = ""
                continue

            a = (rec.version_from_id.content_md or "").splitlines(keepends=True)
            b = (rec.version_to_id.content_md or "").splitlines(keepends=True)
            v_from = rec.version_from_id.version
            v_to = rec.version_to_id.version

            diff_lines = list(difflib.unified_diff(
                a, b,
                fromfile=f"Version {v_from}",
                tofile=f"Version {v_to}",
                n=3,
            ))

            if not diff_lines:
                rec.diff_html = "<p>Keine Unterschiede gefunden.</p>"
                continue

            parts = ['<pre class="o_md_diff">']
            for line in diff_lines:
                escaped = html_mod.escape(line)
                if line.startswith("+++") or line.startswith("---"):
                    parts.append(f'<span class="o_md_diff_header">{escaped}</span>')
                elif line.startswith("+"):
                    parts.append(f'<span class="o_md_diff_add">{escaped}</span>')
                elif line.startswith("-"):
                    parts.append(f'<span class="o_md_diff_del">{escaped}</span>')
                elif line.startswith("@@"):
                    parts.append(f'<span class="o_md_diff_hunk">{escaped}</span>')
                else:
                    parts.append(f'<span>{escaped}</span>')
            parts.append("</pre>")
            rec.diff_html = "".join(parts)
