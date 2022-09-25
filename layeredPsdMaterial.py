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
  """psdファイルの表示状態が更新された場合の処理"""
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

def setPSDLayerConfigs(self, context):
  # context.objectがないか、psdファイルのパスじゃない場合はなにもしない
  if (context.object != None) & (getFileExtensionFromPath(self.filePath) == ".psd"):
    addPsdLayerSettings(context.object)
    # 読み込み時
    onUpdateLayerSettings(self, context)
  pass
