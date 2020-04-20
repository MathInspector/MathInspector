# @TODO get rid of silly hack with cp and mkdir
all:
	@rm -rf build/ -rf dist/;
	@echo "Building...";
	@pyinstaller -y mathinspector.spec;
		
	@cp -r assets/ dist/mathinspector.app/Contents/Resources/assets;
	@cp src/settings/settings.json data/;
	@cp -r data/ dist/mathinspector.app/Contents/Resources/data;
	@cp -r /Library/Frameworks/Python.framework/Versions/3.7/lib/tcl8 dist/mathinspector.app/Contents/MacOS;

	@echo "Done!";
