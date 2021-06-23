@echo on

pyinstaller create.py --console --onefile -n cx5xxx_pcds_imager
del /q /s dist\src
xcopy /Y /S src dist\src
xcopy /Y CB*.zip dist
