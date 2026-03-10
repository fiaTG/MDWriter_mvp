# =============================================================================
# test_md_document.py – Automatisierte Tests für MDWriter
# =============================================================================
# Tests prüfen automatisch, ob der Code korrekt funktioniert.
# In Odoo basieren Tests auf TransactionCase: Jeder Test läuft in einer
# Datenbank-Transaktion, die am Ende automatisch zurückgerollt wird.
# Das bedeutet: Tests beeinflussen sich nicht gegenseitig und die echte
# Datenbank bleibt sauber.
#
# Ausführen: ./odoo-bin test -m markdown_editor -d <datenbankname>
# =============================================================================

import hashlib
# TransactionCase: Basisklasse für Odoo-Tests mit echten Datenbankzugriffen.
from odoo.tests.common import TransactionCase
# AccessError: Odoo wirft diesen Fehler, wenn ein User keine Berechtigung hat.
from odoo.exceptions import AccessError


# =============================================================================
# TestMdDocumentVersioning – Tests für die Versionierungslogik
# =============================================================================
class TestMdDocumentVersioning(TransactionCase):

    def setUp(self):
        """Vorbereitung: Wird vor JEDEM einzelnen Test ausgeführt.

        super().setUp() startet die Datenbank-Transaktion (muss immer aufgerufen werden).
        Dann legen wir ein Testdokument an, das alle Tests in dieser Klasse verwenden.
        self.doc macht das Dokument als Instanzvariable für alle Testmethoden verfügbar.
        """
        super().setUp()
        self.doc = self.env["x.md.document"].create({
            "name": "Testdokument",
            "content_md": "# Hallo Welt",
        })

    def test_create_creates_first_version(self):
        # self.assertEqual(a, b) schlägt fehl, wenn a != b
        self.assertEqual(len(self.doc.version_ids), 1)
        self.assertEqual(self.doc.version_ids[0].version, 1)
        self.assertEqual(self.doc.current_version, 1)

    def test_write_creates_new_version(self):
        self.doc.write({"content_md": "# Neue Version"})
        self.assertEqual(len(self.doc.version_ids), 2)
        self.assertEqual(self.doc.current_version, 2)

    def test_write_without_content_change_no_new_version(self):
        # Änderung eines anderen Feldes (name) darf keine neue Version erzeugen
        self.doc.write({"name": "Neuer Titel"})
        self.assertEqual(len(self.doc.version_ids), 1)

    def test_version_content_matches_document(self):
        self.assertEqual(self.doc.version_ids[0].content_md, "# Hallo Welt")

    def test_checksum_is_md5(self):
        # Wir berechnen die erwartete MD5-Prüfsumme selbst und vergleichen sie mit der gespeicherten.
        expected = hashlib.md5("# Hallo Welt".encode("utf-8")).hexdigest()
        self.assertEqual(self.doc.version_ids[0].checksum, expected)

    def test_version_changed_by_is_current_user(self):
        # self.env.user ist der aktuell angemeldete User (in Tests: Administrator)
        self.assertEqual(self.doc.version_ids[0].changed_by, self.env.user)

    def test_restore_reverts_content(self):
        self.doc.write({"content_md": "# Geändert"})
        # .filtered() gibt nur die Versionen zurück, bei denen die Bedingung wahr ist.
        # lambda v: v.version == 1 ist eine Mini-Funktion: "gib True zurück, wenn version == 1"
        v1 = self.doc.version_ids.filtered(lambda v: v.version == 1)
        v1.action_restore()
        self.assertEqual(self.doc.content_md, "# Hallo Welt")

    def test_restore_creates_new_version(self):
        # Restore muss eine neue Version erzeugen (Auditierbarkeit)
        self.doc.write({"content_md": "# Geändert"})
        count_before = len(self.doc.version_ids)
        v1 = self.doc.version_ids.filtered(lambda v: v.version == 1)
        v1.action_restore()
        self.assertEqual(len(self.doc.version_ids), count_before + 1)

    def test_multiple_writes_increment_version(self):
        self.doc.write({"content_md": "v2"})
        self.doc.write({"content_md": "v3"})
        self.doc.write({"content_md": "v4"})
        self.assertEqual(self.doc.current_version, 4)


# =============================================================================
# TestMdDocumentACL – Tests für Zugriffskontrolle (Access Control)
# =============================================================================
class TestMdDocumentACL(TransactionCase):

    def setUp(self):
        super().setUp()
        # Zwei Testbenutzer anlegen, um die Zugriffsregeln zu prüfen.
        # with_user(user) führt alle Operationen als dieser User aus.
        self.user_a = self.env["res.users"].create({
            "name": "User A",
            "login": "user_a_test@example.com",
        })
        self.user_b = self.env["res.users"].create({
            "name": "User B",
            "login": "user_b_test@example.com",
        })
        # Dokument als User A anlegen → User A ist damit der Eigentümer
        self.doc_a = self.env["x.md.document"].with_user(self.user_a).create({
            "name": "Dokument von A",
            "content_md": "Inhalt A",
        })

    def test_owner_can_read_own_document(self):
        doc = self.env["x.md.document"].with_user(self.user_a).browse(self.doc_a.id)
        self.assertEqual(doc.name, "Dokument von A")

    def test_other_user_cannot_read_document(self):
        # Die Record Rule erlaubt User B nicht, das Dokument von User A zu sehen.
        # search() gibt einen leeren Datensatz zurück (statt eine Exception zu werfen).
        result = self.env["x.md.document"].with_user(self.user_b).search(
            [("id", "=", self.doc_a.id)]
        )
        # self.assertFalse() schlägt fehl, wenn result nicht leer ist
        self.assertFalse(result)

    def test_version_is_readonly_for_user(self):
        # with self.assertRaises(AccessError): prüft, ob innerhalb des Blocks
        # eine AccessError-Exception geworfen wird. Falls nicht → Test schlägt fehl.
        with self.assertRaises(AccessError):
            self.env["x.md.document.version"].with_user(self.user_a).create({
                "document_id": self.doc_a.id,
                "version": 99,
                "content_md": "Gefälschte Version",
            })


# =============================================================================
# TestMdDocumentDiff – Tests für den Versions-Diff-Wizard
# =============================================================================
class TestMdDocumentDiff(TransactionCase):

    def setUp(self):
        super().setUp()
        # Dokument mit zwei verschiedenen Versionen anlegen
        self.doc = self.env["x.md.document"].create({
            "name": "Diff-Test",
            "content_md": "Zeile 1\nZeile 2\n",
        })
        self.doc.write({"content_md": "Zeile 1\nZeile 2 geändert\nZeile 3\n"})

        # Versionen aufsteigend sortieren (v1 = alt, v2 = neu)
        # sorted() gibt eine sortierte Liste zurück; [:2] nimmt nur die ersten zwei Elemente.
        v1, v2 = sorted(self.doc.version_ids, key=lambda v: v.version)[:2]

        # Wizard-Datensatz erstellen (TransientModel: wird nur kurz gehalten)
        self.wizard = self.env["x.md.document.diff.wizard"].create({
            "document_id": self.doc.id,
            "version_from_id": v1.id,
            "version_to_id": v2.id,
        })

    def test_diff_html_contains_additions(self):
        # assertIn(a, b) schlägt fehl, wenn a nicht in b enthalten ist
        self.assertIn("o_md_diff_add", self.wizard.diff_html)

    def test_diff_html_contains_deletions(self):
        self.assertIn("o_md_diff_del", self.wizard.diff_html)

    def test_diff_no_changes_message(self):
        # Gleiche Version von und bis → kein Unterschied
        v1 = self.doc.version_ids.filtered(lambda v: v.version == 1)
        wizard = self.env["x.md.document.diff.wizard"].create({
            "document_id": self.doc.id,
            "version_from_id": v1.id,
            "version_to_id": v1.id,
        })
        self.assertIn("Keine Unterschiede", wizard.diff_html)
