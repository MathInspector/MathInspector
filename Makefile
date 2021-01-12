all:
	@rm -rf build/ -rf dist/;
	@echo "Building...";
	@pyinstaller -y mathinspector.spec;
		
	@cp -r assets/ dist/mathinspector.app/Contents/Resources/assets;
	@cp -r /Library/Frameworks/Python.framework/Versions/3.7/lib/tcl8 dist/mathinspector.app/Contents/MacOS;

	@echo "Done!";
