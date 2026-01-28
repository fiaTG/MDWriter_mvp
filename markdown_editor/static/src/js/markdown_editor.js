/** @odoo-module alias=markdown_editor.MarkdownField **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

/**
 * MarkdownField ist ein einfacher OWL‑basierter Form‑Widget, der
 * einen Split‑View Editor mit Live‑Vorschau darstellt.
 */
class MarkdownField extends Component {
    setup() {
        this.state = useState({
            value: this.props.record.data[this.props.name] || "",
        });

        // Debug-Output für Entwicklung
        console.log("MarkdownField mounted", {
            name: this.props.name,
            value: this.state.value,
            readonly: this.props.readonly
        });
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
MarkdownField.props = {
    record: Object,
    name: String,
    readonly: { type: Boolean, optional: true },
    id: { type: [String, Number], optional: true },
};
MarkdownField.displayName = "Markdown Editor";

// Füge eine CSS-Klasse hinzu, damit das Widget die volle Breite bekommt
MarkdownField.extractProps = ({ attrs }) => {
    return {
        readonly: attrs.readonly,
        id: attrs.id,
    };
};

// Widget im Field Registry registrieren
registry.category("fields").add("markdown_editor", {
    component: MarkdownField,
});

export default MarkdownField;