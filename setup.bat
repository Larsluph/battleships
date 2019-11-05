pyinstaller -F -i icon.ico --distpath compiled main.py

rmdir /S /Q build
rmdir /S /Q custom_module
del main.spec

copy battleships.config compiled\battleships.config