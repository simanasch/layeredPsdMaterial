'''
Copyright (C) 2022 simana
tktossi@live.com

Created by simana

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
  "name": "layered PSD Material",
  "author": "simana",
  "version": (0, 0, 1),
  "blender": (2, 93, 3),
  "location": "Object",
  "description": "import and use layered PSD as Material",
  "warning": "",
  "doc_url": "",
  "tracker_url": "",
  "category": "Object",
}

# "reload Script"でスクリプトを再読み込みした場合に関連ファイルを再読み込みする
if "bpy" in locals():
  import importlib
  reloadables = [
    "psd",
    "handler",
    "classes",
    "operator",
    "ui"
  ]
  for mod in reloadables:
    if mod in locals():
      importlib.reload(locals()[mod])

import bpy
from . import auto_load

auto_load.init()

#
# アドオン有効化時の処理
#
def register():
  auto_load.register()

  from .handler import onFrameChangePost
  from .operators.operator import menu_func_import
  from .classes import psd_OT_Settings
  bpy.types.Object.psd_settings = bpy.props.PointerProperty(type=psd_OT_Settings)
  bpy.app.handlers.frame_change_post.append(onFrameChangePost)
  bpy.types.VIEW3D_MT_image_add.append(menu_func_import)

#
# アドオン無効化時の処理
# 
def unregister():
  auto_load.unregister()
  from .handler import onFrameChangePost
  from .operators.operator import menu_func_import
  bpy.app.handlers.frame_change_post.remove(onFrameChangePost)
  bpy.types.VIEW3D_MT_image_add.remove(menu_func_import)
