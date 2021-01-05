# Copyright (C) 2018 RedFantom
# Derived from https://github.com/ddnexus/equilux-theme (GNU GPLv2)
# Based on /ttkthemes/ttkthemes/themes/arc/arc.tcl (GNU GPLv3)
# Available under the GNU GPLv3, or at your option any later version

# Theme Equilux
namespace eval ttk::theme::equilux {
    
    # Widget colors
    variable colors
    array set colors {
        -fg             "#a6a6a6"
        -bg             "#464646"
        -disabledbg     "#2e2e2e"
        -disabledfg     "#999999"
        -selectbg       "#414141"
        -selectfg       "#a6a6a6"
        -window         "#373737"
        -focuscolor     "#bebebe"
        -checklight     "#e6e6e6"
    }
    
    # Function to load images from subdirectory
    variable directory
    # Subdirectory /equilux
    set directory [file join [file dirname [info script]] equilux]
    variable images
    # Load the images
    foreach file [glob -directory $directory *.png] {
        set img [file tail [file rootname $file]]
        set images($img) [image create photo -file $file -format png]
    }
    
    # Create a new ttk::style
    ttk::style theme create equilux -parent default -settings {
        # Configure basic style settings
        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -fieldbackground $colors(-window) \
            -font TkDefaultFont \
            -borderwidth 1 \
            -focuscolor $colors(-focuscolor)
        
        # Map disabled colors to disabledfg
        ttk::style map . -foreground [list disabled $colors(-disabledfg)]
        
        # WIDGET LAYOUTS
        
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
            Toolbutton.button -children {
                Toolbutton.focus -children {
                    Toolbutton.padding -children {
                        Toolbutton.label -side left -expand true
                    }
                }
            }
        }

        ttk::style layout Vertical.TScrollbar {
            Vertical.Scrollbar.trough -sticky ns -children {
                Vertical.Scrollbar.thumb -expand true
            }
        }

        ttk::style layout Horizontal.TScrollbar {
            Horizontal.Scrollbar.trough -sticky ew -children {
                Horizontal.Scrollbar.thumb -expand true
            }
        }

        ttk::style layout TMenubutton {
            Menubutton.button -children {
                Menubutton.focus -children {
                    Menubutton.padding -children {
                        Menubutton.indicator -side right
                        Menubutton.label -side right -expand true
                    }
                }
            }
        }

        ttk::style layout TCombobox {
            Combobox.field -sticky nswe -children {
                Combobox.downarrow -side right -sticky ns -children {
                    Combobox.arrow -side right
                }
                Combobox.padding -expand true -sticky nswe -children {
                    Combobox.textarea -sticky nswe
                }
            }
        }

        ttk::style layout TSpinbox {
            Spinbox.field -side top -sticky we -children {
                Spinbox.buttons -side right -children {
                    null -side right -sticky {} -children {
                        Spinbox.uparrow -side top -sticky nse -children {
                            Spinbox.symuparrow -side right -sticky e
                        }
                        Spinbox.downarrow -side bottom -sticky nse -children {
                            Spinbox.symdownarrow -side right -sticky e
                        }
                    }
                }
                Spinbox.padding -sticky nswe -children {
                    Spinbox.textarea -sticky nswe
                }
            }
        }

        # Style elements
        
        # Button
        ttk::style element create Button.button image [list $images(button) \
                pressed     $images(button-active) \
                active      $images(button-hover) \
                disabled    $images(button-insensitive) \
            ] -border 3 -padding {3 2} -sticky ewns

        # Toolbutton
        ttk::style element create Toolbutton.button image [list $images(button-empty) \
                selected            $images(button-active) \
                pressed             $images(button-active) \
                {active !disabled}  $images(button-hover) \
            ] -border 3 -padding {3 2} -sticky news
        # Checkbutton
        ttk::style element create Checkbutton.indicator image [list $images(checkbox-unchecked) \
                disabled            $images(checkbox-unchecked-insensitive) \
                {active selected}   $images(checkbox-checked) \
                {pressed selected}  $images(checkbox-checked) \
                active              $images(checkbox-unchecked) \
                selected            $images(checkbox-checked) \
                {disabled selected} $images(checkbox-checked-insensitive) \
            ] -width 22 -sticky w -padding {0 0 25 0}
        # Radiobutton
        ttk::style element create Radiobutton.indicator image [list $images(radio-unchecked) \
                disabled            $images(radio-unchecked-insensitive) \
                {active selected}   $images(radio-checked) \
                {pressed selected}  $images(radio-checked) \
                active              $images(radio-unchecked) \
                selected            $images(radio-checked) \
                {disabled selected} $images(radio-checked-insensitive) \
            ] -width 22 -sticky w -padding {0 0 25 0}

        ttk::style element create Horizontal.Scrollbar.trough image $images(trough-scrollbar-horiz)
        ttk::style element create Horizontal.Scrollbar.thumb \
            image [list $images(slider-horiz) \
                        {pressed !disabled} $images(slider-horiz-active) \
                        {active !disabled}  $images(slider-horiz-prelight) \
                        disabled            $images(slider-horiz-insens) \
            ] -border 6 -sticky ew

        ttk::style element create Vertical.Scrollbar.trough image $images(trough-scrollbar-vert)
        ttk::style element create Vertical.Scrollbar.thumb \
            image [list $images(slider-vert) \
                        {pressed !disabled} $images(slider-vert-active) \
                        {active !disabled}  $images(slider-vert-prelight) \
                        disabled            $images(slider-vert-insens) \
            ] -border 6 -sticky ns

        ttk::style element create Horizontal.Scale.trough \
            image [list $images(trough-horizontal-active) disabled $images(trough-horizontal)] \
            -border {8 5 8 5} -padding 0
        ttk::style element create Horizontal.Scale.slider \
            image [list $images(slider) disabled $images(slider-insensitive) active $images(slider-prelight)] \
            -sticky {}

        ttk::style element create Vertical.Scale.trough \
            image [list $images(trough-vertical-active) disabled $images(trough-vertical)] \
            -border {5 8 5 8} -padding 0
        ttk::style element create Vertical.Scale.slider \
            image [list $images(slider) disabled $images(slider-insensitive) active $images(slider-prelight)] \
            -sticky {}

        ttk::style element create Entry.field \
            image [list $images(entry-border-bg) \
                        focus $images(entry-active) \
                        disabled $images(entry-border-disabled)] \
            -border 4 -padding {6 4} -sticky news

        ttk::style element create Labelframe.border image $images(labelframe) \
            -border 4 -padding 4 -sticky news

        ttk::style element create Menubutton.button \
            image [list $images(button) \
                        pressed  $images(button-active) \
                        active   $images(button-hover) \
                        disabled $images(button-insensitive) \
            ] -sticky news -border 3 -padding {3 2}
        ttk::style element create Menubutton.indicator \
            image [list $images(arrow-down) \
                        active   $images(arrow-down-prelight) \
                        pressed  $images(arrow-down-prelight) \
                        disabled $images(arrow-down-insens) \
            ] -sticky e -width 20

        ttk::style element create Combobox.field \
            image [list $images(combo-entry) \
                {readonly disabled}  $images(button-insensitive) \
                {readonly pressed}   $images(button-active) \
                {readonly hover}     $images(button-hover) \
                readonly             $images(button) \
                {disabled} $images(combo-entry-insensitive) \
                {hover}    $images(combo-entry) \
            ] -border 4 -padding {6 0 0 0}
        ttk::style element create Combobox.downarrow \
            image [list $images(combo-entry-button) \
                        pressed   $images(combo-entry-button-active) \
                        active    $images(combo-entry-button-hover) \
                        disabled  $images(combo-entry-button-insensitive) \
          ] -border 4 -padding {0 10 6 10}
        ttk::style element create Combobox.arrow \
            image [list $images(arrow-down) \
                        active    $images(arrow-down-prelight) \
                        pressed   $images(arrow-down-prelight) \
                        disabled  $images(arrow-down-insens) \
          ]  -sticky e -width 15

        ttk::style element create Spinbox.field \
            image [list $images(combo-entry) focus $images(combo-entry-active)] \
            -border 4 -padding {6 0 0 0} -sticky news
        ttk::style element create Spinbox.uparrow \
            image [list $images(up-background) \
                        pressed   $images(up-background-active) \
                        active    $images(up-background-hover) \
                        disabled  $images(up-background-disable) \
            ] -width 20 -border {0 2 3 0} -padding {0 5 6 2}
        ttk::style element create Spinbox.symuparrow \
            image [list $images(arrow-up-small) \
                        active    $images(arrow-up-small-prelight) \
                        pressed   $images(arrow-up-small-prelight) \
                        disabled  $images(arrow-up-small-insens) \
            ]
        ttk::style element create Spinbox.downarrow \
            image [list $images(down-background) \
                        pressed   $images(down-background-active) \
                        active    $images(down-background-hover) \
                        disabled  $images(down-background-disable) \
            ] -width 20 -border {0 0 3 2} -padding {0 2 6 5}
        ttk::style element create Spinbox.symdownarrow \
            image [list $images(arrow-down) \
                        active    $images(arrow-down-prelight) \
                        pressed   $images(arrow-down-prelight) \
                        disabled  $images(arrow-down-insens) \
          ]

        ttk::style element create Notebook.client \
            image $images(notebook) -border 1
        ttk::style element create Notebook.tab \
            image [list $images(tab-top) \
                        selected    $images(tab-top-active) \
                        active      $images(tab-top-hover) \
            ] -padding {0 2 0 0} -border 3

        ttk::style element create Horizontal.Progressbar.trough \
            image $images(progressbar-horiz-bg) -border {2 2 2 2} -padding 1
        ttk::style element create Horizontal.Progressbar.pbar \
            image $images(progressbar-horiz) -border {4 0 4 0}

        ttk::style element create Vertical.Progressbar.trough \
            image $images(progressbar-vert-bg) -border {2 2 2 2} -padding 1
        ttk::style element create Vertical.Progressbar.pbar \
            image $images(progressbar-vert) -border {0 4 0 4}

        ttk::style element create Treeview.field \
            image $images(treeview) -border 1
        ttk::style element create Treeheading.cell \
            image [list $images(tree-heading) pressed $images(tree-heading-active)] \
            -border 1 -padding 4 -sticky ewns

        ttk::style element create Treeitem.indicator \
            image [list $images(plus) user2 $images(empty) user1 $images(minus)] \
            -width 15 -sticky w

        # Settings
        ttk::style configure TButton -padding {8 4 8 4} -width -10 -anchor center
        ttk::style configure TMenubutton -padding {8 4 4 4}
        ttk::style configure Toolbutton -anchor center
        ttk::style configure TCheckbutton -padding 3
        # Radiobutton and Checkbutton hover highlighting: disabled by default
        # ttk::style map TRadiobutton -background [list active $colors(-checklight)]
        # ttk::style map TCheckbutton -background [list active $colors(-checklight)]
        ttk::style configure TRadiobutton -padding 3
        ttk::style configure TNotebook -tabmargins {0 2 0 0}
        ttk::style configure TNotebook.Tab -padding {6 2 6 2} -expand {0 0 2}
        ttk::style map TNotebook.Tab -expand [list selected {1 2 4 2}]
        ttk::style configure TSeparator -background $colors(-bg)

        # Treeview
        ttk::style configure Treeview -background $colors(-window)
        ttk::style configure Treeview.Item -padding {2 0 0 0}
        ttk::style map Treeview \
            -background [list selected $colors(-selectbg)] \
            -foreground [list selected $colors(-selectfg)]
    }
}

variable version 1.1
package provide ttk::theme::equilux $version

