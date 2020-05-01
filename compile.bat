mkdir custom_module
copy %~d0\Dev\Applications\Python38\Lib\site-packages\custom_module\* .\custom_module

pyinstaller -F --distpath ./compiled main.py

rmdir /S /Q build
rmdir /S /Q custom_module
del main.spec
