/** @odoo-module **/

/**
 * markdown_editor.js – OWL-Komponente für den Split-View Markdown-Editor
 *
 * Diese Datei registriert ein eigenes Odoo-Feld-Widget ("markdown_editor").
 * Es besteht aus zwei Hälften nebeneinander:
 *   Links:  CodeMirror – ein Texteditor mit Syntax-Highlighting für Markdown
 *   Rechts: Live-Vorschau – der Markdown-Text wird in Echtzeit als HTML gerendert
 *
 * OWL (Odoo Web Library) ist das JavaScript-Framework von Odoo für UI-Komponenten.
 * Es funktioniert ähnlich wie React: Komponenten haben einen State (Zustand),
 * und die Oberfläche aktualisiert sich automatisch, wenn sich der State ändert.
 */

// Imports aus dem OWL-Framework:
// - Component:      Basisklasse für alle OWL-Komponenten (wie models.Model in Python)
// - useState:       Erstellt reaktiven State – Änderungen lösen automatisch UI-Updates aus
// - markup:         Markiert einen String als "sicheres HTML" (verhindert doppeltes Escaping)
// - useRef:         Gibt Zugriff auf ein echtes DOM-Element (z.B. die Textarea)
// - onMounted:      Callback, der ausgeführt wird, nachdem die Komponente in die Seite eingefügt wurde
// - onWillUnmount:  Callback, der ausgeführt wird, bevor die Komponente aus der Seite entfernt wird
import { Component, useState, markup, useRef, onMounted, onWillUnmount } from "@odoo/owl";

// registry: Odoos zentrales Verzeichnis – hier melden wir unser Widget an.
import { registry } from "@web/core/registry";

// standardFieldProps: Standardmäßige Props (Eigenschaften), die jedes Odoo-Feld-Widget bekommt.
// Props sind Eingabewerte, die eine Komponente von außen erhält (wie Parameter einer Funktion).
import { standardFieldProps } from "@web/views/fields/standard_field_props";


// MarkdownField ist unsere Komponente – eine Klasse, die Component erweitert (erbt).
class MarkdownField extends Component {

    // setup() ist die Initialisierungsmethode in OWL.
    // Sie wird einmal aufgerufen, wenn die Komponente erstellt wird.
    // Hier richtet man State, Refs und Lifecycle-Callbacks ein.
    setup() {
        // Den aktuellen Feldwert aus dem Odoo-Datensatz lesen.
        // this.props.record ist der Odoo-Datensatz, this.props.name der Feldname.
        // || "" bedeutet: Wenn der Wert leer/null ist, leeren String verwenden.
        const initial = this.props.record.data[this.props.name] || "";

        // markdown-it wird als globale Variable (window.markdownit) geladen.
        // Optionen:
        //   html: false   → Eingebettetes HTML im Markdown wird nicht gerendert (XSS-Schutz)
        //   breaks: true  → Einzelne Zeilenumbrüche erzeugen <br>
        //   linkify: true → URLs werden automatisch zu Links
        this.md = window.markdownit
            ? window.markdownit({ html: false, breaks: true, linkify: true })
            : null;  // Falls die Bibliothek nicht geladen wurde, null

        // useState erstellt reaktiven State: Wenn sich state.value oder state.html ändert,
        // rendert OWL die Komponente automatisch neu.
        this.state = useState({
            value: initial,           // Der Markdown-Rohtext (für den Editor)
            html: this._render(initial), // Das gerenderte HTML (für die Vorschau)
        });

        // useRef gibt uns Zugriff auf das <textarea>-Element im Template.
        // CodeMirror braucht dieses Element, um sich darauf zu mounten.
        this.editorRef = useRef("editor");
        this.cm = null;           // Hier speichern wir die CodeMirror-Instanz (zunächst null)
        this._debounce = null;    // Timer-ID für Debouncing (verhindert zu häufiges Rendern)

        // onMounted: Dieser Code läuft, nachdem das HTML der Komponente in die Seite eingefügt wurde.
        // Erst dann existiert das <textarea>-Element im DOM, auf das CodeMirror zugreift.
        onMounted(() => {
            // Guard-Clause: Wenn CodeMirror nicht verfügbar ist oder das Element fehlt, abbrechen.
            if (!window.CodeMirror || !this.editorRef.el) return;

            // CodeMirror "übernimmt" die Textarea: Es versteckt sie und zeigt seinen eigenen Editor.
            this.cm = window.CodeMirror.fromTextArea(this.editorRef.el, {
                mode: "markdown",         // Syntax-Highlighting für Markdown aktivieren
                lineWrapping: true,       // Lange Zeilen umbrechen statt horizontal scrollen
                lineNumbers: false,       // Keine Zeilennummern anzeigen
                theme: "default",         // Standard-CodeMirror-Theme
                readOnly: this.props.readonly ? "nocursor" : false, // Readonly-Modus wenn nötig
                autofocus: false,
                extraKeys: { Tab: false }, // Tab-Taste nicht von CodeMirror abfangen
            });

            // Initialwert in CodeMirror setzen
            this.cm.setValue(this.state.value);

            // Event-Listener: Bei Texteingabe State aktualisieren – mit Debounce (300ms).
            // Debounce bedeutet: Erst wenn der User 300ms lang nicht tippt, wird die Preview neu
            // gerendert. Ohne Debounce würde markdown-it bei jedem einzelnen Tastendruck
            // den gesamten Text neu parsen – bei großen Dokumenten spürbar langsam.
            // clearTimeout() verwirft den vorherigen Timer, setTimeout() startet einen neuen.
            this.cm.on("change", (cm) => {
                clearTimeout(this._debounce);
                this._debounce = setTimeout(() => this._updateState(cm.getValue()), 300);
            });
        });

        // onWillUnmount: Aufräumen, bevor die Komponente entfernt wird.
        // toTextArea() macht CodeMirror rückgängig und stellt die originale Textarea wieder her.
        onWillUnmount(() => {
            // Debounce-Timer abbrechen, damit kein Update mehr nach dem Unmount feuert.
            clearTimeout(this._debounce);
            if (this.cm) {
                this.cm.toTextArea();
                this.cm = null;
            }
        });
    }

    /**
     * Rendert Markdown-Text zu sicherem HTML.
     * Gibt markup() zurück, damit OWL's t-out den HTML-String wirklich rendert
     * und ihn nicht als Text anzeigt.
     */
    _render(value) {
        // Ternärer Ausdruck: "this.md ? A : B" bedeutet "wenn this.md vorhanden, dann A, sonst B"
        return this.md ? markup(this.md.render(value)) : markup(value);
    }

    /**
     * Aktualisiert den State und speichert den Wert im Odoo-Datensatz.
     * Diese Methode wird bei jeder Texteingabe aufgerufen.
     */
    _updateState(value) {
        this.state.value = value;
        this.state.html = this._render(value);
        // props.record.update() speichert den neuen Wert im Odoo-Datensatz (im Speicher).
        // Der Datensatz wird erst beim Klick auf "Speichern" wirklich in der Datenbank gespeichert.
        this.props.record.update({ [this.props.name]: value });
    }

    /**
     * Fallback-Handler für die rohe Textarea (wenn CodeMirror nicht geladen wurde).
     * Normalerweise übernimmt CodeMirror die Eingabe – nur wenn es fehlt, greift dieser Handler.
     */
    _onInput(ev) {
        // Nur handeln wenn kein CodeMirror aktiv ist
        if (!this.cm) this._updateState(ev.target.value);
    }
}

// Das Template (HTML-Struktur) für diese Komponente – definiert in markdown_editor_templates.xml
MarkdownField.template = "markdown_editor.MarkdownField";

// Props-Definition: Dieses Widget akzeptiert alle Standard-Odoo-Feld-Props.
// Der Spread-Operator "..." kopiert alle Eigenschaften von standardFieldProps.
MarkdownField.props = { ...standardFieldProps };

// Dieses Widget kann nur auf Text-Feldern verwendet werden (content_md ist ein Text-Feld).
MarkdownField.supportedTypes = ["text"];

// Widget in Odoos zentralem Verzeichnis anmelden.
// Nach dieser Zeile kann man in XML-Views widget="markdown_editor" schreiben.
registry.category("fields").add("markdown_editor", {
    component: MarkdownField,
    supportedTypes: ["text"],
});

export default MarkdownField;
