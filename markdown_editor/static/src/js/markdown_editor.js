/** @odoo-module **/

/**
 * Erweitertes Markdown‑Editor‑Widget mit Live‑Vorschau.
 *
 * Diese Version verwendet die Bibliothek "markdown-it" zur
 * Konvertierung des eingegebenen Markdown‑Texts in HTML. In der
 * Vorschau wird das gerenderte HTML angezeigt, sodass der rechte
 * Bereich nicht mehr den rohen Markdown‑Text enthält.
 */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// Importieren Sie die Markdown‑Bibliothek. Beachten Sie, dass
// "markdown-it" als Abhängigkeit in die Assets aufgenommen werden muss.
// Wir verwenden hier keine ES‑Modul‑Importe, weil das ausgelieferte
// UMD‑Bundle von "markdown-it" keinen AMD/ESM‑Namen definiert. Stattdessen
// greift Odoo auf eine globale Variable namens `markdownit` zu, die beim
// Laden von markdown‑it.min.js gesetzt wird. Daher laden wir das Skript
// einfach als Asset und greifen dann auf `window.markdownit` zu.

class MarkdownField extends Component {
    /**
     * Initialisiert den State und den Markdown‑Parser.
     *
     * Es werden zwei State‑Eigenschaften verwaltet:
     *  - value: der aktuelle Markdown‑Text
     *  - html: die gerenderte HTML‑Version des Textes
     */
    setup() {
        // Initialwert aus dem Datensatz lesen
        const initial = this.props.record.data[this.props.name] || "";
        // Instanz des Markdown‑Parsers erzeugen. Wenn die Bibliothek
        // korrekt geladen wurde, steht `window.markdownit` zur
        // Verfügung. Andernfalls bleibt der Parser null, und die
        // Vorschau zeigt den rohen Markdown‑Text.
        this.md = window.markdownit ? window.markdownit() : null;
        // State mit Text und gerendertem HTML initialisieren.
        this.state = useState({
            value: initial,
            html: this.md ? this.md.render(initial) : initial,
        });
    }

    /**
     * Handler fuer Eingaben im Textfeld.
     *
     * Aktualisiert sowohl den Markdown‑Text als auch die HTML‑Vorschau
     * und schreibt den neuen Wert in das aktuelle Record.
     *
     * @param {InputEvent} ev Das Input‑Event des Textfeldes
     */
    _onInput(ev) {
        const value = ev.target.value;
        // Markdown‑Text aktualisieren
        this.state.value = value;
        // HTML‑Vorschau aktualisieren
        this.state.html = this.md ? this.md.render(value) : value;
        // Wert im Record speichern
        this.props.record.update({ [this.props.name]: value });
    }
}

// Zuweisen der QWeb‑Vorlage
MarkdownField.template = "markdown_editor.MarkdownField";
// Standard‑Props uebernehmen
MarkdownField.props = { ...standardFieldProps };
// Unterstuetzte Feldtypen
MarkdownField.supportedTypes = ["text"];

// Registrierung des Widgets in der Registry
registry.category("fields").add("markdown_editor", {
    component: MarkdownField,
    supportedTypes: ["text"],
});

export default MarkdownField;