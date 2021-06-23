@echo on

pyinstaller create.py --console --onefile -n cx5xxx_pcds_imager --add-data src;src --add-binary CBxx63_WEC7_HPS_v608g_TC31_B4024.10.zip;.
