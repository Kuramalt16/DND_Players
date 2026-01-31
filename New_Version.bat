setlocal enabledelayedexpansion
if exist "build/Password" (
    rmdir /s /q "build/Password"
)
if exist "Password.spec" (
    del "Password.spec"
)
if exist "v.txt" (
    set /p number=<v.txt
)else (
    set number=0
)
set /a number+=1
echo !number! > v.txt
echo New version: !number!

pyinstaller --onefile --icon="Images/DND_Icon.ico" --hidden-import=pkg_resources.extern  Password.py
move "dist\Password.exe" ".\"
