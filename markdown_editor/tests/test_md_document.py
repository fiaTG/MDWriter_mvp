import hashlib
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError


class TestMdDocumentVersioning(TransactionCase):
    """Tests für Versionierungslogik von x.md.document."""

    def setUp(self):
        super().setUp()
        self.doc = self.env["x.md.document"].create({
            "name": "Testdokument",
            "content_md": "# Hallo Welt",
        })

    def test_create_creates_first_version(self):
        """Beim Erstellen eines Dokuments wird automatisch Version 1 angelegt."""
        self.assertEqual(len(self.doc.version_ids), 1)
        self.assertEqual(self.doc.version_ids[0].version, 1)
        self.assertEqual(self.doc.current_version, 1)

    def test_write_creates_new_version(self):
        """Jede Änderung von content_md erzeugt eine neue Version."""
        self.doc.write({"content_md": "# Neue Version"})
        self.assertEqual(len(self.doc.version_ids), 2)
        self.assertEqual(self.doc.current_version, 2)

    def test_write_without_content_change_no_new_version(self):
        """Änderung anderer Felder erzeugt keine neue Version."""
        self.doc.write({"name": "Neuer Titel"})
        self.assertEqual(len(self.doc.version_ids), 1)

    def test_version_content_matches_document(self):
        """Versionierter Inhalt stimmt mit dem gespeicherten Inhalt überein."""
        version = self.doc.version_ids[0]
        self.assertEqual(version.content_md, "# Hallo Welt")

    def test_checksum_is_md5(self):
        """Checksum ist der MD5-Hash des Markdown-Inhalts."""
        expected = hashlib.md5("# Hallo Welt".encode("utf-8")).hexdigest()
        self.assertEqual(self.doc.version_ids[0].checksum, expected)

    def test_version_changed_by_is_current_user(self):
        """changed_by zeigt auf den aktuellen User."""
        self.assertEqual(
            self.doc.version_ids[0].changed_by,
            self.env.user,
        )

    def test_restore_reverts_content(self):
        """action_restore() setzt den Inhalt auf den Stand der ausgewählten Version zurück."""
        self.doc.write({"content_md": "# Geändert"})
        v1 = self.doc.version_ids.filtered(lambda v: v.version == 1)
        v1.action_restore()
        self.assertEqual(self.doc.content_md, "# Hallo Welt")

    def test_restore_creates_new_version(self):
        """action_restore() legt eine neue Version an (Restore ist auditierbar)."""
        self.doc.write({"content_md": "# Geändert"})
        count_before = len(self.doc.version_ids)
        v1 = self.doc.version_ids.filtered(lambda v: v.version == 1)
        v1.action_restore()
        self.assertEqual(len(self.doc.version_ids), count_before + 1)

    def test_multiple_writes_increment_version(self):
        """Drei Schreibvorgänge ergeben vier Versionen (inkl. create)."""
        self.doc.write({"content_md": "v2"})
        self.doc.write({"content_md": "v3"})
        self.doc.write({"content_md": "v4"})
        self.assertEqual(self.doc.current_version, 4)


class TestMdDocumentACL(TransactionCase):
    """Tests für ACL und Record Rules."""

    def setUp(self):
        super().setUp()
        self.user_a = self.env["res.users"].create({
            "name": "User A",
            "login": "user_a_test@example.com",
            "groups_id": [(4, self.env.ref("base.group_user").id)],
        })
        self.user_b = self.env["res.users"].create({
            "name": "User B",
            "login": "user_b_test@example.com",
            "groups_id": [(4, self.env.ref("base.group_user").id)],
        })
        # Dokument als User A anlegen
        self.doc_a = self.env["x.md.document"].with_user(self.user_a).create({
            "name": "Dokument von A",
            "content_md": "Inhalt A",
        })

    def test_owner_can_read_own_document(self):
        """Eigentümer kann sein eigenes Dokument lesen."""
        doc = self.env["x.md.document"].with_user(self.user_a).browse(self.doc_a.id)
        self.assertEqual(doc.name, "Dokument von A")

    def test_other_user_cannot_read_document(self):
        """Anderer User kann fremdes Dokument nicht lesen (Record Rule)."""
        with self.assertRaises(AccessError):
            self.env["x.md.document"].with_user(self.user_b).browse(
                self.doc_a.id
            ).name  # Zugriff erzwingen

    def test_version_is_readonly_for_user(self):
        """Normale User können keine Versions-Records direkt anlegen."""
        version = self.doc_a.version_ids[0]
        with self.assertRaises(AccessError):
            self.env["x.md.document.version"].with_user(self.user_a).create({
                "document_id": self.doc_a.id,
                "version": 99,
                "content_md": "Gefälschte Version",
            })


class TestMdDocumentDiff(TransactionCase):
    """Tests für den Diff-Wizard."""

    def setUp(self):
        super().setUp()
        self.doc = self.env["x.md.document"].create({
            "name": "Diff-Test",
            "content_md": "Zeile 1\nZeile 2\n",
        })
        self.doc.write({"content_md": "Zeile 1\nZeile 2 geändert\nZeile 3\n"})

    def test_diff_html_contains_additions(self):
        """Diff-HTML enthält hinzugefügte Zeilen."""
        v1, v2 = sorted(self.doc.version_ids, key=lambda v: v.version)[:2]
        wizard = self.env["x.md.document.diff.wizard"].create({
            "document_id": self.doc.id,
            "version_from_id": v1.id,
            "version_to_id": v2.id,
        })
        self.assertIn("o_md_diff_add", wizard.diff_html)

    def test_diff_html_contains_deletions(self):
        """Diff-HTML enthält gelöschte Zeilen."""
        v1, v2 = sorted(self.doc.version_ids, key=lambda v: v.version)[:2]
        wizard = self.env["x.md.document.diff.wizard"].create({
            "document_id": self.doc.id,
            "version_from_id": v1.id,
            "version_to_id": v2.id,
        })
        self.assertIn("o_md_diff_del", wizard.diff_html)

    def test_diff_no_changes_message(self):
        """Identische Versionen ergeben die Meldung 'Keine Unterschiede'."""
        v1 = self.doc.version_ids.filtered(lambda v: v.version == 1)
        wizard = self.env["x.md.document.diff.wizard"].create({
            "document_id": self.doc.id,
            "version_from_id": v1.id,
            "version_to_id": v1.id,
        })
        self.assertIn("Keine Unterschiede", wizard.diff_html)
