import bpy

from .MainMenu import MassieVFXMenu

bl_info = {
    "name": "MassieVFX",
    "description": "This is a blender menu that adds mostly pipeline functionalities and automations",
    "author": "Emile Massie Vanassie",
    "version": (1, 0, 0),
    "blender": (2, 7, 9),
    #"wiki_url": "my github url here",
    #"tracker_url": "my github url here/issues",
    "category": "Menu"
}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)