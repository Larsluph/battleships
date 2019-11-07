mkdir custom_module
copy %~d0\Dev\Applications\Python38\Lib\custom_module\* .\custom_module

pyinstaller -F -i icon.ico --distpath ./compiled main.py

rmdir /S /Q build
rmdir /S /Q custom_module
del main.spec

copy battleships.config compiled\battleships.config