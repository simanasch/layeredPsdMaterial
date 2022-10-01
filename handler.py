import bpy
from .layeredPsdMaterial import *

def onFrameChangePost(scene):
  """表示フレーム更新後の処理"""
  for obj in [obj for obj in bpy.data.objects if bool(obj.psd_settings.filePath)]:
    updatePsdViewState(obj)