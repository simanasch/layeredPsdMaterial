import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty,EnumProperty,StringProperty
from .layeredpsdmaterial import initPSDPlane, getFileNameFromPath,updatePsdViewState
from .classes import psdLayerSettings, psdLayerItem

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
    default='macroman',
    name='レイヤー名のエンコード'
  )

  addPlane: BoolProperty(
    name="平面を追加"
  )

  # メニューを実行したときに呼ばれるメソッド
  def execute(self, context):
    if self.addPlane :
      bpy.ops.mesh.primitive_plane_add()
      context.object.name = getFileNameFromPath(self.filepath)
    active_obj = context.object
    active_obj.psd_settings.filePath = self.filepath
    active_obj.psd_settings.psdLayerNameEncoding = self.psdLayerNameEncoding
    initPSDPlane(self, context)

    return {'FINISHED'}

class LAYEREDPSDMATERIAL_OT_layerselector(bpy.types.Operator, bpy.types.PropertyGroup):
  bl_idname = "layeredpsdmaterial.layerselector"
  bl_label = "select a layer of psd"
  bl_options = {'REGISTER', 'UNDO'}

  groupName:StringProperty(options={"HIDDEN"})
  layerName:StringProperty(options={"HIDDEN"})

  def execute(self,context): 
    print("layer name:" + self.layerName + "\tg:" + self.groupName)
    if bool(self.groupName) & bool(self.layerName):
      # ラジオボタンにしない場合の処理
      ls = context.object.psd_settings.layerSettings[self.groupName]
      print(ls)
      layerItem = ls.items.get(self.layerName)
      print(layerItem)
      selected_index = ls.selectedItems.find(self.layerName)
      print(selected_index)
      if selected_index >= 0:
        ls.selectedItems.remove(selected_index)
      else:
        # ラジオボタンにする場合、他の選択値をクリアする
        if layerItem.name.startswith('*'):
          ls.selectedItems.clear()
        si = ls.selectedItems.add()
        si.name = self.layerName
    updatePsdViewState(context.object)
    return {'FINISHED'}

def menu_func_import(self, context):
  self.layout.operator(LAYEREDPSDMATERIAL_OT_importer.bl_idname, text="Import PSD as Plane", icon="TEXTURE")
