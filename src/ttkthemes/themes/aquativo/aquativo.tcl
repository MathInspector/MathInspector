# aquativo - Copyright (C) 2004 Pat Thoyts <patthoyts@users.sourceforge.net>
# Available under the BSD-like 2-clause Tcl License as described in LICENSE in this folder

package require Tk 8.4;                 # minimum version for Tile
package require tile 0.8;               # depends upon tile

namespace eval ttk {
  namespace eval theme {
    namespace eval aquativo {
      variable version 0.0.1
    }
  }
}

# TkDefaultFont", "TkTextFont" and "TkMenuFont
#   font create System {*}[font actual System] 
#   font configure System -size 16 -weight bold


namespace eval ttk::theme::aquativo {

  variable I

  set thisDir  [file dirname [info script]]
  set imageDir [file join $thisDir "images"]
  set imageLib [file join $thisDir "ImageLib.tcl"] \

  # try to load image library file...
  if { [file exists $imageLib] } {

      source $imageLib
      array set I [array get images]

  } else {

      proc LoadImages {imgdir {patterns {*.gif}}} {
        foreach pattern $patterns {
          foreach file [glob -directory $imgdir $pattern] {
            set img [file tail [file rootname $file]]
            if {![info exists images($img)]} {
              set images($img) [image create photo -file $file]
            }
        }}
        return [array get images]
      }

      array set I [LoadImages $imageDir "*.gif"]
  }

  
  # "-parent" option controls the treeview "+" icon (collapse/expand)
  # at the beginning of each tree node
  
  ::ttk::style theme create aquativo -settings {
    
    # Defaults
    
    ::ttk::style configure "." \
        -font TkDefaultFont \
        -background "#fafafa" \
        -foreground "Black"
    
    # I really like the mapping options!
    ::ttk::style map "." \
        -foreground { disabled "#565248" } \
        -background { \
	    disabled "#e3e1dd"
            pressed  "#bab5ab"
            active   "#c1d2ee" }
        
    # Troughs

    ::ttk::style element create Horizontal.Scale.trough \
        image $I(horizontal_trough) -border 0

    ::ttk::style element create Vertical.Scale.trough \
        image $I(vertical_trough) -border 0

    ::ttk::style element create Progress.trough \
        image $I(vertical_trough) -border 0

    # Panedwindow parts

    ::ttk::style element create hsash \
            image $I(hseparator) -border {2 0}
    ::ttk::style element create vsash \
            image $I(vseparator) -border {0 2}

    # Buttons, Checkbuttons and Radiobuttons
    
    ::ttk::style layout TButton {
      Button.background
      Button.button -children {
        Button.focus -children {
          Button.label
        }
      }
    }
    
    ::ttk::style element create Button.button image \
        [list $I(buttonNorm) \
	      pressed $I(buttonPressed) active $I(buttonPressed)] \
        -border {4 4} -padding 3 -sticky nsew
    
    ::ttk::style element create Checkbutton.indicator image \
        [list $I(checkbox_unchecked) selected $I(checkbox_checked)] \
        -width 20 -sticky w
    ::ttk::style element create Radiobutton.indicator image \
        [list $I(option_out) selected $I(option_in)] \
        -width 20 -sticky w
    
    # Menubuttons
    
    ::ttk::style element create Menubutton.button image \
        [list $I(menubar_option) ] \
        -border {7 10 29 15} -padding {7 4 29 4} -sticky news
    
    ::ttk::style element create Menubutton.indicator image \
        [list $I(menubar_option_arrow) \
	      disabled $I(menubar_option_arrow_insensitive)] \
        -width 11 -sticky w -padding {0 0 18 0}
    
    # Scrollbar

    ::ttk::style element create Horizontal.Scrollbar.trough \
        image $I(horizontal_trough) -width 16 -border 0 -sticky ew

    ::ttk::style element create Vertical.Scrollbar.trough \
        image $I(vertical_trough) -height 16 -border 0 -sticky ns

    ::ttk::style element create Horizontal.Scrollbar.thumb \
        image [list $I(scrollbar_horizontal) \
	            {active !disabled} $I(scrollbar_horizontal) \
		    disabled  $I(horizontal_trough)] \
        -border 7 -width 16 -height 0 -sticky nsew

    ::ttk::style element create Vertical.Scrollbar.thumb \
        image [list $I(scrollbar_vertical) \
	            {active !disabled}  $I(scrollbar_vertical) \
		    disabled $I(vertical_trough)] \
 	-border 7 -width 0 -height 16 -sticky nsew
    
    # Scale
    
    ::ttk::style element create Horizontal.Scale.slider \
        image $I(scrollbar_horizontal) \
        -border 3 -width 30 -height 16
    
    ::ttk::style element create Vertical.Scale.slider \
        image $I(scrollbar_vertical) \
        -border 3 -width 16 -height 30
    
    # Progress
    
    ::ttk::style element create Progress.bar image $I(progressbar)
    
    # Arrows
    
    ::ttk::style element create uparrow image \
        [list $I(arrow_up_normal) \
              pressed $I(arrow_up_active) \
              disabled $I(arrow_up_insensitive)] -width 12
    ::ttk::style element create downarrow image \
        [list $I(arrow_down_normal) \
              pressed $I(arrow_down_active) \
              disabled $I(arrow_down_insensitive)] -width 12
    ::ttk::style element create leftarrow image \
        [list $I(arrow_left_normal) \
              pressed $I(arrow_left_active) \
              disabled $I(arrow_left_insensitive)] -height 12
    ::ttk::style element create rightarrow image \
        [list $I(arrow_right_normal) \
              pressed $I(arrow_right_active) \
              disabled $I(arrow_right_insensitive)] -height 12
    
    # Notebook parts
    
    ::ttk::style element create tab image \
        [list $I(notebook) selected $I(notebook_active) \
                           active   $I(notebook_inactive) \
                           disabled $I(notebook_inactive)] \
        -sticky news \
        -border {10 2 10 2} -height 10
    
    ::ttk::style configure TNotebook.Tab -padding {2 2}
    ::ttk::style configure TNotebook -expandtab {2 2}
    
    
    # Labelframes
    
    ::ttk::style configure TLabelframe -borderwidth 2 -relief groove

    # Treeview
    ::ttk::style map Treeview \
        -background [list selected #85cafc] \
        -foreground [list selected #000000]
  }
}

namespace eval ::tablelist:: {

    proc aquativoTheme {} {
      variable themeDefaults
      array set themeDefaults [list \
	-background		white \
	-foreground		black \
	-disabledforeground	black \
	-stripebackground	#EDF3FE \
	-selectbackground	#000000 \
	-selectforeground	#ffffff \
	-selectborderwidth	0 \
	-font			TkTextFont \
        -labelbackground	#fafafa \
	-labeldisabledBg	#fafafa \
	-labelactiveBg		#fafafa \
	-labelpressedBg		#fafafa \
	-labelforeground	black \
	-labeldisabledFg	black \
	-labelactiveFg		black \
	-labelpressedFg		black \
	-labelfont		TkDefaultFont \
	-labelborderwidth	2 \
	-labelpady		1 \
	-arrowcolor		#777777 \
	-arrowstyle		flat7x7 \
	-showseparators         yes \
      ]
   }
}


package provide ttk::theme::aquativo $::ttk::theme::aquativo::version
