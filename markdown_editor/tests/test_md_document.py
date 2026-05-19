import hashlib
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError


class TestMdDocumentVersioning(TransactionCase):

    def setUp(self):
        super().setUp()
        self.doc = self.env["x.md.document"].create({
            "name": "Testdokument",
            "content_md": "# Hallo Welt",
        })

    def test_create_creates_first_version(self):
        # Beim Anlegen eines Dokuments muss automatisch Version 1 entstehen.
        self.assertEqual(len(self.doc.version_ids), 1)
        self.assertEqual(self.doc.current_version, 1)

    def test_write_creates_new_version(self):
        # Jede Inhaltsänderung muss eine neue Version erzeugen.
        self.doc.write({"content_md": "# Neue Version"})
        self.assertEqual(self.doc.current_version, 2)

    def test_restore_reverts_content(self):
        # Eine ältere Version muss wiederherstellbar sein (Restore-Funktion).
        self.doc.write({"content_md": "# Geändert"})
        v1 = self.doc.version_ids.filtered(lambda v: v.version == 1)
        v1.action_restore()
        self.assertEqual(self.doc.content_md, "# Hallo Welt")


class TestMdDocumentACL(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user_a = self._make_test_user("User A", "user_a_test@example.com")
        self.user_b = self._make_test_user("User B", "user_b_test@example.com")
        self.doc_a = self.env["x.md.document"].with_user(self.user_a).create({
            "name": "Dokument von A",
            "content_md": "Inhalt A",
        })

    def _make_test_user(self, name, login):
        # Odoo.sh: color_scheme in res_users_settings kann NOT NULL ohne DB-Default sein.
        # ALTER TABLE setzt den fehlenden Default, damit res.users.create() funktioniert.
        self.env.cr.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'res_users_settings'
              AND column_name = 'color_scheme'
              AND column_default IS NULL
        """)
        if self.env.cr.fetchone():
            self.env.cr.execute(
                "ALTER TABLE res_users_settings "
                "ALTER COLUMN color_scheme SET DEFAULT 'light'"
            )
        vals = {"name": name, "login": login}
        if "notification_type" in self.env["res.users"]._fields:
            vals["notification_type"] = "inbox"
        return self.env["res.users"].create(vals)

    def test_owner_can_read_own_document(self):
        # Eigentümer muss sein eigenes Dokument lesen können.
        doc = self.env["x.md.document"].with_user(self.user_a).browse(self.doc_a.id)
        self.assertEqual(doc.name, "Dokument von A")

    def test_other_user_cannot_read_document(self):
        # Record Rule: Fremder User darf das Dokument eines anderen nicht sehen.
        result = self.env["x.md.document"].with_user(self.user_b).search(
            [("id", "=", self.doc_a.id)]
        )
        self.assertFalse(result)

    def test_version_is_readonly_for_user(self):
        # ACL: Normaler User darf keine Versionen manuell anlegen (append-only).
        with self.assertRaises(AccessError):
            self.env["x.md.document.version"].with_user(self.user_a).create({
                "document_id": self.doc_a.id,
                "version": 99,
                "content_md": "Gefälschte Version",
            })


class TestMdDocumentDiff(TransactionCase):

    def setUp(self):
        super().setUp()
        doc = self.env["x.md.document"].create({
            "name": "Diff-Test",
            "content_md": "Zeile 1\nZeile 2\n",
        })
        doc.write({"content_md": "Zeile 1\nZeile 2 geändert\nZeile 3\n"})
        v1, v2 = sorted(doc.version_ids, key=lambda v: v.version)[:2]
        self.wizard = self.env["x.md.document.diff.wizard"].create({
            "document_id": doc.id,
            "version_from_id": v1.id,
            "version_to_id": v2.id,
        })

    def test_diff_shows_changes(self):
        # Diff-Wizard muss Hinzufügungen und Löschungen sichtbar machen.
        self.assertIn("o_md_diff_add", self.wizard.diff_html)
        self.assertIn("o_md_diff_del", self.wizard.diff_html)
