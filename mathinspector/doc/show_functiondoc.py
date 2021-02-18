"""
Leverages the parsing by docutils FunctionDoc in numpy, which is used for generating the numpy
documentation, and generates the tkinter text tags for each parsed section.
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
from .regex import RE_DOC

def show_functiondoc(text, doc, name):
    text.insert("1.0", name + "\n", ("h1", "name"))
    for i in doc:
        if len(doc[i]) > 0:
            text.insert("end", "\n")
            if i == "Signature":
                signature = doc[i].replace(", /", "").replace(", \*", "").replace(", *", "")
                text.insert("end", signature, "signature")
                text.syntax_highlight("end-1c linestart")
                text.insert("end", "\n")
            elif i  == "Summary":
                text.insert("end", "".join(doc[i]) + "\n")
            elif i  == "Extended Summary":
                text.insert("end", strjoin(doc[i]).replace("\n", "\n\n") + "\n")
            elif i  in ("Other Parameters", "Attributes", "Methods", "Warnings"):
                text.insert("end", i + "\n", "see_also_title")
                text.insert("end", " ".join(doc[i]) + "\n")
            elif i in ("Parameters", "Returns", "Raises", "Yields", "Warns"):
                text.insert("end", i.upper() + "\n", ("section_title", "bordered_box", "spacing_top"))
                for j in doc[i]:
                    text.insert("end", j[0], ("parameter_name", "bordered_box"))
                    text.insert("end", " : ", ("bordered_box"))
                    text.insert("end", j[1], ("italic", "blue", "bordered_box"))
                    text.insert("end", "\n", ("bordered_box"))
                    text.insert("end", strjoin(j[2]), ("parameter_description", "bordered_box", "spacing_bottom"))
                    text.insert("end", "\n", ("bordered_box"))
            elif i == "See Also":
                text.insert("end", "See also:\n", ("see_also", "see_also_title"))
                for j in doc[i]:
                    text.insert("end", j[0], ("doc_link", "see_also"))
                    if len(j[1]) > 0:
                        text.insert("end", " : " + "".join(j[1]) + "\n", "see_also")
                    else:
                        text.insert("end", "\n", "see_also")
                text.insert("end", "\n", "see_also")
            elif i == "Notes":
                text.insert("end", "Notes\n", "underline_title")
                text.insert("end", "\n", "horizontal_rule")
                text.insert("end", "\n", "")
                text.insert("end", strjoin(doc[i]) + "\n", "notes")
            elif i == "References":
                items = [j.strip() for j in doc[i]]
                text.insert("end", "References\n", "underline_title")
                text.insert("end", "\n", "horizontal_rule")
                text.insert("end", "\n")
                text.insert("end", " ".join(items).replace(".. ", "\n\n") + "\n", "references")
            elif i == "Examples":
                text.insert("end", "Examples\n", "underline_title")
                text.insert("end", "\n", "horizontal_rule")
                text.insert("end", "\n")
                text.insert("end", "\n".join(doc[i]) + "\n")

    for tag in RE_DOC:
        text.highlight(RE_DOC[tag], tag)

    ranges = text.tag_ranges("code_sample")
    for i in range(0, len(ranges), 2):
        start = ranges[i]
        stop = ranges[i+1]
        text.syntax_highlight(start, stop)

def strjoin(items):
    return "".join([i + " " if len(i) > 0 else "\n" for i in items])