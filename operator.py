import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import EnumProperty
from .layeredpsdmaterial import setPSDLayerConfigs

def addPlane(filename,psd) : 
  w, h = psd.size
  max_size = max(psd.size)
  # 平面を追加
  # フォルダごとにカスタムプロパティを追加する
  bpy.ops.mesh.primitive_plane_add()
  bpy.ops.transform.resize(value=((w/max_size, h/max_size,0)))
  bpy.context.view_layer.objects.active.name = filename
  return bpy.context.view_layer.objects.active

# 作るもの:
# 1.psdファイルを平面としてimportするOperator
# 2.psdファイル読み込みを行うOperator(1.とまとめられるかも?テクスチャ変えたら縦横比変わる)
class LAYEREDPSDMATERIAL_OT_importer(bpy.types.Operator, ImportHelper):
  """psdファイルを開き、平面に対して割り当てする"""
  bl_idname = "layeredpsdmaterial.importer"
  bl_label = "Import PSD As Plane"
  bl_description = "PSDファイルを取り込み"
  bl_options = {'REGISTER', 'UNDO'}

  filename_ext = ".psd"

  psdLayerNameEncoding: EnumProperty(items=[
    ('macroman','default',""),
    ('shift_jis','shift_jis',"")
    ],
    default='macroman'
  )

  # メニューを実行したときに呼ばれるメソッド
  def execute(self, context):
    active_obj = context.object
    active_obj.psd_settings.filePath = self.filepath
    active_obj.psd_settings.psdLayerNameEncoding = self.psdLayerNameEncoding
    setPSDLayerConfigs(self, context)

    return {'FINISHED'}

def menu_func_import(self, context):
  self.layout.operator(LAYEREDPSDMATERIAL_OT_importer.bl_idname, text="Import PSD as Plane", icon="TEXTURE")
