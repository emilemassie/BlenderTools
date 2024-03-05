import bpy
from .ops.SetupCompositorForNuke import SetupCompositorForNuke
bl_info = {"name" : "MassieVFX",   "category": "Menu",   "author": "Emile Massie-Vanasse"}


class MassieVFXMenu(bpy.types.Menu):
    bl_idname = "massievfx_menu"
    bl_label = "MassieVFX"

    def draw(self, context):
        self.layout.operator("massievfx.setup_render_passes")

class SetupRenderPassesOperator(bpy.types.Operator):
    bl_idname = "massievfx.setup_render_passes"
    bl_label = "Setup Render Passes"

    def execute(self, context):
        SetupCompositorForNuke().execute()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MassieVFXMenu)
    bpy.utils.register_class(SetupRenderPassesOperator)
    bpy.types.TOPBAR_MT_editor_menus.append(menu_draw)

def unregister():
    bpy.utils.unregister_class(MassieVFXMenu)
    bpy.utils.unregister_class(SetupRenderPassesOperator)
    bpy.types.TOPBAR_MT_editor_menus.remove(menu_draw)

def menu_draw(self, context):
    self.layout.menu(MassieVFXMenu.bl_idname)

register()
