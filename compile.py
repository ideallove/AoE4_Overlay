"""
# Description:  This manages compiling the app with Nuitka and packaging it into a zip file.
# 这个文件用于管理使用 Nuitka 编译程序并将其打包成 zip 文件。
# Usage: python compile.py
"""
# -*- coding: UTF-8 -*-
import os
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

# Run nuitka
os.system('cmd /c "python -m nuitka'
          ' --plugin-enable=pyside6'
          ' --standalone --debug --show-progress --show-modules --enable-console'
          ' --windows-icon-from-ico=src/img/aoe4_sword_shield.ico'
          ' --include-data-dir=src/img=img'
          ' --include-data-dir=src/html=html'
          ' src/AoE4_overlay.py')

# Zip
file_name = f"AoE4_overlay.zip"

to_zip = []
folder = 'AoE4_overlay.dist'
for root, directories, files in os.walk(folder):
    for f in files:
        to_zip.append(os.path.join(root, f))

print('Compressing files...')
with ZipFile(file_name, 'w', compression=ZIP_DEFLATED) as zip:
    for f in to_zip:
        if "custom.js" in f or "custom.css" in f:
            continue
        zip.write(f, f"AoE4_Overlay/{f[len(folder) + 1:]}")

# Cleanup
# for item in (folder, ):
#     if os.path.isdir(item):
#         shutil.rmtree(item)
