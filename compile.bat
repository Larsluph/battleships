pyinstaller -F -i icon.ico --distpath .\compiled main.py

rmdir /S /Q build
rmdir /S /Q __pycache__
del main.spec
xcopy /E /C /Y /I .\locales\ .\compiled\locales\
