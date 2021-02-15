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

RE_TEXT = {
    "code_sample": r"( |\t){0,}(>>>|\.\.\.).*",
    "section_title": r"(---|===)",
    "code": r"\`(.*?)\`",
    "link_url": r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
}

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

class TextParser:
    def __init__(self, content):
        self.content = content
        self.index = 0
        self.buffer = []

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

                if tag == "code_sample" and not text[:endline].strip():
                    return TextNode(result, tag)

                if tag and not re.findall(RE_TEXT[tag], text[:endline]):
                    is_running = False

                for i in RE_TEXT:
                    match = re.findall(RE_TEXT[i], text[:endline])
                    if match:
                        tag = i
                        if i in ("code", "link_url"):
                            if i == "code":
                                endline = text.index("`")
                                self.buffer.append((match[0], i, 1 + len(match[0])))
                                self.index += 1 + endline
                            elif i == "link_url":
                                endline = text.index("http")
                                self.buffer.append((match[0], i, 1 + len(match[0])))
                                self.index += endline - 1
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
                    if text[:1] == "\n":
                        if not tag and result.strip():
                            result += "\n"
                        is_running = False
                elif endline == -1:
                    result += text
                    self.index = len(self.content)
                else:
                    result += text[:endline]
                    if not tag:
                        result += " "
                    self.index += 1 + endline

                if tag == "code_sample":
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
