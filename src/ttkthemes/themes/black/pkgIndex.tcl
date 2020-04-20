# if { [catch {package require tile 0.8 }] != 0 } { return }

if {[file isdirectory [file join $dir black]]} {
    package ifneeded ttk::theme::black 0.0.1 \
        [list source [file join $dir black.tcl]]
}
