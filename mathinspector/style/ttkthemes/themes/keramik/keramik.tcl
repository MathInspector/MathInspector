# keramik - Copyright (C) 2004 Pat Thoyts <patthoyts@users.sourceforge.net>
# Available under the BSD-like 2-clause Tcl License as described in LICENSE in this folder

package require Tk 8.4;                 # minimum version for Tile
package require tile 0.8.0;             # depends upon tile 0.8.0

namespace eval ttk {
    namespace eval theme {
        namespace eval keramik {
            variable version 0.6.2
        }
        namespace eval keramik_alt {
	    variable version 0.6.2
	}
    }
}

namespace eval ttk::theme::keramik {

    variable colors
    array set colors {
        -frame      "#cccccc"
        -lighter    "#cccccc"
        -window     "#ffffff"
        -selectbg   "#0a5f89"
        -selectfg   "#ffffff"
        -disabledfg "#aaaaaa"
    }

    variable hover hover
    if {[package vsatisfies [package present Ttk] 8-8.5.9] || \
      [package vsatisfies [package present Ttk] 8.6-8.6b1]} {
        # The hover state is not supported prior to 8.6b1 or 8.5.9
        set hover active
    }

    proc LoadImages {imgdir} {
        variable I
        foreach file [glob -directory $imgdir *.gif] {
            set img [file tail [file rootname $file]]
            set I($img) [image create photo -file $file -format gif89]
        }
    }

    LoadImages [file join [file dirname [info script]] keramik]

    ttk::style theme create keramik -parent alt -settings {


        # -----------------------------------------------------------------
        # Theme defaults
        #
        ttk::style configure . \
            -borderwidth 1 \
            -background $colors(-frame) \
            -troughcolor $colors(-lighter) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
	    -fieldbackground $colors(-window) \
            -font TkDefaultFont \
            ;

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]
                
        # -----------------------------------------------------------------
        # Button elements
        #  - the button has a large rounded border and needs a bit of
        #    horizontal padding.
        #  - the checkbutton and radiobutton have the focus drawn around 
        #    the whole widget - hence the new layouts.
        #
        ttk::style layout TButton {
            Button.background
            Button.button -children {
                Button.focus -children {
                    Button.label
                }
            }
        }
        ttk::style layout Toolbutton {
            Toolbutton.background
            Toolbutton.button -children {
                Toolbutton.focus -children {
                    Toolbutton.label
                }
            }
        }

        ttk::style element create button image [list $I(button-n) \
                {pressed !disabled}	$I(button-p) \
		selected		$I(button-s) \
                {active !disabled}	$I(button-h) \
                disabled		$I(button-d)] \
            -border {8 6 8 16} -padding {6 6} -sticky news
        ttk::style configure TButton -padding {10 6} -anchor center

        ttk::style element create Toolbutton.button image [list $I(tbar-n) \
                {pressed !disabled}	$I(tbar-p) \
		selected		$I(tbar-p) \
                {active !disabled}	$I(tbar-a)] \
            -border {2 9 2 18} -padding {2 2} -sticky news
	ttk::style configure Toolbutton -anchor center

        ttk::style element create Checkbutton.indicator \
	    image [list $I(check-u) selected $I(check-c)] \
            -width 20 -sticky w

        ttk::style element create Radiobutton.indicator \
	    image [list $I(radio-u) selected $I(radio-c)] \
            -width 20 -sticky w

        # The layout for the menubutton is modified to have a button element
        # drawn on top of the background. This means we can have transparent
        # pixels in the button element. Also, the pixmap has a special
        # region on the right for the arrow. So we draw the indicator as a
        # sibling element to the button, and draw it after (ie on top of) the
        # button image.
        ttk::style layout TMenubutton {
            Menubutton.background
            Menubutton.button -children {
                Menubutton.focus -children {
                    Menubutton.padding -children {
                        Menubutton.label -side left -expand true
                    }
                }
            }
            Menubutton.indicator -side right
        }
        ttk::style element create Menubutton.button image [list $I(mbut-n) \
                {active !disabled}      $I(mbut-a) \
                {pressed !disabled}     $I(mbut-a) \
                {disabled}              $I(mbut-d)] \
            -border {7 10 29 15} -padding {7 4 29 4} -sticky news
        ttk::style element create Menubutton.indicator image $I(mbut-arrow-n) \
            -width 11 -sticky w -padding {0 0 18 0}

	ttk::style element create Combobox.field image [list $I(cbox-n) \
	        [list readonly disabled]	$I(mbut-d) \
		[list readonly $hover]		$I(mbut-a) \
		[list readonly]			$I(mbut-n) \
		[list disabled]			$I(cbox-d) \
		[list $hover]			$I(cbox-a) \
	    ] -border {9 10 32 15} -padding {9 4 8 4} -sticky news
	ttk::style element create Combobox.downarrow image $I(mbut-arrow-n) \
	    -width 11 -sticky e -border {22 0 0 0}

        # -----------------------------------------------------------------
        # Scrollbars, scale and progress elements
        #  - the scrollbar has three arrow buttons, two at the bottom and
        #    one at the top.
        #
        ttk::style layout Vertical.TScrollbar {
            Scrollbar.background 
            Vertical.Scrollbar.trough -children {
                Scrollbar.uparrow -side top
                Scrollbar.downarrow -side bottom
                Scrollbar.uparrow -side bottom
                Vertical.Scrollbar.thumb -side top -expand true -sticky ns
            }
        }
        
        ttk::style layout Horizontal.TScrollbar {
            Scrollbar.background 
            Horizontal.Scrollbar.trough -children {
                Scrollbar.leftarrow -side left
                Scrollbar.rightarrow -side right
                Scrollbar.leftarrow -side right
                Horizontal.Scrollbar.thumb -side left -expand true -sticky we
            }
        }

        ttk::style element create Horizontal.Scrollbar.thumb \
	    image [list $I(hsb-n) {pressed !disabled} $I(hsb-p)] \
            -border {6 4} -width 15 -height 16 -sticky news
	ttk::style element create Horizontal.Scrollbar.trough image $I(hsb-t)

        ttk::style element create Vertical.Scrollbar.thumb \
	    image [list $I(vsb-n) {pressed !disabled} $I(vsb-p)] \
            -border {4 6} -width 16 -height 15 -sticky news
	ttk::style element create Vertical.Scrollbar.trough image $I(vsb-t)
        
        ttk::style element create Horizontal.Scale.slider image $I(hslider-n) \
	    -border 3
	ttk::style element create Horizontal.Scale.trough image $I(hslider-t) \
	    -border {6 1 7 0} -padding 0 -sticky wes
        
        ttk::style element create Vertical.Scale.slider image $I(vslider-n) \
            -border 3
	ttk::style element create Vertical.Scale.trough image $I(vslider-t) \
	    -border {1 6 0 7} -padding 0 -sticky nes
        
        ttk::style element create Horizontal.Progressbar.pbar \
	    image $I(progress-h) -border {1 1 6}
        
        ttk::style element create Vertical.Progressbar.pbar \
	    image $I(progress-v) -border {1 6 1 1}
        
        ttk::style element create uparrow \
	    image [list $I(arrowup-n) {pressed !disabled} $I(arrowup-p)]
                  
        ttk::style element create downarrow \
	    image [list $I(arrowdown-n) {pressed !disabled} $I(arrowdown-p)]

        ttk::style element create rightarrow \
	    image [list $I(arrowright-n) {pressed !disabled} $I(arrowright-p)]

        ttk::style element create leftarrow \
	    image [list $I(arrowleft-n) {pressed !disabled} $I(arrowleft-p)]

	# Treeview elements
	#
	ttk::style element create Treeheading.cell \
	    image [list $I(tree-n) pressed $I(tree-p)] \
	    -border {5 15 5 8} -padding 12 -sticky ewns

        # -----------------------------------------------------------------
        # Notebook elements
        #
        ttk::style element create tab \
	    image [list $I(tab-n) selected $I(tab-p) active $I(tab-p)] \
            -border {6 6 6 4} -padding {6 3} -height 12

	ttk::style configure TNotebook -tabmargins {0 3 0 0}
	ttk::style map TNotebook.Tab \
	    -expand [list selected {0 3 2 2} !selected {0 0 2}]

	## Settings.
	#
	ttk::style configure TLabelframe -borderwidth 2 -relief groove

	# Spinbox (only available since 8.6b1 or 8.5.9)
	ttk::style layout TSpinbox {
	    Spinbox.field -side top -sticky we -children {
		Spinbox.arrows -side right -sticky ns -children {
		    null -side right -sticky {} -children {
			Spinbox.uparrow -side top -sticky w
			Spinbox.downarrow -side bottom -sticky w
		    }
		}
		Spinbox.padding -sticky nswe -children {
		    Spinbox.textarea -sticky nswe
		}
	    }
	}
	ttk::style element create Spinbox.arrows image $I(spinbox-a) \
	  -border {0 9} -padding 0
	ttk::style element create Spinbox.uparrow \
	  image [list $I(spinup-n) {pressed !disabled} $I(spinup-p)]
	ttk::style element create Spinbox.downarrow \
	  image [list $I(spindown-n) {pressed !disabled} $I(spindown-p)]
	    
	# Treeview (since 8.6b1 or 8.5.9)
	ttk::style configure Treeview -background $colors(-window)
	ttk::style map Treeview \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]

	# Treeview (older version)
	ttk::style configure Treeview.Row -background $colors(-window)
	ttk::style configure Row -background $colors(-window)
	ttk::style configure Cell -background $colors(-window)
	ttk::style map Row \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]
      	ttk::style map Cell \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]
	ttk::style map Item \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]
    }
}

namespace eval ttk::theme::keramik_alt {

    variable colors
    array set colors {
        -frame      "#cccccc"
        -lighter    "#cccccc"
        -window     "#ffffff"
        -selectbg   "#0a5f89"
        -selectfg   "#ffffff"
        -disabledfg "#aaaaaa"
    }

    proc LoadImages {imgdir} {
        variable I
        foreach file [glob -directory $imgdir *.gif] {
            set img [file tail [file rootname $file]]
            set I($img) [image create photo -file $file -format gif89]
        }
    }

    LoadImages [file join [file dirname [info script]] keramik_alt]

    ttk::style theme create keramik_alt -parent keramik -settings {

        # -----------------------------------------------------------------
        # Theme defaults
        #
        ttk::style configure . \
            -borderwidth 1 \
            -background $colors(-frame) \
            -troughcolor $colors(-lighter) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
	    -fieldbackground $colors(-window) \
            -font TkDefaultFont \
            ;

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]

	# The alternative keramik theme doesn't have the conspicuous
	# highlighted scrollbars of the main keramik theme.
	#
        ttk::style element create Vertical.Scrollbar.thumb \
            image [list $I(vsb-a) {pressed !disabled} $I(vsb-h)] \
            -border {4 6} -width 16 -height 15 -sticky news
        ttk::style element create Horizontal.Scrollbar.thumb \
	    image [list $I(hsb-a) {pressed !disabled} $I(hsb-h)] \
	    -border {6 4} -width 15 -height 16 -sticky news

	# Repeat the settings because they don't seem to be copied from the
	# parent theme.
	#
        ttk::style configure TButton -padding {10 6} -anchor center
	ttk::style configure Toolbutton -anchor center
	ttk::style configure TNotebook -tabmargins {0 3 0 0}
	ttk::style map TNotebook.Tab \
		-expand [list selected {0 3 2 2} !selected {0 0 2}]

	ttk::style configure TLabelframe -borderwidth 2 -relief groove

	# Treeview (since 8.6b1 or 8.5.9)
	ttk::style configure Treeview -background $colors(-window)
	ttk::style map Treeview \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]

	# Treeview (older version)
	ttk::style configure Treeview -padding 0
	ttk::style configure Treeview.Row -background $colors(-window)
	ttk::style configure Row -background $colors(-window)
	ttk::style configure Cell -background $colors(-window)
	ttk::style map Row \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]
	ttk::style map Cell \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]
	ttk::style map Item \
	  -background [list selected $colors(-selectbg)] \
	  -foreground [list selected $colors(-selectfg)]
    }
}

package provide ttk::theme::keramik $::ttk::theme::keramik::version
package provide ttk::theme::keramik_alt $::ttk::theme::keramik_alt::version
