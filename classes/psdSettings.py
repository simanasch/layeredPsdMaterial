import bpy
from bpy.props import StringProperty,EnumProperty,CollectionProperty,BoolProperty
from .psdLayerSettings import psdLayerSettings

class psd_OT_Settings(bpy.types.PropertyGroup):
  bl_idname = "layeredpsdmaterial.psd_settings"
  bl_label = "psdMaterialProperties"
  bl_options = {'REGISTER', 'UNDO'}

  # props
  filePath: StringProperty(subtype="FILE_PATH",description="psdファイルのパス")
  psdLayerNameEncoding: EnumProperty(items=[
      ('macroman','default',""),
      ('shift_jis','shift_jis',"")
    ],
    default='macroman',
    description="psdファイル内のレイヤー名のエンコード、文字化けする場合は変更してください"
  )
  layerSettings: CollectionProperty(type=psdLayerSettings)
  isFlipped: BoolProperty(description="左右反転の有無")

