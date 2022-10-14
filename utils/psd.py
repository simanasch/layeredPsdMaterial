# PSDファイルや画像に対する関数郡
import bpy,re,os
try:
  import numpy as np
  from PIL import Image
  from psd_tools import PSDImage
except Exception as e:
  import logging
  logging.debug("error during import:"+ str(e))

def sanitizeFilePath(path):
  return re.sub(r"[\/:*?\"<>|]","_",path )

# layerの絶対パスを返す
def getGroupAbsPath(layer, sanitize=True):
  if (layer.name == "Root" )| (layer.name == None) | (layer.parent == None):
    return
  elif layer.parent.name == "Root":
    if layer.is_group():
      # Root階層のGroup
      return sanitizeFilePath(layer.name)
    else:
      # Root階層の通常Layer
      return "Root"
  else:
    if layer.is_group():
      # Root階層以外でGroupの場合
      return os.path.join(getGroupAbsPath(layer.parent),sanitizeFilePath(layer.name))
    else:
      # Root階層以外でlayerの場合
      return getGroupAbsPath(layer.parent)

def getFileNameFromPath(filepath):
  return os.path.splitext( os.path.basename(filepath))[0]

def getFileExtensionFromPath(filepath):
  return os.path.splitext( os.path.basename(filepath))[1]

# psdファイルから、blenderの画像にするためのnp.arrayを返す
def get_image_as_np_array(image):
  return np.array(image).flatten() / 255

def updatePsdViewState(obj):
  """psdファイルの表示状態が更新された場合の処理"""
  # layerの表示状態からimage名を生成する
  image_name = getImageNameByProperty(obj)
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
    # imageTextureNode = add_mat.node_tree.nodes['画像テクスチャ']
  else :
    # マテリアルを新規追加
    add_mat = bpy.data.materials.new(image_name)
    # 透過を設定
    add_mat.blend_method = 'CLIP'
    add_mat.shadow_method = 'CLIP'
    add_mat.use_nodes = True

    # ノードを追加
    shader_node = add_mat.node_tree.nodes['Principled BSDF']
    imageTextureNode = add_mat.node_tree.nodes.new("ShaderNodeTexImage")

    # ノード同士のリンクを設定
    add_mat.node_tree.links.new(shader_node.inputs['Base Color'], imageTextureNode.outputs['Color'])
    add_mat.node_tree.links.new(shader_node.inputs['Alpha'], imageTextureNode.outputs['Alpha'])
    imageTextureNode.image = bpy_image
  return add_mat

def getImageNameByProperty(obj):
  """引数のobjに対するpsdファイル関係の設定から、imageにつける名前を取得する"""
  filename=os.path.splitext(bpy.path.basename(obj.psd_settings.filePath))[0]
  for ls in obj.psd_settings.layerSettings:
    bithashed=0
    for i in range(len(ls.items.keys())):
      key=ls.items.keys()[i]
      # TODO:"!"始まりなら必須にする条件判定を切り出すかする
      if (key in ls.settings) | key.startswith('!'):
        bithashed = bithashed + 2**i
    filename += "_"+str(bithashed)
  filename += "_" + str(int(obj.psd_settings.isFlipped))
  return filename

def getImage(obj):
  """引数のobjに対するpsdファイル関係の設定から、objに設定するbpy_imageを返す"""
  imageName = getImageNameByProperty(obj)
  if bpy.data.images.get(imageName) != None:
    # 既にimageが存在する場合
    bpy_image = bpy.data.images[imageName]
  else:
    # print(os.path.abspath(bpy.path.abspath(obj.psd_settings.filePath)))
    psd = PSDImage.open(os.path.abspath(bpy.path.abspath(obj.psd_settings.filePath)),encoding=obj.psd_settings.psdLayerNameEncoding)
    setPsdLayerVisibility(psd, obj)
    w,h = psd.size
    # alpha=Trueとしないと透過として保存されない
    bpy_image = bpy.data.images.new(imageName, w, h, alpha=True)
    # imageの書き出しをしない場合、numpy Arrayにしてpixelsに渡す
    image  = psd.compose(force=True)
    # 左右反転の処理
    if obj.psd_settings.isFlipped:
      image = image.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
    bpy_image.pixels = get_image_as_np_array(image)

  return bpy_image

def setPsdLayerVisibility(psd,obj):
  """引数のobjに対するpsdファイル関係の設定から、psdファイル内の各layerに対する表示制御を行う"""
  for layer in psd:
    setting = obj.psd_settings.layerSettings.get(getGroupAbsPath(layer))
    if layer.is_group():
      # TODO:Groupに対する表示制御を追加
      layer.visible = True
      setPsdLayerVisibility(layer, obj)
    else:
      if setting == None:
        break
      # TODO:"!"始まりなら必須にする条件判定を切り出すかする
      elif layer.name.startswith('!'):
        # layer名が"!"で始まる場合、必須
        layer.visible = True
      # elif setting.selectedItems.get(layer.name) != None:
      #   layer.visible=True
      elif layer.name in setting.settings:
        layer.visible=True
      else:
        layer.visible=False
  return psd

def addPsdLayerSettings(obj):
  """PSDファイル読み込み後の初期処理、各layerごとに表示/非表示制御をするためのプロパティを追加する"""
  psdSetting = obj.psd_settings
  psd = PSDImage.open(os.path.abspath(bpy.path.abspath(psdSetting.filePath)),encoding=psdSetting.psdLayerNameEncoding)
  w, h = psd.size
  max_size = max(psd.size)
  # importするpsdファイルに合わせ、オブジェクトをリサイズする
  obj.scale = (1.0,1.0,1.0)
  bpy.ops.transform.resize(value=((w/max_size, h/max_size,0)))
  # psdファイルの設定クリア後、ルート階層用の設定値追加
  psdSetting.layerSettings.clear()
  rootSetting = psdSetting.layerSettings.add()
  rootSetting.name='Root'
  rootSetting.items.clear()
  # その他フォルダ用の設定追加
  for layer in list(psd.descendants()):
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

def initPSDPlane(self, context):
  # context.objectがないか、psdファイルのパスじゃない場合はなにもしない
  if (context.object != None) & (getFileExtensionFromPath(context.object.psd_settings.filePath) == ".psd"):
    # psdファイルに対する設定値を初期化
    addPsdLayerSettings(context.object)
    # psdファイルの読み込み
    updatePsdViewState(context.object)
