# winxpblue - Copyright (C) 2004 Pat Thoyts <patthoyts@users.sourceforge.net>
# Available under the BSD-like 2-clause Tcl License as described in LICENSE in this folder
package require Tk 8.4;                 # minimum version for Tile
package require tile 0.7.8;             # depends upon tile

namespace eval ttk::theme::winxpblue {

package provide ttk::theme::winxpblue 0.6

proc LoadImages {imgdir} {
    variable I
    foreach file [glob -directory $imgdir *.gif] {
	set img [file tail [file rootname $file]]
	set I($img) [image create photo -file $file -format gif]
    }
}

LoadImages [file join [file dirname [info script]] winxpblue]

ttk::style theme create winxpblue -settings {

    ttk::style configure "." -background #ece9d8 -font TkDefaultFont \
	-selectbackground "#4a6984" \
	-selectforeground "#ffffff" ;

    # gtkrc has #ece9d8 for background, notebook_active looks like #efebde

    ttk::style map "." -foreground {
	disabled    	#565248
    } -background {
        disabled	#e3e1dd
	pressed		    #bab5ab
	active  		#c1d2ee
    }

    ## Buttons, checkbuttons, radiobuttons, menubuttons:
    #
    ttk::style layout TButton {
	Button.button -children { Button.focus -children { Button.label } }
    }
    ttk::style configure TButton -padding 3 -width -11 -anchor center

    ttk::style element create Button.button image [list $I(buttonNorm) \
	    pressed $I(buttonPressed) \
	    active $I(button) \
	] -border {4 9} -padding 3 -sticky nsew
    ttk::style element create Checkbutton.indicator \
	image [list $I(checkbox_unchecked) selected $I(checkbox_checked)] \
	-width 20 -sticky w
    ttk::style element create Radiobutton.indicator \
    	image [list $I(option_out) selected $I(option_in)] \
	-width 20 -sticky w
    ttk::style element create Menubutton.indicator \
	image $I(menubar_option_arrow)

    ## Toolbuttons
    #
    ttk::style map Toolbutton -background {
        disabled	#e3e1dd
	pressed		#bab5ab
	selected	#bab5ab
	active		#c1d2ee
    }
    ttk::style configure Toolbutton -anchor center

    ## Scrollbars, scale, progress bars:
    #
    ttk::style element create Horizontal.Scrollbar.thumb \
    	image $I(scroll_horizontal) -border 3 -width 15 -height 0 -sticky nsew
    ttk::style element create Vertical.Scrollbar.thumb \
    	image $I(scroll_vertical) -border 3 -width 0 -height 15 -sticky nsew
    ttk::style element create trough \
    	image $I(horizontal_trough) -sticky ew -border {0 2}
    ttk::style element create Vertical.Scrollbar.trough \
    	image $I(vertical_trough) -sticky ns -border {2 0}
    ttk::style element create Vertical.Scale.trough \
    	image $I(vertical_trough) -sticky ns -border {2 0}
    ttk::style element create Progress.bar image $I(progressbar)
    ttk::style element create Progress.trough image $I(through) -border 4

    ## Notebook parts:
    #
    ttk::style element create tab \
	image [list $I(notebook_inactive) selected $I(notebook_active)] \
	-border {2 2 2 1} -width 8
    ttk::style configure TNotebook.Tab -padding {4 2}
    ttk::style configure TNotebook -expandtab {2 1}
    ttk::style map TNotebook.Tab \
	-expand [list selected {0 0 0 1} !selected {0 0}]

    ## Arrows:
    #
    ttk::style element create uparrow image $I(arrow_up_normal) -sticky {}
    ttk::style element create downarrow image $I(arrow_down_normal) -sticky {}
    ttk::style element create leftarrow image $I(arrow_left_normal) -sticky {}
    ttk::style element create rightarrow image $I(arrow_right_normal) -sticky {}

    ## Treeview
    #
    ttk::style map Treeview \
        -background [list selected #c1d2ee] \
        -foreground [list selected #000000]
}
}

# -------------------------------------------------------------------------
