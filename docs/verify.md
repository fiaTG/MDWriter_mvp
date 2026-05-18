# Überschrift H1 — Trendtec Grün, Border-Bottom

## Überschrift H2

### Überschrift H3

#### Überschrift H4

---

## Fließtext & Inline-Elemente

Normaler Fließtext mit **fettem Text**, *kursivem Text* und ~~durchgestrichenem Text~~.

Inline-Code: `const x = 42;` soll grünen Hintergrund (`--tt-primary-dim`) und dunkle Schrift haben.

Ein [Link zum Testen](https://example.com) soll dunkelgrün sein und beim Hover heller werden.

---

## Code-Block

```javascript
// Kommentar — sollte grau sein
const greeting = "Hallo Welt";   // String — grün
const count = 42;                 // Zahl
function hello(name) {            // Funktionsname
    return `Hallo, ${name}!`;
}
```

```python
# Python Beispiel
def berechne(x, y):
    """Docstring"""
    ergebnis = x + y
    return ergebnis

wert = berechne(10, 20)
print(wert)
```

---

## Blockquote

> Das ist ein Blockquote. Er soll eine grüne linke Borderlinie haben und leicht kursiv sowie transparent wirken.
>
> Mehrzeiliger Blockquote mit zweitem Absatz.

---

## Tabelle

| Spalte A       | Spalte B     | Spalte C   |
|----------------|--------------|------------|
| Zelle 1        | Zelle 2      | Zelle 3    |
| Trendtec       | MDWriter     | Odoo 19    |
| Hover-Zeile    | Grüner Bg    | bei Hover  |

Der Tabellenkopf soll Trendtec-Grün (`--tt-primary`) als Hintergrund haben.

---

## Listen

**Ungeordnete Liste:**
- Erster Eintrag
- Zweiter Eintrag
  - Eingerückt
  - Noch eingerückt
- Dritter Eintrag

**Geordnete Liste:**
1. Erster Schritt
2. Zweiter Schritt
3. Dritter Schritt

---

## Horizontale Linie

Über der Linie.

---

Unter der Linie. Die `<hr>` soll Trendtec-Grün, dünn und leicht transparent sein.

---

## Kombiniert

> **Fetter Text in einem Blockquote** mit `inline code` und einem [Link](https://example.com).

Tabelle mit Code:

| Element     | Token            | Farbe               |
|-------------|------------------|---------------------|
| Überschrift | `--tt-cm-header` | `var(--tt-primary)` |
| Link        | `--tt-cm-link`   | `var(--tt-primary-dark)` |
| Blockquote  | `--tt-cm-quote`  | `#6a9a4a`           |

---

## Plugin-Tests (feat/markdown-plugins Branch)

---

### Typographer

Smartquotes: "doppelte Anführungszeichen" und 'einfache Anführungszeichen'

Sonderzeichen: (c) (C) (r) (R) (tm) (TM)

Gedankenstriche: Kurz -- lang --- sehr lang

Ellipsis: test...

---

### Emoji (markdown-it-emoji)

Klassisch: :smile: :wink: :cry: :laughing: :heart: :thumbsup:

Shortcuts: :-) :-( 8-) ;) :D

---

### Superscript & Subscript (markdown-it-sup / markdown-it-sub)

Superscript: 2^10^ = 1024, E = mc^2^, 19^th^ century

Subscript: H~2~O, CO~2~, x~i~ + y~j~

---

### Inserted & Marked (markdown-it-ins / markdown-it-mark)

Eingefügter Text: ++dieser Text wurde eingefügt++

Hervorgehobener Text: ==dieser Text ist markiert==

Kombiniert: ++eingefügt++ und ==markiert== und ~~gelöscht~~

---

### Footnotes (markdown-it-footnote)

Erster Satz mit Fußnote.[^fn1]

Zweiter Satz mit weiterer Fußnote.[^fn2]

Inline-Fußnote^[Das ist eine Inline-Fußnote direkt im Text.] ohne separaten Eintrag.

[^fn1]: Das ist die erste Fußnote. Sie kann **Markdown** enthalten.
[^fn2]: Das ist die zweite Fußnote mit einem [Link](https://example.com).

---

### Definition List (markdown-it-deflist)

Markdown
:   Eine leichtgewichtige Auszeichnungssprache.

MDWriter
:   Markdown-Editor als Odoo-19-Modul.
:   Mit Versionierung und PDF-Export.

HTML
:   HyperText Markup Language.

    Zweiter Absatz zur Definition.

---

### Abbreviations (markdown-it-abbr)

Dieser Text enthält HTML und CSS als Abkürzungen — beim Hover erscheint der Tooltip.

Auch mehrfach: HTML ist nicht CSS und CSS ist nicht HTML.

*[HTML]: HyperText Markup Language
*[CSS]: Cascading Style Sheets

---

### Custom Containers (markdown-it-container)

::: warning
**Achtung:** Das ist ein Warning-Container. Sollte als Block gerendert werden.
:::

::: info
**Info:** Das ist ein Info-Container mit `inline code` und einem [Link](https://example.com).
:::

::: danger
**Gefahr:** Das ist ein Danger-Container.

Mehrere Absätze sind möglich.
:::

---

### Kombiniert (alle Plugins)

> ==Markierter Text== in einem Blockquote mit H~2~O und 2^8^ = 256.[^fn3]

Term mit Abkürzung
:   MDWriter nutzt HTML nicht direkt — Markdown wird via markdown-it gerendert.

*[MDWriter]: Markdown-Editor Odoo-Modul

[^fn3]: Kombinierter Test: Fußnote aus dem Kombinations-Abschnitt.
