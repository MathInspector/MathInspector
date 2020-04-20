# black.tcl -
#
#   Experimental!
#
#  Copyright (c) 2007-2008 Mats Bengtsson
#
# $Id: black.tcl,v 1.2 2009/10/25 19:21:30 oberdorfer Exp $

package require Tk 8.4;                 # minimum version for Tile
package require tile 0.8;               # depends upon tile


namespace eval ttk {
  namespace eval theme {
    namespace eval black {
      variable version 0.1
    }
  }
}

namespace eval ttk::theme::black {

  #variable imgdir [file join [file dirname [info script]] black]
  #variable I
  #array set I [tile::LoadImages $imgdir *.png]

  variable dir [file dirname [info script]]

  # NB: These colors must be in sync with the ones in black.rdb

  variable colors
  array set colors {
    -disabledfg	"DarkGrey"
    -frame  	"#424242"
    -dark	    "#222222"
    -darker 	"#121212"
    -darkest	"black"
    -lighter	"#626262"
    -lightest 	"#ffffff"
    -selectbg	"#4a6984"
    -selectfg	"#ffffff"
  }
  if {[info commands ::ttk::style] ne ""} {
    set styleCmd ttk::style
  } else {
    set styleCmd style
  }

  $styleCmd theme create black -parent clam -settings {

    # -----------------------------------------------------------------
    # Theme defaults
    #
    $styleCmd configure "." \
        -background $colors(-frame) \
        -foreground white \
        -bordercolor $colors(-darkest) \
        -darkcolor $colors(-dark) \
        -lightcolor $colors(-lighter) \
        -troughcolor $colors(-darker) \
        -selectbackground $colors(-selectbg) \
        -selectforeground $colors(-selectfg) \
        -selectborderwidth 0 \
        -font TkDefaultFont \
        ;

    $styleCmd map "." \
        -background [list disabled $colors(-frame) \
        active $colors(-lighter)] \
        -foreground [list disabled $colors(-disabledfg)] \
        -selectbackground [list  !focus $colors(-darkest)] \
        -selectforeground [list  !focus white] \
        ;

    # ttk widgets.
    $styleCmd configure TButton \
        -width -8 -padding {5 1} -relief raised
    $styleCmd configure TMenubutton \
        -width -11 -padding {5 1} -relief raised
    $styleCmd configure TCheckbutton \
        -indicatorbackground "#ffffff" -indicatormargin {1 1 4 1}
    $styleCmd configure TRadiobutton \
        -indicatorbackground "#ffffff" -indicatormargin {1 1 4 1}

    $styleCmd configure TEntry \
        -fieldbackground white -foreground black \
        -padding {2 0}
    $styleCmd configure TCombobox \
        -fieldbackground white -foreground black \
        -padding {2 0}

    $styleCmd configure TNotebook.Tab \
        -padding {6 2 6 2}

    $styleCmd map TNotebook.Tab -background [list \
        selected $colors(-lighter)]

    # tk widgets.
    $styleCmd map Menu \
        -background [list active $colors(-lighter)] \
        -foreground [list disabled $colors(-disabledfg)]

    $styleCmd configure TreeCtrl \
        -background gray30 -itembackground {gray60 gray50} \
        -itemfill white -itemaccentfill yellow

    $styleCmd map Treeview \
        -background [list selected $colors(-selectbg)] \
        -foreground [list selected $colors(-selectfg)]

    $styleCmd configure Treeview -fieldbackground $colors(-lighter)
  }
}

# A few tricks for Tablelist.

namespace eval ::tablelist:: {

  proc blackTheme {} {
    variable themeDefaults

    array set colors [array get ttk::theme::black::colors]

    array set themeDefaults [list \
      -background	  "Black" \
      -foreground	  "White" \
      -disabledforeground $colors(-disabledfg) \
      -stripebackground	  "#191919" \
      -selectbackground	  "#4a6984" \
      -selectforeground	  "DarkRed" \
      -selectborderwidth 0 \
      -font		TkTextFont \
      -labelbackground	$colors(-frame) \
      -labeldisabledBg	"#dcdad5" \
      -labelactiveBg	"#eeebe7" \
      -labelpressedBg	"#eeebe7" \
      -labelforeground	white \
      -labeldisabledFg	"#999999" \
      -labelactiveFg	white \
      -labelpressedFg	white \
      -labelfont	TkDefaultFont \
      -labelborderwidth	2 \
      -labelpady	1 \
      -arrowcolor	"" \
      -arrowstyle	sunken10x9 \
      ]
  }
}

package provide ttk::theme::black $::ttk::theme::black::version
