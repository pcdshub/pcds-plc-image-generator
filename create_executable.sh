#!/bin/bash

export VERSION=3

pyinstaller console.py --console --onefile -n cx5xxx_pcds_imager_v${VERSION} --add-data src:src
pyinstaller gui.py --console --onefile -n cx5xxx_pcds_imager_gui_v${VERSION} --add-data src:src
