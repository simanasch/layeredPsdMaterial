import bpy

#
# psdMaterial_PT_uiPanel
#
class psdMaterial_PT_uiPanel(bpy.types.Panel):
  """オブジェクトのカスタムプロパティからpsdファイルとpsdファイル内で表示するlayer情報をとり、オブジェクトのmaterialとして設定する"""
  bl_idname = "layeredpsdmaterial.PSD_PT_uiPanel"
  bl_label = "layered psd material ui"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = "Psd Material"
  bl_label = "psd Configs"

  #--- draw ---#
  def draw(self, context):
    layout = self.layout
    if not bool(context.object) or not bool(context.object.psd_settings) or not bool(context.object.psd_settings.filePath):
      return
    psdSetting = context.object.psd_settings
    layout.operator("layeredpsdmaterial.importer",text="PSDファイルを選択")
    disabledSettings=layout.column()
    disabledSettings.prop(psdSetting, "psdLayerNameEncoding")
    disabledSettings.prop(psdSetting, "filePath")
    disabledSettings.enabled = False
    layout.prop(psdSetting, "isFlipped",text="左右反転")
    layout.separator()
    for layer in  psdSetting.layerSettings :
      col = layout.column()
      # print(layer)
      if len(layer.items) > 0:
        col.label(text = layer.name)
      if len(list(filter(lambda x:x.name.startswith("*") ,layer.items))) == 0 :
        for item in layer.items:
          col.prop_enum(layer, "settings", item.name)
      else:
        # layer名が"*"で始まる場合、ラジオボタン(的な)にする
        col.prop(layer,"settings",expand=True)