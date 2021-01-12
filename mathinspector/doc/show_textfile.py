from .textparser import TextParser

def show_textfile(text, content):
    parse = TextParser(content.strip() if content else "")
    is_title = True

    for i in parse:
        text.insert("end", i.text, i.tag)
    
        if i.tag in ("", "section_title"):
            text.insert("end", " \n")
            if i.tag == "section_title":
                text.insert("end", " \n", "horizontal_rule")
                text.insert("end", " \n")

    ranges = text.tag_ranges("code_sample")
    for i in range(0, len(ranges), 2):
        start = ranges[i]
        stop = ranges[i+1]
        text.syntax_highlight(start, stop)