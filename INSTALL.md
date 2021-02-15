## python module dependencies for building the executable with Make
- numpy
- scipy
- scikit-image
- cloudpickle
- pillow
- PyInstaller
- ttkthemes
- pygame
- pyglm
- watchdog
- PyOpenGL
- PyOpenGL_accelerate

$ python -m pip install numpy  scipy  scikit-image  cloudpickle  pillow  PyInstaller  ttkthemes  pygame  pyglm==2.0.0a3  watchdog  PyOpenGL  PyOpenGL_accelerate

## Make File
*MacOS only for now, in a future version the Make file will detect the platform automatically*
The style/arc.tcl file and image files in style/arc/ needs to be copied over the png/arc/arc.tcl file in the ttkthemes
on the local filesystem, before running the Make command.

## Building on Linux/Windows
$ pyinstaller mathinspector.linux.spec

or

$ pyinstaller mathinspector.win.spec

## OpenGL Error on MacOS
see the solution in this issue if OpenGL is not working on macos https://github.com/PixarAnimationStudios/USD/issues/1372

edit PyOpenGL file OpenGL/platform/ctypesloader.py, and changing the line

```fullName = util.find_library( name )```

to

```fullName = '/System/Library/Frameworks/OpenGL.framework/OpenGL'```

