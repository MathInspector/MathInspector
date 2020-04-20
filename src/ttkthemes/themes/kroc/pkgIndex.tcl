if {![file isdirectory [file join $dir kroc]]} { return }
if {![package vsatisfies [package provide Tcl] 8.4]} { return }

package ifneeded ttk::theme::kroc 0.0.1 \
    [list source [file join $dir kroc.tcl]]
