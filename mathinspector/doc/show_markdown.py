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
