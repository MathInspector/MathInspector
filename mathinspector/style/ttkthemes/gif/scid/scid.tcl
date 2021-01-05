# scidthemes - Copyright (C) 2018 Uwe Klimmek
# Available under the BSD-like 2-clause Tcl License, see LICENSE.md

# Copyright (c) 2018 RedFantom
# Edited for indents, spaces instead of tabs and formatting
# Fixed the spacing of down arrow in Menubutton/OptionMenu
# TODO: Fix alignment of down arrow in Menubutton/OptionMenu
# TODO: Fix spacing on Combobox down arrow sides

package provide ttk::theme::scid 0.9.1

foreach { t } { blue mint green purple sand pink grey } {
    set ::tks $t

    package provide ttk::theme::scid$t 0.9.1

    namespace eval ttk::theme::scid$t {

    set t $::tks
    proc LoadImages {imgdir {patterns {*.png}}} {
        foreach pattern $patterns {
            foreach file [glob -directory $imgdir $pattern] {
                set img [file tail [file rootname $file]]
                if {![info exists images($img)]} {
                    set images($img) [image create photo -file $file -format gif]
                }
            }
        }
        return [array get images]
    }

    variable I
    array set I [LoadImages [file join [file dirname [info script]] scid$t] *.gif]

    variable colors
    array set colors {
        -frame          "#d8d8d8"
        -lighter        "#fcfcfc"
        -dark           "#c8c8c8"
        -darker         "#9e9e9e"
        -darkest        "#cacaca"
        -selectbg       "#3d3d3d"
        -selectfg       "#fcfcfc"
        -disabledfg     "#b3b3b3"
        -entryfocus     "#6f6f6f"
        -tabbg          "#c9c9c9"
        -tabborder      "#b7b7b7"
        -troughcolor    "#d7d7d7"
        -troughborder   "#a7a7a7"
        -checklight     "#f5f5f5"
        -eborder        "#5464c4"
        -foreground     "#202020"
        -background     "#efefef"
    }

    ttk::style theme create scid$t -settings {
        ttk::style configure . \
        -borderwidth        1 \
        -background         $colors(-frame) \
        -foreground         $colors(-foreground) \
        -bordercolor        $colors(-darkest) \
        -darkcolor          $colors(-dark) \
        -lightcolor         $colors(-lighter) \
        -troughcolor        $colors(-troughcolor) \
        -selectforeground   $colors(-selectfg) \
        -selectbackground   $colors(-selectbg) \
        -font               TkDefaultFont

        ttk::style map . \
            -background [list disabled $colors(-frame) active $colors(-lighter)] \
            -foreground [list disabled $colors(-disabledfg)] \
            -selectbackground [list !focus $colors(-darker)] \
            -selectforeground [list !focus white]

        ## Treeview
        ttk::style element create Treeheading.cell image \
        [list $I(tree-n) \
             selected $I(tree-p) \
             disabled $I(tree-d) \
             pressed $I(tree-p) \
             active $I(tree-h) \
            ] -border 4 -sticky ew
        ttk::style configure Row -background $colors(-background)
        ttk::style map Row -background \
            [list \
                {focus selected} "#6474d4" \
                selected "#7484e4" \
                alternate white]
        ttk::style map Item -foreground [list selected white]
        ttk::style map Cell -foreground [list selected white]
        ttk::style configure Treeview -background white
        ttk::style map Treeview \
            -background [list selected "#5464c4"] \
            -foreground [list selected $colors(-selectfg)]

        ## Buttons
        ttk::style configure TButton -anchor center
        ttk::style layout TButton {
            Button.button -children {
                Button.focus -children {
                    Button.padding -children {
                        Button.label
                    }
                }
            }
        }

        ttk::style element create button image \
            [list $I(button-n) \
                pressed $I(button-p) \
                {selected active} $I(button-pa) \
                selected $I(button-p) \
                active $I(button-a) \
                disabled $I(button-d) \
            ] -border {4 9 4 18} -padding {4 0} -sticky news
        ttk::style configure Tbutton -padding {4 0 4 0}

        ## Checkbuttons
        ttk::style element create Checkbutton.indicator image \
            [list $I(check-nu) \
                {disabled selected} $I(check-dc) \
                disabled $I(check-du) \
                {pressed selected} $I(check-pc) \
                pressed $I(check-pu) \
                {active selected} $I(check-ac) \
                active $I(check-hu) \
                selected $I(check-nc) \
            ] -width 20 -sticky w
        ttk::style map TCheckbutton -background [list active $colors(-frame)]
        ttk::style configure TCheckbutton -padding {0 4 0 4}

        ## Radiobuttons
        ttk::style element create Radiobutton.indicator image \
            [list $I(radio-nu) \
                {disabled selected} $I(radio-dc) \
                disabled $I(radio-du) \
                {pressed selected} $I(radio-pc) \
                pressed $I(radio-pu) \
                {active selected} $I(radio-ac) \
                active $I(radio-hu) \
                selected $I(radio-nc) \
            ] -width 20 -sticky w
        ttk::style map TRadiobutton -background [list active $colors(-frame)]
        ttk::style configure TRadiobutton -padding {0 4 0 4 }

        ## Menubuttons
        ttk::style element create Menubutton.indicator image \
            [list $I(menuarrow-a) \
                disabled $I(menuarrow-d) \
            ] -sticky e -border {15 0 0 0} -padding 0
        ttk::style element create Menubutton.border image \
            [list $I(button-n) \
                 selected $I(button-p) \
                 disabled $I(button-d) \
                 active $I(button-a) \
            ] -border 4 -sticky ew
        ttk::style configure TMenubutton -padding {4 0 4 0}

        ## Toolbar buttons
        ttk::style configure Toolbutton -padding -5 -relief flat
        ttk::style configure Toolbutton.label -padding 0 -relief flat
        ttk::style element create Toolbutton.border image \
            [list $I(blank) \
                pressed $I(toolbutton-p) \
                {selected active} $I(toolbutton-pa) \
                selected $I(toolbutton-p) \
                active $I(toolbutton-a) \
                disabled $I(blank) \
            ] -border 11 -sticky nsew

        ## Entry widgets
        ttk::style configure TEntry \
            -padding {0 4 0 4 } \
            -insertwidth 1 \
            -fieldbackground white \
            -selectbackground $colors(-eborder) \
            -selectforeground $colors(-foreground)
        ttk::style map TEntry \
            -fieldbackground [list readonly $colors(-frame)] \
            -bordercolor     [list focus $colors(-eborder)] \
            -lightcolor      [list focus $colors(-entryfocus)] \
            -darkcolor       [list focus $colors(-entryfocus)]
        ttk::style element create Entry.field image \
            [list $I(entry-n) \
                 {focus} $I(entry-a) \
                 {readonly disabled} $I(entry-rd) \
                 {readonly pressed} $I(entry-d) \
                 {focus readonly} $I(entry-d) \
                 readonly $I(entry-d) \
            ] -border {3 3 3 3} -sticky ew

        ## Combobox
        ttk::style element create Combobox.downarrow image \
            [list $I(comboarrow-n) \
                 focus $I(comboarrow-af) \
                 disabled $I(comboarrow-d) \
                 pressed $I(comboarrow-p) \
                 active $I(comboarrow-a) \
            ] -sticky e -border {22 0 0 0}
        ttk::style element create Combobox.field image \
            [list $I(combo-n) \
                 focus $I(combo-ra) \
                 {readonly disabled} $I(combo-rd) \
                 {readonly pressed} $I(combo-rp) \
                 {readonly focus} $I(combo-rf) \
                 readonly $I(combo-rn) \
            ] -border {4 0 0 0} -sticky ew
        ttk::style configure TCombobox \
            -selectbackground "#ffffff" \
            -selectforeground "#202020" \
            -padding {0 4 0 4}

        ## Spinbox
        ttk::style element create Spinbox.downarrow image \
            [list $I(spinarrowdown-a) \
                {focus pressed} $I(spinarrowdown-paf) \
                focus $I(spinarrowdown-af) \
                disabled $I(spinarrowdown-a) \
                active $I(spinarrowdown-p) \
            ] -border 4 -sticky {}
        ttk::style element create Spinbox.uparrow image \
            [list $I(spinarrowup-a) \
                {focus pressed} $I(spinarrowup-paf) \
                focus $I(spinarrowup-af) \
                disabled $I(spinarrowup-a) \
                active $I(spinarrowup-p) \
            ] -border 4 -sticky {}
        ttk::style element create Spinbox.field image \
            [list $I(combo-n) \
                focus $I(combo-ra) \
                {readonly disabled} $I(combo-rd) \
                {readonly pressed} $I(combo-rp) \
                {readonly focus} $I(combo-rf) \
                readonly $I(combo-rn) \
            ] -border {4 0 0 0} -sticky ew
        ttk::style configure TSpinbox \
            -selectbackground "#ffffff" \
            -selectforeground "#202020" \
             -padding {0 4 0 4}

        ## Notebooks
        ttk::style element create Notebook.client \
            image $I(surface) -border 2 -sticky news
        ttk::style element create Notebook.tab image \
            [list $I(tab-n) \
                selected $I(tab-s) \
                active $I(tab-a) \
            ] -border {3 6 3 12} -padding {3 3}

        ## Labelframes
        ttk::style element create Labelframe.border image $I(labelframe) \
            -border 4 -sticky news
        ttk::style configure TLabelframe -padding 4

        ## Scrollbars
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
        ttk::style element create Horizontal.Scrollbar.thumb image \
            [list $I(sbthumb-hn) \
                disabled $I(sbthumb-hd) \
                pressed $I(sbthumb-hp) \
                active $I(sbthumb-ha) \
            ] -border 4
        ttk::style element create Vertical.Scrollbar.thumb image \
            [list $I(sbthumb-vn) \
                disabled $I(sbthumb-vd) \
                pressed $I(sbthumb-vp) \
                active $I(sbthumb-va) \
            ] -border 4
        ttk::style element create Horizontal.Scrollbar.trough image $I(sbtrough-h)
        ttk::style element create Vertical.Scrollbar.trough image $I(sbtrough-v)
        ttk::style configure TScrollbar -bordercolor $colors(-troughborder)

        ## Scales
        ttk::style element create Horizontal.Scale.slider image \
            [list $I(scale-hn) \
                disabled $I(scale-hd) \
                active $I(scale-ha) \
            ]
        ttk::style element create Horizontal.Scale.trough image \
            [list $I(scaletrough-h) \
                pressed $I(scaletrough-hp) \
            ] -border 4 -sticky ew -padding 0
        ttk::style element create Vertical.Scale.slider image \
            [list $I(scale-vn) \
                disabled $I(scale-vd) \
                active $I(scale-va) \
            ]
        ttk::style element create Vertical.Scale.trough image \
            [list $I(scaletrough-v) \
                pressed $I(scaletrough-vp) \
            ] -border 4 -sticky ns -padding 0

        ttk::style configure TScale -bordercolor $colors(-troughborder)

        ## Progressbar
        ttk::style element create Progressbar.trough \
            image $I(entry-n) -border 2
        ttk::style element create Vertical.Progressbar.pbar \
            image $I(progress-v) -border {2 2 1 1}
        ttk::style element create Horizontal.Progressbar.pbar \
            image $I(progress-h) -border {2 2 1 1}
        ttk::style configure TProgressbar \
            -bordercolor $colors(-troughborder) \
            -foreground $colors(-eborder)

        ## Statusbar
        ttk::style element create sizegrip image $I(sizegrip)

        ## Separator
        ttk::style element create separator image $I(sep-h)
        ttk::style element create hseparator image $I(sep-h)
        ttk::style element create vseparator image $I(sep-v)

        ## Paned window
        ttk::style element create vsash image $I(sas-v) -sticky e
        ttk::style element create hsash image $I(sas-h) -sticky s
    }
    }
}
unset ::tks
