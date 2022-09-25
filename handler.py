import bpy
from .layeredpsdmaterial import *

def onFrameChangePost(scene):
  """表示フレーム更新後の処理"""
  for obj in [obj for obj in scene.objects if (obj.psd_settings.filePath) & (obj.psd_settings.filePath != "")]:
    updatePsdViewState(obj)