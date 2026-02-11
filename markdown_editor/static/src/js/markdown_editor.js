/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * MarkdownField – OWL-basierter Split-View Editor mit Live-Vorschau.
 * Registriert als "markdown_editor" Widget fuer Text-Felder.
 */
class MarkdownField extends Component {
    setup() {
        this.state = useState({
            value: this.props.record.data[this.props.name] || "",
        });
    }

    _onInput(ev) {
        const value = ev.target.value;
        this.state.value = value;
        this.props.record.update({ [this.props.name]: value });
    }
}

MarkdownField.template = "markdown_editor.MarkdownField";
MarkdownField.props = { ...standardFieldProps };
MarkdownField.supportedTypes = ["text"];

registry.category("fields").add("markdown_editor", {
    component: MarkdownField,
    supportedTypes: ["text"],
});

export default MarkdownField;
