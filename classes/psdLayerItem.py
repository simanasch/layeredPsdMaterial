import bpy
from bpy.props import StringProperty
# from .utils.psd import *


class psdLayerItem(bpy.types.PropertyGroup):
  """psdファイル内の各layer階層の名前を持たせるためのクラス"""
  bl_idname = "layeredpsdmaterial.psd_layer_item"
  bl_label = "psdLayerItem"

  name:StringProperty()