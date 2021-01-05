#  Copyright (c) 2015 Sergei Golovan <sgolovan@nes.ru>
#  Derived from https://github.com/horst3180/arc-theme/ under the GNU GPLv3
#  Thus this is available under GNU GPLv3 also, as described in LICENSE

namespace eval ttk::theme::arc {

    variable colors
    array set colors {
        -fg             "#5c616c"
        -bg             "#f5f6f7"
        -disabledbg     "#fbfcfc"
        -disabledfg     "#a9acb2"
        -selectbg       "#5294e2"
        -selectfg       "#ffffff"
        -window         "#ffffff"
        -focuscolor     "#5c616c"
        -checklight     "#fbfcfc"
    }

    proc LoadImages {imgdir} {
        variable I
        foreach file [glob -directory $imgdir *.gif] {
            set img [file tail [file rootname $file]]
            set I($img) [image create photo -file $file]
        }
    }

    LoadImages [file join [file dirname [info script]] arc]

    ttk::style theme create arc -parent default -settings {
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

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]

        #
        # Layouts:
        #

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

        #
        # Elements:
        #

        ttk::style element create Button.button image [list $I(button) \
                pressed     $I(button-active) \
                active      $I(button-hover) \
                disabled    $I(button-insensitive) \
            ] -border 3 -padding {3 2} -sticky ewns

        ttk::style element create Toolbutton.button image [list $I(button-empty) \
                selected            $I(button-active) \
                pressed             $I(button-active) \
                {active !disabled}  $I(button-hover) \
            ] -border 3 -padding {3 2} -sticky news

        ttk::style element create Checkbutton.indicator image [list $I(checkbox-unchecked) \
                disabled            $I(checkbox-unchecked-insensitive) \
                {active selected}   $I(checkbox-checked) \
                {pressed selected}  $I(checkbox-checked) \
                active              $I(checkbox-unchecked) \
                selected            $I(checkbox-checked) \
                {disabled selected} $I(checkbox-checked-insensitive) \
            ] -width 22 -sticky w

        ttk::style element create Radiobutton.indicator image [list $I(radio-unchecked) \
                disabled            $I(radio-unchecked-insensitive) \
                {active selected}   $I(radio-checked) \
                {pressed selected}  $I(radio-checked) \
                active              $I(radio-unchecked) \
                selected            $I(radio-checked) \
                {disabled selected} $I(radio-checked-insensitive) \
            ] -width 22 -sticky w

        ttk::style element create Horizontal.Scrollbar.trough image $I(trough-scrollbar-horiz)
        ttk::style element create Horizontal.Scrollbar.thumb \
            image [list $I(slider-horiz) \
                        {pressed !disabled} $I(slider-horiz-active) \
                        {active !disabled}  $I(slider-horiz-prelight) \
                        disabled            $I(slider-horiz-insens) \
            ] -border 6 -sticky ew

        ttk::style element create Vertical.Scrollbar.trough image $I(trough-scrollbar-vert)
        ttk::style element create Vertical.Scrollbar.thumb \
            image [list $I(slider-vert) \
                        {pressed !disabled} $I(slider-vert-active) \
                        {active !disabled}  $I(slider-vert-prelight) \
                        disabled            $I(slider-vert-insens) \
            ] -border 6 -sticky ns

        ttk::style element create Horizontal.Scale.trough \
            image [list $I(trough-horizontal-active) disabled $I(trough-horizontal)] \
            -border {8 5 8 5} -padding 0
        ttk::style element create Horizontal.Scale.slider \
            image [list $I(slider) disabled $I(slider-insensitive) active $I(slider-prelight)] \
            -sticky {}

        ttk::style element create Vertical.Scale.trough \
            image [list $I(trough-vertical-active) disabled $I(trough-vertical)] \
            -border {5 8 5 8} -padding 0
        ttk::style element create Vertical.Scale.slider \
            image [list $I(slider) disabled $I(slider-insensitive) active $I(slider-prelight)] \
            -sticky {}

        ttk::style element create Entry.field \
            image [list $I(entry-border-bg-solid) \
                        focus $I(entry-border-active-bg-solid) \
                        disabled $I(entry-border-disabled-bg)] \
            -border 3 -padding {6 4} -sticky news

        ttk::style element create Labelframe.border image $I(labelframe) \
            -border 4 -padding 4 -sticky news

        ttk::style element create Menubutton.button \
            image [list $I(button) \
                        pressed  $I(button-active) \
                        active   $I(button-hover) \
                        disabled $I(button-insensitive) \
            ] -sticky news -border 3 -padding {3 2}
        ttk::style element create Menubutton.indicator \
            image [list $I(arrow-down) \
                        active   $I(arrow-down-prelight) \
                        pressed  $I(arrow-down-prelight) \
                        disabled $I(arrow-down-insens) \
            ] -sticky e -width 20

        ttk::style element create Combobox.field \
            image [list $I(combo-entry) \
                {readonly disabled}  $I(button-insensitive) \
                {readonly pressed}   $I(button-active) \
                {readonly focus}     $I(button-focus) \
                {readonly hover}     $I(button-hover) \
                readonly             $I(button) \
                {disabled} $I(combo-entry-insensitive) \
                {focus}    $I(combo-entry-focus) \
                {hover}    $I(combo-entry) \
            ] -border 4 -padding {6 0 0 0}
        ttk::style element create Combobox.downarrow \
            image [list $I(combo-entry-button) \
                        pressed   $I(combo-entry-button-active) \
                        active    $I(combo-entry-button-hover) \
                        disabled  $I(combo-entry-button-insensitive) \
          ] -border 4 -padding {0 10 6 10}
        ttk::style element create Combobox.arrow \
            image [list $I(arrow-down) \
                        active    $I(arrow-down-prelight) \
                        pressed   $I(arrow-down-prelight) \
                        disabled  $I(arrow-down-insens) \
          ]  -sticky e -width 15

        ttk::style element create Spinbox.field \
            image [list $I(combo-entry) focus $I(combo-entry-focus)] \
            -border 4 -padding {6 0 0 0} -sticky news
        ttk::style element create Spinbox.uparrow \
            image [list $I(up-background) \
                        pressed   $I(up-background-active) \
                        active    $I(up-background-hover) \
                        disabled  $I(up-background-disable) \
            ] -width 20 -border {0 2 3 0} -padding {0 5 6 2}
        ttk::style element create Spinbox.symuparrow \
            image [list $I(arrow-up-small) \
                        active    $I(arrow-up-small-prelight) \
                        pressed   $I(arrow-up-small-prelight) \
                        disabled  $I(arrow-up-small-insens) \
            ]
        ttk::style element create Spinbox.downarrow \
            image [list $I(down-background) \
                        pressed   $I(down-background-active) \
                        active    $I(down-background-hover) \
                        disabled  $I(down-background-disable) \
            ] -width 20 -border {0 0 3 2} -padding {0 2 6 5}
        ttk::style element create Spinbox.symdownarrow \
            image [list $I(arrow-down-small) \
                        active    $I(arrow-down-small-prelight) \
                        pressed   $I(arrow-down-small-prelight) \
                        disabled  $I(arrow-down-small-insens) \
          ]

        ttk::style element create Notebook.client \
            image $I(notebook) -border 1
        ttk::style element create Notebook.tab \
            image [list $I(tab-top) \
                        selected    $I(tab-top-active) \
                        active      $I(tab-top-hover) \
            ] -padding {0 2 0 0} -border 2

        ttk::style element create Horizontal.Progressbar.trough \
            image $I(trough-progressbar_v) -border {5 1 5 1} -padding 1
        ttk::style element create Horizontal.Progressbar.pbar \
            image $I(progressbar_v) -border {4 0 4 0}

        ttk::style element create Vertical.Progressbar.trough \
            image $I(trough-progressbar) -border {1 5 1 5} -padding 1
        ttk::style element create Vertical.Progressbar.pbar \
            image $I(progressbar) -border {0 4 0 4}

        ttk::style element create Treeview.field \
            image $I(treeview) -border 1
        ttk::style element create Treeheading.cell \
            image [list $I(notebook) pressed $I(notebook)] \
            -border 1 -padding 4 -sticky ewns

        ttk::style element create Treeitem.indicator \
            image [list $I(plus) user2 $I(empty) user1 $I(minus)] \
            -width 15 -sticky w

        #ttk::style element create Separator.separator image $I()

        #
        # Settings:
        #

        ttk::style configure TButton -padding {8 4 8 4} -width -10 -anchor center
        ttk::style configure TMenubutton -padding {8 4 4 4}
        ttk::style configure Toolbutton -anchor center
        ttk::style map TCheckbutton -background [list active $colors(-checklight)]
        ttk::style configure TCheckbutton -padding 3
        ttk::style map TRadiobutton -background [list active $colors(-checklight)]
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

variable version 0.1
package provide ttk::theme::arc $version

