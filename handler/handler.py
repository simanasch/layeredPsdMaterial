import bpy
from ..utils.psd import *

def onFrameChangePost(scene,depsgraph):
  """表示フレーム更新後の処理"""
  for obj in [obj for obj in bpy.data.objects if bool(obj.psd_settings.filePath)]:
    print("updating"+str(obj.evaluated_get(depsgraph)))
    updatePsdViewState(obj.evaluated_get(depsgraph))