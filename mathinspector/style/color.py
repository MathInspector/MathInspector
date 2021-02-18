COLORS = {
	"WHITE": "#f8f8f2",
	"PURE_WHITE": "#fff",
	"NAV": "#f3f3f3",
	"LEFT_NAV": "#42433e",
	"EVEN_LIGHTER_GREY": "#f5f5f5",
	"LIGHTER_GREY": "#eeeeee",
	"LIGHT_GREY": "#ececec",
	"VERY_LIGHT_GREY": "#f5f6f7",
	"GREY": "#e6e6e6",
	"DARK_GREY": "#e2e2e2",
	"COOL_GREY": "#474842",
	"DARKER_GREY": "#989898",
	"HIGHLIGHT": "#48473d",
	"HIGHLIGHT_INACTIVE": "#383830",
	"QUALITY_GREY": "#90918b",
	"VERY_DARK_GREY": "#75715d",
	"FADED_GREY": "#42433e",
	"BACKGROUND": "#272822",
	"CONSOLE_BACKGROUND": "#191919",
	"ALT_BACKGROUND": "#252526",
	"RED": "#fc1e70",
	"GREEN": "#a4e405",
	"DARK_ORANGE": "#c65d09",
	"ORANGE": "#ff9800",
	"PROMPT": "#c65d09",
	"LIGHT_PURPLE": "#3b3b62",
	"VERY_LIGHT_PURPLE": "#343460",
	"DARK_PURPLE": "#7a52b9",
	"WIRE_INACTIVE": "#7a52b9",
	"PURPLE": "#af7dff",
	"INACTIVE": "#af7dff",
	"BLUE": "#60d9f1",
	"LINK_URL": "#0088cc",
	"LINK_URL_HOVER": "#005580",
	"ACTIVE": "#60d9f1",
	"SELECT_HOVER": "#60d9f1",
	"LIGHT_BLUE": "#308bb5",
	"HOVER": "#308bb5",
	"ACTIVE_WIRE": "#308bb5",
	"WIRE_ACTIVE": "#308bb5",
	"SELECTED": "#308bb5",
	"PALE_BLUE": "#c7cbd1",
	"COOL_BLUE": "#f6f8fa",
	"LIGHT_BLACK": "#555555",
	"DARK_BLACK": "#000000",
	"EMPTY_NODE": "#000",
	"BLACK": "#333333",
	"SILVER": "#bcc6cc",
	"YELLOW": "#e6dc6d",
	"LIGHT_YELLOW": "#ffffcc"
}

class ColorClass:
	def __init__(self):
		for i in COLORS:
			setattr(self, i, COLORS[i])

	def __repr__(self):
		result = {}
		for i in dir(self):
			if i[:2] != '__':
				result[i] = getattr(self, i)
		return str(result)

Color = ColorClass()
