# Installing on Linux/Windows/MacOS
$ python -m pip install mathinspector

or

$ git clone https://github.com/MathInspector/MathInspector
$ cd MathInspector
$ python -m pip install .

## OpenGL Error on MacOS
see the solution in this issue if OpenGL is not working on macos https://github.com/PixarAnimationStudios/USD/issues/1372

edit PyOpenGL file OpenGL/platform/ctypesloader.py, and changing the line

```fullName = util.find_library( name )```

to

```fullName = '/System/Library/Frameworks/OpenGL.framework/OpenGL'```
