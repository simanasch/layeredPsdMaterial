import bpy
from bpy.props import FloatProperty,StringProperty,EnumProperty,CollectionProperty,BoolProperty
from .layeredPsdMaterial import *


class psdLayerItem(bpy.types.PropertyGroup):
  """psdファイル内の各layer階層の名前を持たせるためのクラス"""
  bl_idname = "layeredpsdmaterial.psd_layer_item"
  bl_label = "psdLayerItem"

  name:StringProperty()

# bpy.props.EnumPropertyの既知バグ回避のためのワークアラウンド
# EnumPropertyに持たせる文字列への参照をキャッシュする(ないと文字化けする。。。)
STRING_CACHE = {}
def intern_enum_items(items):
  def intern_string(s):
    if not isinstance(s, str):
      return s
    global STRING_CACHE
    if s not in STRING_CACHE:
      STRING_CACHE[s] = s
    return STRING_CACHE[s]
  return [tuple(intern_string(s) for s in item) for item in items]

def onUpdateLayerSettings(self,context):
  if hasattr(context, "object") and hasattr(context.object, "psd_settings") and bool(context.object.psd_settings.filePath):
    # 何故か条件を満たすオブジェクトが選択されている場合に常時呼ばれている…
    # print("onUpdateLayerSettings:"+context.object.psd_settings.filePath)
    updatePsdViewState(context.object)

class psdLayerSettings(bpy.types.PropertyGroup):
  """psdファイル内のlayerごとの表示状態を保持するカスタムプロパティクラス"""
  bl_idname = "layeredpsdmaterial.psd_layer_settings"
  bl_label = "psdLayerSettings"

  # itemsからEnum値を生成する
  def getItems(self, context):
    result = []
    for i in range(len(self.items)):
      layerName = self.items[i].name
      result.append((layerName,layerName,""))
    return intern_enum_items(result)

  name: StringProperty()
  isvisible: BoolProperty(default=True)
  items:CollectionProperty(type=psdLayerItem)
  selectedItems : CollectionProperty(type=psdLayerItem)
  volume: FloatProperty()
  controlType:EnumProperty(
    items=[
      ("default","default",""),
      ("index","index","")
    ],
    options={"ANIMATABLE"},
    default='default'
  )
  settings:EnumProperty(
    items=getItems,
    options={
      "ENUM_FLAG",
      "ANIMATABLE"
    },
    update = onUpdateLayerSettings
  )

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

