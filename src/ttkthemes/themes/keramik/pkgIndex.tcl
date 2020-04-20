if {![file isdirectory [file join $dir keramik]]} { return }
if {![package vsatisfies [package provide Tcl] 8.4]} { return }

package ifneeded ttk::theme::keramik 0.6.2 \
    [list source [file join $dir keramik.tcl]]
package ifneeded ttk::theme::keramik_alt 0.6.2 \
    [list source [file join $dir keramik.tcl]]
