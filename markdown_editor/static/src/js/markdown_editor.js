/** @odoo-module **/
import { Component, useState, useRef } from "@odoo/owl";
import { fieldRegistry } from "@web/views/fields/field_registry";

/**
 * MarkdownField ist ein einfacher OWL‑basierter Form‑Widget, der
 * einen Split‑View Editor mit Live‑Vorschau darstellt. Die
 * eigentliche Markdown‑Konvertierung wird hier nicht durchgeführt,
 * stattdessen wird der Inhalt 1:1 in der Vorschau angezeigt.
 * Eine Erweiterung um eine echte Markdown‑Parser‑Bibliothek ist
 * möglich, indem beispielsweise marked.js eingebunden wird.
 */
class MarkdownField extends Component {
    setup() {
        this.state = useState({
            value: this.props.record.data[this.props.name] || "",
        });
        this.editorRef = useRef("editor");
    }

    /**
     * Aktualisiert den Zustand beim Tippen im Textarea und schreibt
     * den neuen Wert ins Record.
     */
    _onInput(ev) {
        const value = ev.target.value;
        this.state.value = value;
        this.props.record.update({ [this.props.name]: value });
    }
}

MarkdownField.template = "markdown_editor.MarkdownField";

// Widget im Registry registrieren
fieldRegistry.add("markdown_editor", MarkdownField);

export default MarkdownField;