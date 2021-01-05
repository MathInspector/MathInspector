if {[file isdirectory [file join $dir radiance]]} {
    if {![catch {package require Ttk}]} {
        package ifneeded ttk::theme::radiance 0.1 \
            [list source [file join $dir radiance8.5.tcl]]
    } elseif {![catch {package require tile}]} {
        package ifneeded tile::theme::radiance 0.1 \
            [list source [file join $dir radiance8.4.tcl]]
    } else {
	return
    }
}

