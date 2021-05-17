https://github.com/pyinstaller/pyinstaller/issues/3327

TO FIX create a ressource file : test.qrc

<!DOCTYPE RCC><RCC version="1.0">
<qresource prefix="/">
   <file>images/icon.png</file>
</qresource>
</RCC>

Use the following command (pyrcc3/4/5 depends on your version of pyqt) in cmd to generate a resource file:
pyrcc5 "path/test.qrc" -o test_rc.py
pyside6-rcc books.qrc > rc_books.py

Usage:
import test_rc.py
wherever you are setting the icon use this. ':/images/icon.png' is from the resource file.
self.icon = QIcon(':/images/icon.png')


pyrcc5 "path/test.qrc" -o test_rc.py