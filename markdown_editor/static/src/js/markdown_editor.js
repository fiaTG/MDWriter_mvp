/** @odoo-module **/

import { Component, useState, markup, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class MarkdownField extends Component {
    setup() {
        const initial = this.props.record.data[this.props.name] || "";

        this.md = window.markdownit
            ? window.markdownit({ html: false, breaks: true, linkify: true })
            : null;

        this.state = useState({
            value: initial,
            html: this._render(initial),
        });

        this.editorRef = useRef("editor");
        this.cm = null;

        onMounted(() => {
            if (!window.CodeMirror || !this.editorRef.el) return;
            this.cm = window.CodeMirror.fromTextArea(this.editorRef.el, {
                mode: "markdown",
                lineWrapping: true,
                lineNumbers: false,
                theme: "default",
                readOnly: this.props.readonly ? "nocursor" : false,
                autofocus: false,
                extraKeys: { Tab: false },
            });
            this.cm.setValue(this.state.value);
            this.cm.on("change", (cm) => this._updateState(cm.getValue()));
        });

        onWillUnmount(() => {
            if (this.cm) {
                this.cm.toTextArea();
                this.cm = null;
            }
        });
    }

    _render(value) {
        return this.md ? markup(this.md.render(value)) : markup(value);
    }

    _updateState(value) {
        this.state.value = value;
        this.state.html = this._render(value);
        this.props.record.update({ [this.props.name]: value });
    }

    // Fallback wenn CodeMirror nicht geladen wurde
    _onInput(ev) {
        if (!this.cm) this._updateState(ev.target.value);
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
