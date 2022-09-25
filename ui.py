import bpy

#
# psdMaterial_PT_uiPanel
#
class psdMaterial_PT_uiPanel(bpy.types.Panel):
  """オブジェクトのカスタムプロパティからpsdファイルとpsdファイル内で表示するlayer情報をとり、オブジェクトのmaterialとして設定する"""
  bl_idname = "layeredPsdMaterial.PSD_PT_uiPanel"
  bl_label = "layered psd material ui"
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
    if not psdSetting.filePath:
      return
    for layer in  psdSetting.layerSettings :
      col = layout.column()
      # print(layer)
      col.label(text = layer.name)
      if len(list(filter(lambda x:x.name.startswith("*") ,layer.items))) == 0 :
        for item in layer.items:
          col.prop_enum(layer, "settings", item.name)
      else:
        col.prop(layer,"settings",expand=True)

