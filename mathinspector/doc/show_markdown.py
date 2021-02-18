"""
used for displaying markdown documents in the doc browser
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
# from .textparser import TextParser

RE_MARKDOWN = {
    "section_title": r"^#(.*)$",
}

def show_markdown(text, content):
    parse = TextParser(content.strip() if content else "", RE_MARKDOWN, group_index=0)
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