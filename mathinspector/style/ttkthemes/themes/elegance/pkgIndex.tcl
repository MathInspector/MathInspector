if {[file isdirectory [file join $dir elegance]]} {
    package ifneeded ttk::theme::elegance 0.1 \
        [list source [file join $dir elegance.tcl]]
}
