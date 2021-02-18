"""
Math Inspector: a visual programming environment for scientific computing
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
RE_MARKDOWN = {
	"h1": r"^#(?!#) {0,}(.*)\n",
	"h2": (r"^##(?!#) {0,1}(.*)", r"^(?!\n)(.*\n===={0,})$", r"^(?!\n)(.*\n----{0,})$"),
	"h3": r"^###(?!#) {0,}(.*)",
	"italic": r"(?<!\*)\*(?!\*)(.*?)\*",
	"bold": r"\*\*(?!\*)(.*?)\*\*",
	"blockquote": r"^>(?!>)(.*)",
	"unordered_list": r"^((\t|    ) {0,}-(?!-).*)",
	"code": r"`(?!`)(.*?)`",
	"code_block": r"(?s)```\n{0,}(.*?)\n{0,}```.*$",
	"horizontal_rule": (r"^()----{0,}$", r"^()===={0,}$")
}

RE_DOC = {
    "link_url": r"()(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)",
    "code_sample": r"()(?s)(>>>.*?\n)\n",
    "console_prompt": r"((>>>))"
}
