"""
Used for parsing raw text in doc strings which cannot be parsed by other methods.
"""
"""
Copyright (C) 2021 Matt Calhoun

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import re

RE_DEFAULT = {
    # "list_number": r"^[0-9]*\.",
    "italic": r"(?<!\*)\*(?!\*)(.*?)\*",
    "code_sample": r"^( |\t){0,}(>>>|\.\.\.).*",
    "h1": r"^(?<!#)#(?!#)([^\n]*) {0,}$",
    "h2": r"^(?<!#)##(?!#)(.*)$",
    "section_title": r"(---|===)",
    "code": r"(?<!\`)\`(?!\`)(.*?)\`",
    "code_block": r"\`\`\`",
    "link_url": r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
}

def show_textfile(text, content):
    parse = TextParser(content.strip() if content else "")
    is_title = True

    for i in parse:
        if i.tag == "code_block" and i.text[3:].strip():
            text.insert("end", i.text[3:] + "\n", i.tag)
        else:
            text.insert("end", i.text, i.tag)
    
        if i.tag in ("", "section_title", "h1", "h2"):
            text.insert("end", " \n")
            if i.tag:
                text.insert("end", " \n", "horizontal_rule")
                # text.insert("end", " \n")


    ranges = text.tag_ranges("code_sample")
    for i in range(0, len(ranges), 2):
        start = ranges[i]
        stop = ranges[i+1]
        text.syntax_highlight(start, stop)


class TextParser:
    def __init__(self, content, re_map=RE_DEFAULT, group_index=0, with_defaults=True):
        self.content = content
        self.index = 0
        self.buffer = []
        self.re = re_map
        self.group_index = group_index
        if with_defaults and group_index == 0:
            self.re.update(RE_DEFAULT)

    def __iter__(self):
        self.index = 0
        self.count = 0
        self.buffer.clear()
        return self

    def __next__(self):
        self.count += 1
        if len(self.buffer):
            result, tag, offset = self.buffer.pop()
            self.index += offset
            return TextNode(result, tag)

        if self.index < len(self.content):
            result = ""
            tag = ""
            is_running = True
            while is_running and self.index < len(self.content):
                text = self.content[self.index:]
                endline = -1 if "\n" not in text else text.index("\n")

                if tag in ("code_sample", "code_block") and not text[:endline].strip():
                    if tag == "code_block":
                        result = ""
                    return TextNode(result, tag)

                if tag and not re.findall(self.re[tag], text[:endline]):
                    is_running = False

                for i in self.re:
                    match = re.findall(self.re[i], text[:endline])
                    if match:
                        tag = i
                        if i in ("h1", "h2"):
                            if i == "h1":
                                self.index += len(text[:endline]) + 1
                            elif i == "h2":
                                self.index += len(text[:endline]) + 1
                            return TextNode(match[0].strip(), tag)
                        elif i in ("code", "link_url", "italic"):
                            if i == "code": 
                                endline = text.index("`")
                                self.buffer.append((match[0], i, 1 + len(match[0])))
                                self.index += 1 + endline
                            elif i == "link_url":
                                endline = text.index("http")
                                self.buffer.append((match[0], i, 1 + len(match[0])))
                                self.index += endline - 1
                            elif i == "italic":
                                endline = text.index("*")
                                self.buffer.append((match[0], i, 1 + len(match[0])))
                                self.index += endline + 2
                            result += text[:endline]
                            return TextNode(result)

                if tag and tag in ("section_title"):
                    if self.count == 1:
                        is_running = False
                        self.index += 1 + endline
                    else:
                        self.buffer.append((result, "section_title", 1 + endline))
                        return TextNode("\n")
                elif endline == 0:
                    self.index += 1
                    result = result.rstrip()
                    if text[:1] == "\n":
                        # print ("hi")
                        is_running = False
                elif endline == -1:
                    result += text
                    self.index = len(self.content)
                else:
                    result += text[:endline]
                    if not tag:
                        result += " "
                    self.index += 1 + endline

                if tag == "code_block":
                    # result = result[]
                    pass
                if tag in ("code_sample"):
                    result += "\n"

            return TextNode(result, tag)
        else:
            raise StopIteration


class TextNode:
    def __init__(self, text, tag=None):
        self.text = text
        self.tag = tag

    def __repr__(self):
        return f"{str(self.tag)}: {self.text}"        