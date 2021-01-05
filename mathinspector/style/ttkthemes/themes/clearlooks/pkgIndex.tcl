if {[file isdirectory [file join $dir clearlooks]]} {
    if {![catch {package require Ttk}]} {
        package ifneeded ttk::theme::clearlooks 0.1 \
            [list source [file join $dir clearlooks8.5.tcl]]
    } elseif {![catch {package require tile}]} {
        package ifneeded tile::theme::clearlooks 0.1 \
            [list source [file join $dir clearlooks8.4.tcl]]
    } else {
	return
    }
}

