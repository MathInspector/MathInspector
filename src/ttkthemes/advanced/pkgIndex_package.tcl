set themesdir [file join [pwd] [file dirname [info script]]]
lappend auto_path $themesdir
package provide advanced 1.0
source [file join $themesdir advanced advanced.tcl]
