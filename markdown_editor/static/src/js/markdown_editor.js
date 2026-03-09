/** @odoo-module **/

/**
 * Erweitertes Markdown‑Editor‑Widget mit Live‑Vorschau und Syntax‑Highlighting.
 *
 * Verwendet markdown‑it für die HTML‑Vorschau und CodeMirror 5 für
 * Syntax‑Highlighting im Editor (Markdown‑Modus).
 * Beide Bibliotheken werden als UMD‑Bundle geladen und sind über
 * window.markdownit bzw. window.CodeMirror verfügbar.
 */

import { Component, useState, markup, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class MarkdownField extends Component {
    setup() {
        const initial = this.props.record.data[this.props.name] || "";

        // markdown‑it für Live‑Vorschau
        this.md = window.markdownit
            ? window.markdownit({ html: false, xhtmlOut: false, breaks: true, linkify: true })
            : null;

        this.state = useState({
            value: initial,
            html: this.md ? markup(this.md.render(initial)) : markup(initial),
        });

        this.editorRef = useRef("editor");
        this.cm = null;

        onMounted(() => {
            if (window.CodeMirror && this.editorRef.el) {
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
                this.cm.on("change", (cm) => {
                    const value = cm.getValue();
                    this.state.value = value;
                    this.state.html = this.md
                        ? markup(this.md.render(value))
                        : markup(value);
                    this.props.record.update({ [this.props.name]: value });
                });
            }
        });

        onWillUnmount(() => {
            if (this.cm) {
                this.cm.toTextArea();
                this.cm = null;
            }
        });
    }

    // Fallback‑Handler falls CodeMirror nicht geladen wurde
    _onInput(ev) {
        if (this.cm) return;
        const value = ev.target.value;
        this.state.value = value;
        this.state.html = this.md ? markup(this.md.render(value)) : markup(value);
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
