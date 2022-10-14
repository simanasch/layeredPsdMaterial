import bpy
from bpy.app.handlers import persistent
from ..utils.psd import *

@persistent
def onFrameChangePost(scene,depsgraph):
  """表示フレーム更新後の処理"""
  for obj in [obj for obj in bpy.data.objects if bool(obj.psd_settings.filePath)]:
    updatePsdViewState(obj.evaluated_get(depsgraph))