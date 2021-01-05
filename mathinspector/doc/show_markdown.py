from .regex import RE_MARKDOWN, RE_DOC

def show_markdown(text, content):
    text.delete("1.0", "end")
    text.insert("1.0", content)
    for tag in RE_MARKDOWN:
        if isinstance(RE_MARKDOWN[tag], tuple):
            for i in RE_MARKDOWN[tag]:
                text.highlight(i, tag)
        else:
            text.highlight(RE_MARKDOWN[tag], tag)

    for tag in RE_DOC:
        text.highlight(RE_DOC[tag], tag)     

    text.replace(r"^(---{1,})$", "horizontal_rule", "\n")
    text.replace(r"^(==={1,})$", "horizontal_rule", "\n")

    # text.replace(r"^([-\*+])", "unordered-list", "•")
    # text.replace(r"^(\t[-\*+])", "unordered-list", "\t◦")
