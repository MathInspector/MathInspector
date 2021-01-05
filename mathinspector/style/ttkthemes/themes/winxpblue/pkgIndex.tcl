if {![file isdirectory [file join $dir winxpblue]]} { return }
if {![package vsatisfies [package provide Tcl] 8.4]} { return }

package ifneeded ttk::theme::winxpblue 0.6 \
    [list source [file join $dir winxpblue.tcl]]
