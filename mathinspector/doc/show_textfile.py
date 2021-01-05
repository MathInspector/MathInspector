import re
from textwrap import dedent

def show_textfile(text, content):
    content = unwrap(content)

    text.insert("end", content)

    text.highlight(r"^((.*\n)---{1,}$)", "section_title")
    text.highlight(r"^((.*\n)==={1,}$)", "section_title")
    text.replace(r"^(?<!\n)==={1,}\n(.*\n)==={1,}$", "h1")
    text.replace(r"^(?<!\n)(.*\n)==={1,}$", "h1")
    text.replace(r"^(---{1,})$", "horizontal_rule", "\n")
    text.replace(r"^(==={1,})$", "horizontal_rule", "\n")
    
    
    text.replace(r" {0,}>>>", "console_prompt", ">>>")
    text.highlight(r"(?s)((>>>.*?\n)(\n|$))", "code_sample")


    text.replace(r"``(.*?)``", "bold")
    text.replace(r"\*\*(.*?)\*\*", "code")
    text.highlight(r"((?<!`)`(?!`)(.*?)`)", "menlo_italic")
    text.replace(r"<{0,}(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+(?<!(>|\.)))>{0,}", "link_url")
    text.replace(r"`", newtext="")

    ranges = text.tag_ranges("code_sample")
    for i in range(0, len(ranges), 2):
        start = ranges[i]
        stop = ranges[i+1]
        text.syntax_highlight(start, stop)

def unwrap(text):
    if not text: return ""
    
    result = ""
    text = dedent(text.strip())
    blocks = [i.strip() for i in text.split("\n\n")]

    for i in blocks:
        lines = [j for j in i.splitlines()]
        for k in range(0, len(lines)):
            match1 = re.search(r"([a-zA-Z`])", lines[k][:1])
            if k + 1 < len(lines) - 1:
                match2 = re.search(r"([a-zA-Z`])", lines[k+1][:1])
            elif lines[-1][:1] in ("=", "-"):
                match2 = False 
            else: 
                match2 = True


            if match1 and match2:
                result += " " + lines[k]
            else:
                result += lines[k] + "\n"

        result += "\n\n"
    return result