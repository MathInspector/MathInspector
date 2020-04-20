if {[file isdirectory [file join $dir advanced]]} {
    package ifneeded ttk::theme::advanced 1.0 \
        [list source [file join $dir advanced.tcl]]
}
