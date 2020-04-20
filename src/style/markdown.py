"""
Math Inspector: a visual programing environment for scientific computing with python
Copyright (C) 2018 Matt Calhoun

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

markdown = {
	"h1": r"^#(?!#) {0,}(.*)$",
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