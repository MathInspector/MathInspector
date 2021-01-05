# kroc - Copyright (C) 2004 David Zolli <kroc@kroc.tk>
# Available under the BSD-like 2-clause Tcl License as described in LICENSE in this folder
namespace eval ttk::kroc {
    
    package provide ttk::theme::kroc 0.0.1
    
    set imgdir [file join [file dirname [info script]] kroc]

    proc LoadImages {imgdir} {
        variable Images
        foreach file [glob -directory $imgdir *.gif] {
            set img [file tail [file rootname $file]]
            set Images($img) [image create photo -file $file -format gif89]
        }
    }
    array set Images [LoadImages $imgdir]
    set TNoteBook_Tab TNotebook.Tab
    
    ::ttk::style theme create kroc -parent alt -settings {
        
        ::ttk::style configure . -background #FCB64F -troughcolor #F8C278 -borderwidth 1
	    ::ttk::style configure . -font TkDefaultFont -borderwidth 1
        ::ttk::style map . -background [list active #694418]
        ::ttk::style map . -foreground [list disabled #B2B2B2 active #FFE7CB]
        ::ttk::style map Treeview \
            -background [list selected #000000] \
            -foreground [list selected #ffffff]
        ::ttk::style configure Treeview -fieldbackground #FFE7CB
        
        ::ttk::style configure TButton -padding "10 4"
        
        ::ttk::style configure $TNoteBook_Tab -padding {10 3} -font TkDefaultFont
        ::ttk::style map $TNoteBook_Tab \
                -background [list selected #FCB64F {} #FFE6BA] \
                -foreground [list {} black] \
                -padding [list selected {10 6 10 3}]

        ::ttk::style map TScrollbar \
		    -background	{ pressed #694418} \
                    -arrowcolor	{ pressed #FFE7CB } \
                    -relief		{ pressed sunken } \
                    ;
        
        ::ttk::style layout Vertical.TScrollbar {
            Scrollbar.trough -children {
                Scrollbar.uparrow -side top
                Scrollbar.downarrow -side bottom
                Scrollbar.uparrow -side bottom
                Scrollbar.thumb -side top -expand true
            }
        }
        
        ::ttk::style layout Horizontal.TScrollbar {
            Scrollbar.trough -children {
                Scrollbar.leftarrow -side left
                Scrollbar.rightarrow -side right
                Scrollbar.leftarrow -side right
                Scrollbar.thumb -side left -expand true
            }
        }
        
        #
        # Elements:
        #
        ::ttk::style element create Button.button image [list  \
                $Images(button-n) \
                pressed		$Images(button-p) \
                active		$Images(button-h) \
                ] -border 3 -sticky ew
        
        ::ttk::style element create Checkbutton.indicator image [list \
                $Images(check-nu) \
                {pressed selected}	$Images(check-nc) \
                pressed		$Images(check-nu) \
                {active selected}	$Images(check-hc) \
                active		$Images(check-hu) \
                selected		$Images(check-nc) \
                ] -sticky w
        
        ::ttk::style element create Radiobutton.indicator image [list \
                $Images(radio-nu) \
                {pressed selected}	$Images(radio-nc) \
                pressed		$Images(radio-nu) \
                {active selected}	$Images(radio-hc) \
                active		$Images(radio-hu) \
                selected		$Images(radio-nc) \
                ] -sticky w

        #
        # Settings: (*button.background is not needed in tile 0.5 or above)
        #
        ::ttk::style layout TButton {
	        Button.button -children {
		        Button.focus -children {
		            Button.padding -children {
			        Button.label -expand true -sticky {}
		            }
		        }
	        }
        }

        ::ttk::style layout TCheckbutton {
	    Checkbutton.border -children {
		Checkbutton.background
		Checkbutton.padding -children {
		    Checkbutton.indicator -side left
		    Checkbutton.focus -side left -children {
			Checkbutton.label
		    }
		}
            }
        }
        
        ::ttk::style layout TRadiobutton {
            Radiobutton.border -children {
                Radiobutton.background
                Radiobutton.padding -children  {
                    Radiobutton.indicator -side left
                    Radiobutton.focus -expand true -sticky w -children {
                        Radiobutton.label -side right -expand true
                    }
                }
            }
        }
        
    } 
}


