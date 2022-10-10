import bpy
from bpy.props import StringProperty,EnumProperty,CollectionProperty,BoolProperty
from ..utils.psd import *
from .psdLayerItem import psdLayerItem

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
  # selectedItems : CollectionProperty(type=psdLayerItem)
  settings:EnumProperty(
    items=getItems,
    options={
      "ENUM_FLAG",
      "ANIMATABLE"
    },
    update = onUpdateLayerSettings
  )
