# Author: RedFantom
# License: GNU GPLv3
# Copyright (c) 2017-2018 RedFantom

set base_theme_dir [file join [pwd] [file dirname [info script]]]

array set base_themes {
  aquativo 0.0.1
  black 0.1
  blue 0.7
  clearlooks 0.1
  elegance 0.1
  itft1 0.14
  keramik 0.6.2
  kroc 0.0.1
  plastik 0.6.2
  radiance 0.1
  smog 0.1.1
  winxpblue 0.6
}

foreach {theme version} [array get base_themes] {
  package ifneeded ttk::theme::$theme $version \
    [list source [file join $base_theme_dir $theme $theme.tcl]]
}
