# This software is copyrighted by the Regents of the University of California, Sun Microsystems, Inc., Scriptics
# Corporation, and other parties.
namespace eval ::ttk::theme::elegance {

    package provide ttk::theme::elegance 0.1

    variable I

    proc LoadImages {imgdir} {
        variable I
        foreach file [glob -directory $imgdir *.gif] {
            set img [file tail [file rootname $file]]
            set I($img) [image create photo -file $file -format gif89]
        }
    }

    LoadImages [file join [file dirname [info script]] elegance]

    variable colors
    array set colors {
        -frame      "#d8d8d8"
        -lighter    "#fcfcfc"
        -window     "#cdcdcd"
        -selectbg   "#3d3d3d"
        -selectfg   "#fcfcfc"
        -disabledfg "#747474"
    }

    ::ttk::style theme create elegance -settings {
        
        # -----------------------------------------------------------------
        # Theme defaults
        #
        ::ttk::style configure . \
            -borderwidth 1 \
            -background $colors(-frame) \
            -troughcolor $colors(-lighter) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -fieldbackground $colors(-window) \
            -font TkDefaultFont
        ::ttk::style map . -foreground [list disabled $colors(-disabledfg)]
        
        # -----------------------------------------------------------------
        # Button
        #
        ::ttk::style layout TButton {
            Button.background
            Button.button -children {
                Button.focus -children {
                    Button.label
                }
            }
        }
        ::ttk::style element create button image [list $I(button-default) \
            pressed $I(button-active)  \
            active $I(button-prelight) \
            disabled $I(button-active-disabled)   \
        ] -border 4 -sticky ew
        ::ttk::style configure TButton -padding {10 6} -anchor center
        
        # -----------------------------------------------------------------
        # Checkbutton
        #
        ::ttk::style element create Checkbutton.indicator image \
            [list $I(check1) selected $I(check2)] \
            -width 20 -sticky w
            
        # -----------------------------------------------------------------
        # Radiobutton
        #
        ::ttk::style element create Radiobutton.indicator image \
            [list $I(option1) selected $I(option2)] \
            -width 20 -sticky w

        # -----------------------------------------------------------------
        # Menubutton
        #
        ::ttk::style layout TMenubutton {
            Menubutton.background
            Menubutton.button -children {
                Menubutton.focus -children {
                    Menubutton.label -side left -expand true
                }
            }
            Menubutton.indicator -side right
        }
        ::ttk::style element create Menubutton.indicator image \
            [list $I(arrow-optionmenu) \
                {pressed !disabled} $I(arrow-optionmenu-prelight) \
                {active !disabled} $I(arrow-optionmenu-prelight) \
                disabled $I(arrow-optionmenu-disabled)] \
            -padding {0 0 18 0} -sticky w

        # -----------------------------------------------------------------
        # Entry
        #
        ::ttk::style element create Entry.field image \
            [list $I(entry-active) focus $I(entry-inactive)] \
            -height 18 -border 2 -padding {3 4} -sticky news
        
        # -----------------------------------------------------------------
        # Combobox
        #
        ::ttk::style element create Combobox.field image \
            [list $I(combo-active) \
                {readonly} $I(button-active) \
                {active}   $I(combo-active) \
            ] -border {9 10 32 15} -padding {9 4 8 4} -sticky news
        ::ttk::style element create Combobox.downarrow image \
            [list $I(stepper-down) disabled $I(stepper-down)] \
            -sticky e -border {15 0 0 0}

        # -----------------------------------------------------------------
        # Notebook elements
        #
        ::ttk::style element create tab \
            image [list $I(tab-top) selected $I(tab-top-active) active $I(tab-top-active)] \
            -border {6 6 6 4} -padding {6 3} -height 12

        ::ttk::style configure TNotebook -tabmargins {0 3 0 0}
        ::ttk::style map TNotebook.Tab \
            -expand [list selected {0 3 2 2} !selected {0 0 2}]
        
        # -----------------------------------------------------------------
        # Scrollbars elements
        #
        ::ttk::style layout Horizontal.TScrollbar {
            Horizontal.Scrollbar.trough -sticky ew -children {
                Scrollbar.leftarrow -side left -sticky {}
                Scrollbar.rightarrow -side right -sticky {}
                Horizontal.Scrollbar.thumb -side left -expand true -sticky we -children {
                    Horizontal.Scrollbar.grip -sticky {}
                }
            }
        }
        ::ttk::style element create Horizontal.Scrollbar.thumb \
            image [list $I(slider-horiz) {pressed !disabled} $I(slider-horiz-prelight)] \
            -border {1 0} -width 32 -height 16 -sticky news
        ::ttk::style element create Horizontal.Scrollbar.grip \
            image [list $I(grip-horiz) {pressed !disabled} $I(grip-horiz-prelight)]
        ::ttk::style element create Horizontal.Scrollbar.trough \
            image $I(trough-scrollbar-horiz) \
            -border 2 -padding 0 -width 32 -height 15
        ::ttk::style element create rightarrow \
            image [list $I(stepper-right) {pressed !disabled} $I(stepper-right-prelight)]
        ::ttk::style element create leftarrow \
            image [list $I(stepper-left) {pressed !disabled} $I(stepper-left-prelight)]

        ::ttk::style layout Vertical.TScrollbar {
            Scrollbar.background 
            Vertical.Scrollbar.trough -children {
                Scrollbar.uparrow -side top -sticky {}
                Scrollbar.downarrow -side bottom -sticky {}
                Vertical.Scrollbar.thumb -side top -expand true -sticky ns -children {
                    Vertical.Scrollbar.grip -sticky {}
                }
            }
        }
        ::ttk::style element create Vertical.Scrollbar.thumb \
            image [list $I(slider-vert) {pressed !disabled} $I(slider-vert-prelight)] \
            -border {0 1} -width 15 -height 32 -sticky news
        ::ttk::style element create Vertical.Scrollbar.grip \
            image [list $I(grip-vert) {pressed !disabled} $I(grip-vert-prelight)]
        ::ttk::style element create uparrow \
            image [list $I(stepper-up) {pressed !disabled} $I(stepper-up-prelight)]
        ::ttk::style element create downarrow \
            image [list $I(stepper-down) {pressed !disabled} $I(stepper-down-prelight)]
        ::ttk::style element create Vertical.Scrollbar.trough \
            image $I(trough-scrollbar-vert) \
            -border 2 -padding 0 -width 15 -height 64
        
        # -----------------------------------------------------------------
        # Progressbar
        #
        ::ttk::style element create Horizontal.Progressbar.trough \
            image $I(trough-progressbar-horiz) -border 3
        ::ttk::style element create Vertical.Progressbar.trough \
            image $I(trough-progressbar-vert) -border 3
        ::ttk::style element create Horizontal.Progressbar.pbar \
            image $I(progressbar-horiz) -border {2 9}
        ::ttk::style element create Vertical.Progressbar.pbar \
            image $I(progressbar-vert) -border {9 2}
            
        # -----------------------------------------------------------------
        # Sliders horizontal and vertical.
        #
        ::ttk::style element create Scale.slider \
            image [list $I(scale) pressed $I(scale-prelight)] -border 3
        ::ttk::style element create Horizontal.Scale.trough \
            image $I(trough-horiz) -border {6 1 7 0} -padding 0 -sticky wes
        ::ttk::style element create Vertical.Scale.trough \
            image $I(trough-vert) -border {1 6 0 7} -padding 0 -sticky nes
            
        # -----------------------------------------------------------------
        # Tree
        #
        ::ttk::style element create Treeheading.cell \
            image [list $I(list-header) pressed $I(list-header-prelight)] \
            -border {4 10} -padding 4 -sticky ewns
        ::ttk::style map Treeview \
            -background [list selected $colors(-selectbg)] \
            -foreground [list selected $colors(-selectfg)]
    }
}
