mkdir custom_module
copy %~d0\Dev\Applications\Python38\Lib\custom_module\* .\custom_module

python pyinstaller -F --distpath ./compiled main.py

rmdir /S /Q build
rmdir /S /Q custom_module
del main.spec

copy battleships.save compiled\battleships.save
