# =============================================================================
# md_document_diff.py – Versionsdiff-Wizard
# =============================================================================
# Ein "Wizard" in Odoo ist ein temporäres Formular (kein dauerhafter Datensatz).
# Dieser Wizard vergleicht zwei Versionen eines Markdown-Dokuments und zeigt
# die Unterschiede farbig an (grün = hinzugefügt, rot = gelöscht).
#
# Die Klasse erbt von models.TransientModel (statt models.Model):
# TransientModel = Datensätze werden nur kurz im Speicher gehalten und
# automatisch nach einer Weile wieder gelöscht. Perfekt für Dialoge.
# =============================================================================

import difflib          # Python-Standardbibliothek: erzeugt Diffs zwischen Texten
import html as html_mod # Python-Standardbibliothek: schützt Text vor HTML-Injection

from odoo import api, fields, models


class XMdDocumentDiffWizard(models.TransientModel):
    _name = "x.md.document.diff.wizard"
    _description = "Versionsdiff"

    # -------------------------------------------------------------------------
    # Felder
    # -------------------------------------------------------------------------

    document_id = fields.Many2one(
        comodel_name="x.md.document",
        string="Dokument",
        required=True,
    )
    # domain schränkt die Auswahl ein: Nur Versionen des gewählten Dokuments sind wählbar.
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
    # sanitize=False: Wir bauen das HTML selbst sicher zusammen (mit html.escape),
    # deshalb soll Odoo hier nicht nochmal sanitizen (das würde unsere CSS-Klassen entfernen).
    diff_html = fields.Html(
        string="Diff",
        compute="_compute_diff_html",
        sanitize=False,
    )

    # -------------------------------------------------------------------------
    # Diff-Berechnung
    # -------------------------------------------------------------------------

    @api.depends("version_from_id", "version_to_id")
    def _compute_diff_html(self):
        for rec in self:
            # Beide Versionen müssen ausgewählt sein, sonst nichts anzeigen.
            if not (rec.version_from_id and rec.version_to_id):
                rec.diff_html = ""
                continue

            # splitlines(keepends=True): Text in einzelne Zeilen aufteilen.
            # keepends=True behält das Zeilenende-Zeichen (\n) – difflib braucht das.
            a = (rec.version_from_id.content_md or "").splitlines(keepends=True)
            b = (rec.version_to_id.content_md or "").splitlines(keepends=True)
            v_from = rec.version_from_id.version
            v_to = rec.version_to_id.version

            # unified_diff erzeugt einen Standard-Diff im "unified"-Format
            # (wie man es vom Terminal kennt: +++ für neu, --- für alt, @@ für Position).
            # list() ist nötig, weil unified_diff einen Generator zurückgibt,
            # der nur einmal durchlaufen werden kann.
            diff_lines = list(difflib.unified_diff(
                a, b,
                fromfile=f"Version {v_from}",
                tofile=f"Version {v_to}",
                n=3,  # 3 Kontextzeilen um jede Änderung herum anzeigen
            ))

            if not diff_lines:
                rec.diff_html = "<p>Keine Unterschiede gefunden.</p>"
                continue

            # HTML zusammenbauen: Wir sammeln alle Teile in einer Liste (parts)
            # und verbinden sie am Ende mit join(). Das ist effizienter als
            # viele String-Konkatenationen mit "+".
            parts = ['<pre class="o_md_diff">']

            for line in diff_lines:
                # html.escape() schützt vor XSS: < wird zu &lt;, > zu &gt; usw.
                # Das ist wichtig, weil der Markdown-Inhalt vom User kommt.
                escaped = html_mod.escape(line)

                # Je nach Zeilenanfang die passende CSS-Klasse setzen.
                # Reihenfolge ist wichtig: +++ und --- müssen vor + und - geprüft werden,
                # weil "+".startswith("+") auch für "+++" wahr wäre.
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
            # "".join(parts) verbindet alle Listenelemente zu einem einzigen String.
            rec.diff_html = "".join(parts)
