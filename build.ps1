# Gera dist\whatwhale.exe (arquivo único) com PyInstaller.
python -m pip install --quiet pyinstaller
python -m PyInstaller --onefile --clean --name whatwhale whatwhale.py
if ($?) { Write-Host "OK: dist\whatwhale.exe" }
