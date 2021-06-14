# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\sebas\\Buoy-Mapper\\hydro_p_LakeSuperior', '.\\hydro_p_LakeSuperior')]
binaries = [('C:\\Users\\sebas\\anaconda3\\Library\\bin\\spatialindex_c-64.dll', '.\\Library\\bin'), ('C:\\Users\\sebas\\anaconda3\\Library\\bin\\spatialindex-64.dll', '.\\Library\\bin'),
('C:\\Users\\sebas\\anaconda3\\Library\\bin\\spatialindex_c-64.dll', '.\\rtree'), ('C:\\Users\\sebas\\anaconda3\\Library\\bin\\spatialindex-64.dll', '.\\rtree')]
hiddenimports = [ 'fiona', 'gdal', 'shapely', 'shapely.geometry', 'pyproj', 'rtree', 'geopandas.datasets', 'pytest', 'pandas._libs.tslibs.timedeltas', 'fiona._shim']
tmp_ret = collect_all('geopandas')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rtree')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('fiona')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


block_cipher = None


a = Analysis(['..\\Buoy-Mapper\\buoyMapperGUI.py'],
             pathex=['C:\\Users\\sebas'],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='buoyMapperGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='buoyMapperGUI')
