import os
import sys
import importlib
import logging
import subprocess
import bpy
from bpy.props import *

addonName = os.path.basename(os.path.dirname(__file__))
dependant_modules=["numpy","psd_tools"]

def isInstalled(module):
  try:
    importlib.import_module(module)
    return True
  except ImportError:
    return False

def installModule(module: str, options: str = None):
  executable = None
  try:
    for path in glob.glob('{}/bin/python*'.format(sys.exec_prefix)):
      if os.access(path, os.X_OK) and not path.lower().endswith('dll'):
        executable = path
        logging.debug(
            'Blender\'s Python interpreter: {}'.format(executable))
        break
  except Exception as e:
    logging.error(e)
  if executable is None:
    logging.error('Unable to locate Blender\'s Python interpreter')

  if isInstalled('ensurepip'):
    subprocess.call([executable, '-m', 'ensurepip'])
  elif not isInstalled('pip'):
    url = 'https://bootstrap.pypa.io/get-pip.py'
    filepath = '{}/get-pip.py'.format(os.getcwd())
    try:
      requests = importlib.import_module('requests')
      response = requests.get(url)
      with open(filepath, 'w') as f:
        f.write(response.text)
      subprocess.call([executable, filepath])
    except Exception as e:
      logging.error(e)
    finally:
      if os.path.isfile(filepath):
        os.remove(filepath)

  if not isInstalled(module) and executable is not None:
      try:
          if options is None or options.strip() == '':
              subprocess.call([executable, '-m', 'pip', 'install', module])
          else:
              subprocess.call([executable, '-m', 'pip', 'install', options, module])
      except Exception as e:
          logging.error(e)

  return isInstalled(module)

class LAYEREDPSDMATERIAL_OT_installmodule(bpy.types.Operator):
  bl_idname = 'layeredpsdmaterial.installmodule'
  bl_label = 'Install Python Module'
  bl_description = 'Installs given Python module with pip'
  bl_options = {'INTERNAL'}

  name: bpy.props.StringProperty(
    name = 'Module Name',
    description = 'Installs the given module')

  options: bpy.props.StringProperty(
    name = 'Command line options',
    description = 'Command line options for pip (e.g. "--no-deps -r")',
    default = '')

  reload_scripts: bpy.props.BoolProperty(
    name = 'Reload Scripts',
    description = 'Reloads Blender scripts upon successful installation',
    default = True)

  def execute(self, context):
    if len(self.name) > 0 and installModule(self.name, self.options):
      self.report({'INFO'}, f'Installed Python module: {self.name}')
      if self.reload_scripts:
        bpy.ops.script.reload()
    else:
      self.report({'ERROR'}, f'Unable to install Python module: {self.name}')
    return {'FINISHED'}

class AddonPreferences(bpy.types.AddonPreferences):
  bl_idname = addonName

  def draw(self, context):
    layout = self.layout
    drawModuleInstaller(context, layout)

def drawModuleInstaller(context: bpy.types.Context, layout: bpy.types.UILayout):

  box = layout.box()
  box.label(text = "Install modules:")
  col = box.column(align = True)

  for module in dependant_modules:
    title = module.title()
    if isInstalled(module):
      row = col.row(align = True)
      row.label(text = f'{title} is installed', icon = 'CHECKMARK')
    else:
      row = col.row(align = True)
      op = row.operator(LAYEREDPSDMATERIAL_OT_installmodule.bl_idname,
                text = f'Install {title}', icon = 'IMPORT')
      op.name = module