# plastik - Copyright (C) 2004 Pat Thoyts <patthoyts@users.sourceforge.net>
# Available under the BSD-like 2-clause Tcl License as described in LICENSE in this folder

package require Tk 8.4
package require tile 0.8.0

namespace eval ttk::theme::plastik {

    variable version 0.6.2
    package provide ttk::theme::plastik $version

    variable colors
    array set colors {
    	-frame 		"#efefef"
	-disabledfg	"#aaaaaa"
	-selectbg	"#657a9e"
	-selectfg	"#ffffff"
	-window		"#ffffff"
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

    LoadImages [file join [file dirname [info script]] plastik]

ttk::style theme create plastik -parent default -settings {
    ttk::style configure . \
    	-background $colors(-frame) \
	-troughcolor $colors(-frame) \
	-selectbackground $colors(-selectbg) \
	-selectforeground $colors(-selectfg) \
	-fieldbackground $colors(-window) \
	-font TkDefaultFont \
	-borderwidth 1 \
	;

    ttk::style map . -foreground [list disabled $colors(-disabledfg)]

    #
    # Layouts:
    #
    ttk::style layout Vertical.TScrollbar {
	Vertical.Scrollbar.uparrow -side top -sticky {}
	Vertical.Scrollbar.downarrow -side bottom -sticky {}
	Vertical.Scrollbar.uparrow -side bottom -sticky {}
	Vertical.Scrollbar.trough -sticky ns -children {
	    Vertical.Scrollbar.thumb -expand 1 -unit 1 -children {
		Vertical.Scrollbar.grip -sticky {}
	    }
	}
    }

    ttk::style layout Horizontal.TScrollbar {
	Horizontal.Scrollbar.leftarrow -side left -sticky {}
	Horizontal.Scrollbar.rightarrow -side right -sticky {}
	Horizontal.Scrollbar.leftarrow -side right -sticky {}
	Horizontal.Scrollbar.trough -sticky ew -children {
	    Horizontal.Scrollbar.thumb -expand 1 -unit 1 -children {
		Horizontal.Scrollbar.grip -sticky {}
	    }
        }
    }

    ttk::style layout TButton {
        Button.button -children {
	    Button.focus -children {
		Button.padding -children {
		    Button.label -side left -expand true
		}
	    }
	}
    }

    ttk::style layout Toolbutton {
        Toolbutton.border -children {
            Toolbutton.button -children {
                Toolbutton.padding -children {
                    Toolbutton.label -side left -expand true
                }
            }
        }
    }

    ttk::style layout TMenubutton {
	Menubutton.button -children {
	    Menubutton.indicator -side right
	    Menubutton.focus -children {
		Menubutton.padding -children {
		    Menubutton.label -side left -expand true
		}
	    }
	}
    }

    #
    # Elements:
    #
    ttk::style element create Button.button image [list $I(button-n) \
	    pressed	$I(button-p) \
	    active	$I(button-h) \
	] -border {4 10} -padding 4 -sticky ewns
    ttk::style element create Toolbutton.button image [list $I(tbutton-n) \
	    selected		$I(tbutton-p) \
	    pressed		$I(tbutton-p) \
	    {active !disabled}	$I(tbutton-h) \
	] -border {4 9} -padding 3 -sticky news

    ttk::style element create Checkbutton.indicator image [list $I(check-nu) \
	    {active selected}	$I(check-hc) \
	    {pressed selected}	$I(check-pc) \
	    active              $I(check-hu) \
	    selected            $I(check-nc) \
	] -sticky {}

    ttk::style element create Radiobutton.indicator image [list $I(radio-nu) \
	    {active selected}	$I(radio-hc) \
	    {pressed selected}  $I(radio-pc) \
	    active              $I(radio-hu) \
	    selected            $I(radio-nc) \
	] -sticky {}

    ttk::style element create Horizontal.Scrollbar.thumb image $I(hsb-n) \
	-border 3 -sticky ew
    ttk::style element create Horizontal.Scrollbar.grip image $I(hsb-g)
    ttk::style element create Horizontal.Scrollbar.trough image $I(hsb-t)
    ttk::style element create Vertical.Scrollbar.thumb image $I(vsb-n) \
	-border 3 -sticky ns
    ttk::style element create Vertical.Scrollbar.grip image $I(vsb-g)
    ttk::style element create Vertical.Scrollbar.trough image $I(vsb-t)
    ttk::style element create Scrollbar.uparrow image \
	[list $I(arrowup-n) pressed $I(arrowup-p)] -sticky {}
    ttk::style element create Scrollbar.downarrow \
	image [list $I(arrowdown-n) pressed $I(arrowdown-p)] -sticky {}
    ttk::style element create Scrollbar.leftarrow \
	image [list $I(arrowleft-n) pressed $I(arrowleft-p)] -sticky {}
    ttk::style element create Scrollbar.rightarrow \
	image [list $I(arrowright-n) pressed $I(arrowright-p)] -sticky {}

    ttk::style element create Horizontal.Scale.slider image $I(hslider-n) \
	-sticky {}
    ttk::style element create Horizontal.Scale.trough image $I(hslider-t) \
	-border 1 -padding 0
    ttk::style element create Vertical.Scale.slider image $I(vslider-n) \
	-sticky {}
    ttk::style element create Vertical.Scale.trough image $I(vslider-t) \
	-border 1 -padding 0

    ttk::style element create Entry.field \
	image [list $I(entry-n) focus $I(entry-f)] \
	-border 2 -padding {3 4} -sticky news

    ttk::style element create Labelframe.border image $I(border) \
	-border 4 -padding 4 -sticky news

    ttk::style element create Menubutton.button \
	image [list $I(combo-r) active $I(combo-ra)] \
	-sticky news -border {4 6 24 15} -padding {4 4 5}
    ttk::style element create Menubutton.indicator \
      image [list $I(arrow-n) disabled $I(arrow-d)] \
      -sticky e -border {15 0 0 0}

    ttk::style element create Combobox.field \
	image [list $I(combo-n) \
	    [list readonly $hover !disabled]	$I(combo-ra) \
	    [list focus $hover !disabled]	$I(combo-fa) \
	    [list $hover !disabled]		$I(combo-a) \
	    [list !readonly focus !disabled]	$I(combo-f) \
	    [list !readonly disabled]		$I(combo-d) \
	    readonly				$I(combo-r) \
	] -border {4 6 24 15} -padding {4 4 5} -sticky news
    ttk::style element create Combobox.downarrow \
      image [list $I(arrow-n) disabled $I(arrow-d)] \
      -sticky e -border {15 0 0 0}

    # ttk::style element create Notebook.client image $I(notebook-c) -border 2
    ttk::style element create Notebook.tab image [list $I(notebook-tn) \
	    selected	$I(notebook-ts) \
	    active	$I(notebook-ta) \
	] -padding {0 2 0 0} -border {4 10 4 10}

    ttk::style element create Progressbar.trough \
	image $I(hprogress-t) -border 2
    ttk::style element create Horizontal.Progressbar.pbar \
	image $I(hprogress-b) -border {2 9}
    ttk::style element create Vertical.Progressbar.pbar \
	image $I(vprogress-b) -border {9 2}

    ttk::style element create Treeheading.cell \
	image [list $I(tree-n) pressed $I(tree-p)] \
	-border {4 10} -padding 4 -sticky ewns

    # Use the treeview item indicator from the alt theme, as that looks better
    ttk::style element create Treeitem.indicator from alt

    #
    # Settings:
    #
    ttk::style configure TButton -width -10 -anchor center
    ttk::style configure Toolbutton -anchor center
    ttk::style configure TNotebook -tabmargins {0 2 0 0}
    ttk::style configure TNotebook.Tab -padding {6 2 6 2} -expand {0 0 2}
    ttk::style map TNotebook.Tab -expand [list selected {1 2 4 2}]

    # Spinbox (only available since 8.6b1 or 8.5.9)
    ttk::style layout TSpinbox {
	Spinbox.field -side top -sticky we -children {
	    Spinbox.buttons -side right -border 1 -children {
		null -side right -sticky {} -children {
		    Spinbox.uparrow -side top -sticky e
		    Spinbox.downarrow -side bottom -sticky e
		}
	    }
	    Spinbox.padding -sticky nswe -children {
		Spinbox.textarea -sticky nswe
	    }
	}
    }
    ttk::style element create Spinbox.field \
      image [list $I(spinbox-n) focus $I(spinbox-f)] \
      -border {2 2 18 2} -padding {3 0 0} -sticky news
    ttk::style element create Spinbox.buttons \
      image [list $I(spinbut-n) [list $hover !disabled] $I(spinbut-a)] \
      -border {5 3 3} -padding {0 0 1 0}
    ttk::style element create Spinbox.uparrow image [list $I(spinup-n) \
      disabled	$I(spinup-d) \
      pressed	$I(spinup-p) \
      ]
    ttk::style element create Spinbox.downarrow image [list $I(spindown-n) \
      disabled	$I(spindown-d) \
      pressed	$I(spindown-p) \
      ]
    ttk::style element create Spinbox.padding image $I(spinbut-n) \
      -border {0 3}
    
    # Treeview (since 8.6b1 or 8.5.9)
    ttk::style configure Treeview -background $colors(-window)
    ttk::style map Treeview \
      -background [list selected $colors(-selectbg)] \
      -foreground [list selected $colors(-selectfg)]

    # Treeview (older version)
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
} }
