if {![file isdirectory [file join $dir plastik]]} { return }
if {![package vsatisfies [package provide Tcl] 8.4]} { return }

package ifneeded ttk::theme::plastik 0.6.2 \
    [list source [file join $dir plastik.tcl]]

