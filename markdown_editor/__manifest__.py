{
    "name": "Markdown Editor",
    "summary": "Markdown‑basierter Editor mit Live‑Vorschau und Versionierung",
    "version": "19.0.1.0.0",
    "author": "Timo",
    "maintainers": ["Timo"],
    "website": "https://github.com/fiaTG/MDWriter",
    "license": "LGPL-3",
    "category": "Productivity",
    "depends": [
        "base",
        "web",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/markdown_editor_security.xml",
        "views/md_document_views.xml",
        "report/md_document_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "markdown_editor/static/src/js/markdown_editor.js",
            "markdown_editor/static/src/xml/markdown_editor_templates.xml",
            "markdown_editor/static/src/scss/markdown_editor.scss",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}