# Part of the same project as smog
# Available under GNU GPLv2, or at your option any later version
# This modified version only available under GNU GPLv3

# itft1.tcl - Copyright (C) 2005 Jelco Huijser jelco@user.sourceforge.net
# Based on sriv.tcl by Pat Thoyts <patthoyts@users.sourceforge.net>
#
# itft1.tcl, v0.14 2005/08/11 Jelco Huijser
# Added support for treeviews and alternating line colors

# itft1.tcl, v0.15 2018/08/18 RedFantom
# Modified to support ttk instead of ttk, indentation and formatting
# Combobox Down arrow is currently vertically stretched
# TODO: Implement support for OptionMenu widget
# TODO: Improve Treeview heading
# TODO: Fix Combobox down button (either change down arrow or -border)

namespace eval ttk::theme::itft1 {

    package provide ttk::theme::itft1 0.14

    set imgdir [file join [file dirname [info script]] smog]
    proc LoadImages {imgdir {patterns {*.gif}}} {
        foreach pattern $patterns {
            foreach file [glob -directory $imgdir $pattern] {
                set img [file tail [file rootname $file]]
                if {![info exists images($img)]} {
                    set images($img) [image create photo -file $file]
                }
            }
        }
        return [array get images]
    }
    array set I [LoadImages [file join [file dirname [info script]] itft1] *.gif]

    array set colors {
        -frame  	"#daeffd"
        -lighter	"#f9f6f6"
        -window	 	"#f9f6f6"
        -selectbg	"#3c9bf7"
        -selectfg	"#000000"
        -disabledfg	"#8dc7eb"
        -disabledbg	"#daeffd"
    }

    ttk::style theme create itft1 -settings {

	ttk::style configure . \
	    -borderwidth 	1 \
	    -background 	$colors(-frame) \
	    -fieldbackground	$colors(-window) \
	    -troughcolor	$colors(-lighter) \
	    -selectbackground	$colors(-selectbg) \
	    -selectforeground	$colors(-selectfg) \
	    -disabledbackground	$colors(-disabledbg) \
	    -disabledforeground	$colors(-disabledfg)
	ttk::style map . -foreground [list disabled $colors(-disabledfg)]

	## Buttons
	#
	ttk::style configure TButton -padding "10 0"
	ttk::style layout TButton {
	    Button.button -children {
            Button.focus -children {
                    Button.padding -children {
                    Button.label
                }
            }
	    }
	}
	ttk::style element create Button.button image \
	    [list $I(button-n) \
	        pressed $I(button-p) \
	        active $I(button-h) \
	    ] -border 8 -sticky ew
    ttk::style element create Checkbutton.indicator image \
        [list $I(check-nu) \
            {!disabled active selected} $I(check-hc) \
            {!disabled active} $I(check-hu) \
            {!disabled selected} $I(check-nc) \
        ] -width 24 -sticky w
    ttk::style element create Radiobutton.indicator image \
        [list $I(radio-nu) \
            {!disabled active selected} $I(radio-hc) \
            {!disabled active} $I(radio-hu) \
		    selected $I(radio-nc) \
        ] -width 24 -sticky w

	ttk::style configure TMenubutton -relief raised -padding {10 2}

	## Toolbar buttons
	#
	ttk::style configure Toolbutton \
	    -width 0 -relief flat -borderwidth 2 -padding 4 \
	    -background $colors(-frame) -foreground #000000 ;
	ttk::style map Toolbutton \
	    -background [list active $colors(-selectbg) disabled $colors(-disabledbg)] \
	    -foreground [list active $colors(-selectfg) disabled $colors(-disabledfg)]
	ttk::style map Toolbutton -relief {
	    disabled 	flat
	    selected	sunken  
	    pressed 	sunken  
	    active  	raised
	}

	## Entry widgets
	#
	ttk::style configure TEntry \
	    -selectborderwidth 1 \
	    -padding 2 \
	    -insertwidth 2 \
	    -font TkTextFont
	ttk::style configure TCombobox \
	    -selectborderwidth 1 \
	    -padding 2 \
	    -insertwidth 2 \
	    -font TkTextFont
	ttk::style configure TButton \
	    -padding {3 0} \
	    -font {Helvetica -12 bold}

	## Notebooks
	#
    ttk::style element create tab image \
        [list $I(tab-n) \
            active $I(tab-s) \
            disabled $I(tab-hide-n) \
        ] -border {10 6 10 2} -height 12
	ttk::style configure TNotebook.Tab -padding {4 2 4 2}
	ttk::style map TNotebook.Tab \
	    -background [list selected $colors(-frame) active $colors(-lighter)] \
	    -padding [list selected {4 4 4 2}]

	## Scrollbars
	#
	ttk::style layout Vertical.TScrollbar {
        Scrollbar.trough -children {
            Scrollbar.uparrow -side top
            Scrollbar.downarrow -side bottom
            Scrollbar.uparrow -side bottom
            Vertical.Scrollbar.thumb -side top -expand true -sticky ns
	    }
	}
	ttk::style layout Horizontal.TScrollbar {
	    Scrollbar.trough -children {
            Scrollbar.leftarrow -side left
            Scrollbar.rightarrow -side right
            Scrollbar.leftarrow -side right
            Horizontal.Scrollbar.thumb -side left -expand true -sticky we
	    }
	}
	ttk::style element create Horizontal.Scrollbar.thumb image \
	    [list $I(sb-thumb) \
	        {pressed !disabled} $I(sb-thumb-p) \
	    ] -border 3
	ttk::style element create Vertical.Scrollbar.thumb image \
	    [list $I(sb-vthumb) \
	        {pressed !disabled} $I(sb-vthumb-p) \
	    ] -border 3
	foreach dir {up down left right} {
	    ttk::style element create ${dir}arrow image \
            [list $I(arrow${dir}) \
                disabled $I(arrow${dir}) \
                pressed $I(arrow${dir}-p) \
                active $I(arrow${dir}-h) \
            ] -border {2 6 2 7}
	}

	## Scales
	#
	ttk::style element create Scale.slider image \
	    [list $I(slider) \
            {pressed !disabled} $I(slider-p)
	    ]
	ttk::style element create Vertical.Slider.slider image \
	    [list $I(vslider) \
	        {pressed !disabled} $I(vslider-p) \
	    ]

	## Progressbars
	#
	ttk::style element create Horizontal.Progress.bar \
	    image $I(sb-thumb) -border 2
	ttk::style element create Vertical.Progress.bar \
	    image $I(sb-vthumb) -border 2
	
	## Treeview
	#
	ttk::style theme settings itft1 {
	ttk::style map Item -foreground [list selected "#FFFFFF"]
	ttk::style configure Row -background "#EEEEEE"
	ttk::style configure Heading \
	    -borderwidth 1 \
	    -relief raised \
	    -font tkDefaultFont
	ttk::style configure Item -justify left
	ttk::style map Heading -relief {
	    pressed sunken
	}
	ttk::style map Row -background {
	    selected	"#3c9bf7"
	    focus   	"#ccccff"
	    alternate	"#FFFFFF"
	}
	ttk::style map Cell -foreground {
	    selected	"#FFFFFF"
	}
    }

    }
}

