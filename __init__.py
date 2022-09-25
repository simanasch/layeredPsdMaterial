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

import bpy
from . import layeredPsdMaterial
from . import ui

#
# register classs
#
classes = [
  layeredPsdMaterial.psdLayerItem,
  layeredPsdMaterial.psdLayerSettings,
  layeredPsdMaterial.psd_OT_Settings,
  ui.psdMaterial_PT_uiPanel
]

#
# register
#
def register():
  for c in classes:
    bpy.utils.register_class(c)
  bpy.types.Object.psd_settings = bpy.props.PointerProperty(type=layeredPsdMaterial.psd_OT_Settings)
  bpy.app.handlers.frame_change_post.append(layeredPsdMaterial.onFrameChangePost)


#
# unregister
#        
def unregister():
  for c in classes:
    bpy.utils.unregister_class(c)
