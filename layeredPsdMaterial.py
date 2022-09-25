# オブジェクトとpsdのパスを引数とする
# オブジェクトのカスタムプロパティからpsdの表示状態を取得し、psdに設定する
# 画像をキャッシュする(透過pngとして一度保存するか)を渡せるようにする
import bpy,re,os
import numpy as np
from bpy.props import StringProperty,EnumProperty,CollectionProperty,BoolProperty,PointerProperty
from PIL import Image

# このスクリプトではanimation nodeは使わない
try:
  from psd_tools import PSDImage
except:
  print('psd_tool is not installed!')

# layerの絶対パスを返す
def getGroupAbsPath(layer, sanitize=True):
  if (layer.name == "Root" )| (layer.name == None) | (layer.parent == None):
    return
  elif layer.parent.name == "Root":
    if layer.is_group():
      # Root階層のGroup
      return re.sub(r"[\/:*?\"<>|]","_",layer.name )
    else:
      # Root階層の通常Layer
      return "Root"
  else:
    if layer.is_group():
      # Root階層以外でGroupの場合
      return os.path.join(getGroupAbsPath(layer.parent),re.sub(r"[\/:*?\"<>|]","_",layer.name ))
    else:
      # Root階層以外でlayerの場合
      return getGroupAbsPath(layer.parent)

def getFileNameFromPath(filepath):
  return os.path.splitext( os.path.basename(filepath))[0]

def getFileExtensionFromPath(filepath):
  return os.path.splitext( os.path.basename(filepath))[1]

# TODO:imageの表示部分はanimation nodesのほうに移動する
# psdファイルから、blenderの画像にするためのnp.arrayを返す
def get_image_as_np_array(image):
  return np.array(image).flatten() / 255

def onUpdateLayerSettings(self,context):
  updatePsdViewState(context.object)


def updatePsdViewState(obj):
  # この時点でlayerとカスタムプロパティからimage名を生成する
  image_name = getImageNameByProperty(obj)
  # psdの表示layer設定
  # setPsdLayerVisibility(psd, obj)
  bpy_image = getImage(obj)
  # psdファイルの表示先とするmaterialを作成してplaneに割当する
  obj.active_material = getMaterial(image_name,bpy_image)
  return

# String imageName,bpy.image bpy_imageを設定したMaterialを生成して返す
def getMaterial(image_name,bpy_image):
  add_mat = None
  imageTextureNode = None
  # 引数のfilenameと同名のmaterialが定義されている場合、上書き なければ新規
  if image_name in list(bpy.data.materials.keys()):
    add_mat = bpy.data.materials[image_name]
    # print('material exists:'+str(add_mat))
    imageTextureNode = add_mat.node_tree.nodes['画像テクスチャ']
  else :
    add_mat = bpy.data.materials.new(image_name)
    # print('material not exists:'+str(add_mat))
    # 透過を設定
    add_mat.blend_method = 'CLIP'
    add_mat.use_nodes = True

    shader_node = add_mat.node_tree.nodes['Principled BSDF']
    # "画像テクスチャ"のノードを追加する
    imageTextureNode = add_mat.node_tree.nodes.new("ShaderNodeTexImage")

    # ノードに対するリンクを設定する
    add_mat.node_tree.links.new(shader_node.inputs['Base Color'], imageTextureNode.outputs['Color'])
    add_mat.node_tree.links.new(shader_node.inputs['Alpha'], imageTextureNode.outputs['Alpha'])
  imageTextureNode.image = bpy_image
  return add_mat

# objに設定されているカスタムプロパティからimageにつける名前を取得する
def getImageNameByProperty(obj):
  filename=os.path.splitext(bpy.path.basename(obj.psd_settings.filePath))[0]
  # やりたいこと:layerの選択状態に対して一意な名前をつける
  for ls in obj.psd_settings.layerSettings:
    bithashed=0
    for i in range(len(ls.items.keys())):
      key=ls.items.keys()[i]
      # print(key)
      # print("settings:" + str(key in ls.settings))
      # TODO:"!"始まりなら必須にする条件判定を切り出すかする
      if (key in ls.settings) | key.startswith('!'):
        bithashed = bithashed + 2**i
    filename += "_"+str(bithashed)
  filename += "_" + str(int(obj.psd_settings.isFlipped))
  return filename

def getTempPath():
  return bpy.path.abspath('//'+ 'psdCache')

# image:bpy.data.images[i]
# return:bpy.data.images[imageName]
def getImage(obj):
  imageName = getImageNameByProperty(obj)
  if bpy.data.images.get(imageName) != None:
    # 既にimageが存在する場合
    # print("image already exists:" + imageName)
    bpy_image = bpy.data.images[imageName]
  else:
    psd = PSDImage.open(os.path.abspath(bpy.path.abspath(obj.psd_settings.filePath)),encoding=obj.psd_settings.psdLayerNameEncoding)
    setPsdLayerVisibility(psd, obj)
    w,h = psd.size
    # alpha=Trueとしないと透過として保存されない
    bpy_image = bpy.data.images.new(imageName, w, h, alpha=True)
    # imageの書き出しをしない場合、numpy Arrayにしてpixelsに渡す
    image  = psd.compose(force=True)
    if obj.psd_settings.isFlipped:
      image = image.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
    bpy_image.pixels = get_image_as_np_array(image)

  return bpy_image

# psdファイル内の各layerに対して引数のobjのカスタムプロパティから表示/非表示の設定をする
def setPsdLayerVisibility(psd,obj):
  for layer in psd:
    setting = obj.psd_settings.layerSettings.get(getGroupAbsPath(layer))
    if layer.is_group():
      # groupは常に表示する
      layer.visible = True
      setPsdLayerVisibility(layer, obj)
    else:
      if setting == None:
        break
      # TODO:"!"始まりなら必須にする条件判定を切り出すかする
      elif layer.name.startswith('!'):
        # layer名が"!"で始まる場合は必須
        layer.visible = True
      elif layer.name in setting.settings:
        layer.visible=True
      else:
        layer.visible=False
  return psd

# psdファイルの読み込み後、layerの表示制御をするための設定値の追加
def addPsdLayerSettings(obj):
  psdSetting = obj.psd_settings
  psd = PSDImage.open(os.path.abspath(bpy.path.abspath(psdSetting.filePath)),encoding=psdSetting.psdLayerNameEncoding)
  psdSetting.layerSettings.clear()
  # 'Root'階層用の設定追加
  rootSetting = psdSetting.layerSettings.add()
  rootSetting.name='Root'
  rootSetting.items.clear()
  # その他フォルダ用の設定追加
  for layer in list(psd.descendants()):
    # print('group:'+getGroupAbsPath(layer) + "layerName:"+layer.name )
    if ((getGroupAbsPath(layer) == "Root") & (layer.is_group() == False)):
      item = rootSetting.items.add()
      item.name = layer.name
    else:
      layerSetting = psdSetting.layerSettings.get( getGroupAbsPath(layer))
      if layerSetting == None :
        layerSetting = psdSetting.layerSettings.add()
        layerSetting.name = getGroupAbsPath(layer)
      else:
        item = layerSetting.items.add()
        item.name = layer.name

def onFrameChangePost(scene):
  for obj in [obj for obj in scene.objects if obj.psd_settings.filePath != ""]:
    updatePsdViewState(obj)
    # print(obj.psd_settings.filePath)
  pass

def setPSDLayerConfigs(self, context):
  # context.objectがないか、psdファイルのパスじゃない場合はなにもしない
  if (context.object != None) & (getFileExtensionFromPath(self.filePath) == ".psd"):
    addPsdLayerSettings(context.object)
    # 読み込み時
    onUpdateLayerSettings(self, context)
  pass

# class setMaterialFromPSD(Operator):
#   """オブジェクトのカスタムプロパティからpsdファイルとpsdファイル内で表示するlayer情報をとり、オブジェクトのmaterialとして設定する"""
#   bl_idname = "layeredPsdMaterial.set_material_from_psd"
#   bl_label = "set object material from psd"

#   def execute(self, context):
#     return {'FINISHED'}

# psdファイルの各layer階層の名前を持たせるためのクラス
class psdLayerItem(bpy.types.PropertyGroup):
  bl_idname = "layeredPsdMaterial.psd_layer_item"
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

# layerごとの表示状態保持用のカスタムプロパティ
class psdLayerSettings(bpy.types.PropertyGroup):
  bl_idname = "layeredPsdMaterial.psd_layer_settings"
  bl_label = "psdLayerSettings"

  # itemsからEnum値を生成する
  def getItems(self, context):
    result = []
    for i in range(len(self.items)):
      layerName = self.items[i].name
      result.append((layerName,layerName,"",2**i))
    return intern_enum_items(result)

  layerNames = []
  name: StringProperty()
  items:CollectionProperty(type=psdLayerItem)
  settings:EnumProperty(
    items=getItems,
    options={
      "ENUM_FLAG",
      "ANIMATABLE"
    },
    update = onUpdateLayerSettings
  )

class psd_OT_Settings(bpy.types.PropertyGroup):
  bl_idname = "layeredPsdMaterial.psd_settings"
  bl_label = "psdMaterialProperties"
  bl_options = {'REGISTER', 'UNDO'}

  # props
  filePath: StringProperty(subtype="FILE_PATH",description="DO NOT EDIT,file path of psd file",update=setPSDLayerConfigs)
  psdLayerNameEncoding: EnumProperty(items=[
      ('macroman','default',""),
      ('shift_jis','shift_jis',"")
    ],
    default='macroman'
  )
  layerSettings: CollectionProperty(type=psdLayerSettings)
  # TODO:反転の処理追加
  isFlipped: BoolProperty(description="左右反転の有無")


#
# psdMaterial_PT_uiPanel
#
class psdMaterial_PT_uiPanel(bpy.types.Panel):
  """オブジェクトのカスタムプロパティからpsdファイルとpsdファイル内で表示するlayer情報をとり、オブジェクトのmaterialとして設定する"""
  bl_idname = "layeredPsdMaterial.psd_PT_uiPanel"
  bl_label = "set object material from psd ui"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "Psd Material"
  bl_label = "psd Configs"

  #--- draw ---#
  def draw(self, context):
    layout = self.layout
    psdSetting = context.object.psd_settings
    layout.prop(psdSetting, "psdLayerNameEncoding")
    layout.prop(psdSetting, "filePath")
    layout.prop(psdSetting, "isFlipped",text="左右反転")
    layout.separator()
    # layout.prop(psdSetting, "layerSettings")
    for layer in  psdSetting.layerSettings :
      col = layout.column()
      # print(layer)
      col.label(text = layer.name)
      if len(list(filter(lambda x:x.name.startswith("*") ,layer.items))) == 0 :
        for item in layer.items:
          col.prop_enum(layer, "settings", item.name)
      else:
        col.prop(layer,"settings",expand=True)

