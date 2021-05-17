pyinstaller --onefile --noconsole  app.py


create exe with additional data folders :
https://github.com/smoqadam/PyFladesk
https://elc.github.io/posts/executable-flask-pyinstaller/





F - Bundles everything in a single file
w - Avoid displaying a console
--add-data - Add Folders to the directory/executable
Since Flask relies on a directory structure you should pass it to the folder, in the example case we only have two folders: templates and static, in case you use a database or some other directory structure you should adapt this.

Note: For more complex scenarios check the PyInstaller Docs

If we want everything in one executable file we can

Windows:

pyinstaller -w -F --add-data "templates;templates" --add-data "static;static" app.py

Linux:

pyinstaller -w -F --add-data "templates:templates" --add-data "static:static" app.py

Depending on the Linux version, you might need to install sudo apt install libpython3.x-dev

This will create a folder dist with our executable ready to be shipped. The executable will open the main window of our app.