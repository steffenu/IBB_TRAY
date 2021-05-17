application_title = "IBB Tray" # Use your own application name
main_python_file = "app.py" # Your python script
files = ['images' ,'sounds' , 'config.ini'] # include folder ... can also include isngle file use full path

import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includes = ["atexit","re"]

setup(
    name = application_title,
    version = "0.6",
    description = "Stundenplan der IBB US",
    options = {"build_exe" : {"includes" : includes , 'include_files':files }},
    executables = [Executable(main_python_file, base = base ,shortcutDir="DesktopFolder",shortcutName="ibb_tray")])

