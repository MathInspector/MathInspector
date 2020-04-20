#TODO
- organize this file

#BUG
- "not managed by notebook" error when no tab is open ( just make it open a tab obv )
	* this hasnt happened in awhile and not sure how to reproduce yet
- gridlines not showing up when click on graph (minor)

#REFACTOR
- a bunch of clean up is going to need to happen, i have been getting things to work and leaving a few messes

#EDITOR
- expose a logging function so functions in mathinspector can call log() and see it appear in the console or workspace

(going to abandon the editor i think, its really not a great idea)
- add breakpoint system to editor using (`from pdb import set_trace as bp`)
- autocomplete
- find/replace
- multiselect
- ctrl+tab
- move line
- i should make it work with an external editor and remove the built in editor. instead use a watch system


#DOCVIEWER
- do style for non FunctionDoc docs
- checkout polynomial -> hermite
	* words in `tilde` should be bold -- should be line

#MODULES
- ability to import valid modules from system using import command from prompt
	* will need to specify correct path on file system but should work actually
	* can set include file path in settings.json
	* need to specify version of python for build in about section
	* automatically detect if correct version of python is installed on system, if possible, then set include path automatically

#OUTPUT
- create systems for different type of visualizations, including color maps for complex functions, and the other thing I saw on 3blue1brown about function domains
- show image files in output when selected in projecttree

#MENU
- get about section working, specify python build its based on
- options/hotkeys for switching to each view (like numbers)
- options/hotkeys for maximizing/minizing each view

#WORKSPACE
- slider functionality for numbers (int and float)
	* make this built in to the widget if its int or float by default
- confirm dialog on delete
- show output value of fn inside block element as well as in output panel (which has visualizations)
- fix outline of connected circuit color when have 3 blocks connected in a row
	* if first 2 are connected, then when connecting 2 to 3 dont change color of 2
- undo/redo functionality

#SAVE DATA
- when bad data is auto-saved and program is quit, if error on restart when loading savedata then erase prev savedata and 

#DOCVIEWER
- when click on links to other docs, jump (open folder if necc) and select that same thing in moduletree
- make :ref: links work 
- render TeX
- sympy docs have render issues (spacing btwn multiple lines, code examples on same line)
	* see Sympy => geometry => ellipse => S
- better style for builtin's docs

#CONSOLE
- errors from workspace connections failing shows as black but should be red

#OBJECT TREE
- allow changing of variable names

#WEBSITE
- create a subdomain docs.mathinspector.com which will be the home for the documentation
	* use sphinx for this, see /Projects/sphinx-test for an example
	* have 2 kinds of documentation, for end-users and for contributors

#TODO
- icons for imported modules
- add kwargs to fn's
- set up inotify (pynotify?)
- give minimum width to treeviews and have them snap open/closed (also jump x coord of mouse)
- get savedata to work on build from /data dir
- allow workspace elements to connect with multiple wires out (why not right, drag from output to create more)
- enable mathinspector to open files of type .math
- refactor font system to use settings and have color, size, and type as options
- better system for showing errors on canvas connections and value edits (make a "toast" type message appear in bottom of workspace in red letters)
- pretty print the items inside (esp dict and list) of the objects and shorten with ... if too long and show in object inspector and apply the very same syntax highlighting as in pycode
- create systems for different type of visualizations, including color maps for complex functions, and the other thing I saw on 3blue1brown about function domains
- create some kind of documentation for MathStation and have that imported as default along with numpy
- make MathStation module which contains useful classes and functions for working with the interface
- set up virtual env so that build does not depend at all on system python version
- explore possability of including widgets for if and loop statements
- look into cutting out ttkthemes if possible
- use transparent image with label to give tabs rounded corners and not overlap too much

# COMMENTS/DOCUMENTATION
- add comment docstrings to all views/widgets to explain how it works/what they are doing (this is impt for releasing an open source project)
- use documentation generator Sphinx to create online documentation like pyton docs are
- make MathStation module which contains useful classes and functions for working with the interface


# BUILD PROCESS
- package fonts with build
- clean up imports and make sure only important required modules
- use virtualenv to prevent version conflicts during dev
- have list of modules to import so can be accessed during built program

# MISC
- fix builtins.int example code, needs to be on own line
- deal with doc_link's which have . in them (this means in a different module, possibly numpy. implied or not)
- deal with ::version added.. 
- show TeX for math
- using  arrow keys to browse methods does not leave anything highlighted like on projecttree
- ability to set fn arg values in objecttree
- vary contextmenu based on item click, e.g. for values can have set value option (also just on click allow edit)
- ability to edit, incl edit args to functions
- highlight value same way as everywhere, incl red for module + class name
- make the output of fn's show on the widget when they have an output
- system for changing values of numbers (both val and argval) by holding down btn1 and dragging (for int/float use raw distance, for complex use x,y coords)
- dont allow multiple input to same node
