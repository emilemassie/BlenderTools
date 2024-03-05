import bpy 
import sys, os
import random

#from .MainMenu import MassieVFXMenu

bl_info = {
    "name": "MVFX Plant Animator",
    "description": "This is a blender addon that is used to add modifiers and null objects to animate a geometry as if it was in",
    "author": "Emile Massie Vanassie",
    "version": (1, 0, 1),
    "blender": (3, 5, 0),
    #"wiki_url": "my github url here",
    #"tracker_url": "my github url here/issues",
    "category": "Animation"
}


class MVX_PLANT_ANIM_EXEC(bpy.types.Operator):
    bl_label = "Add wind \nto selected object"
    bl_idname = 'object.mvfxplantanim_operator'


    def execute(self, context):

        try: 
            texture_small = bpy.data.textures['noise_for_plant_anim_small']
        except:
            texture_small = bpy.data.textures.new(name='noise_for_plant_anim_small', type='CLOUDS')
            texture_small.noise_scale = 0.1

        try: 
            texture_large = bpy.data.textures['noise_for_plant_anim_large']  
        except:
            texture_large = bpy.data.textures.new(name='noise_for_plant_anim_large', type='CLOUDS')
            texture_large.noise_scale = 1

        selected_objects = bpy.context.selected_objects
        
        bpy.ops.ed.undo_push()
        count = 0
        for object in selected_objects:

            selected_object = object#bpy.context.active_object
            # mover
            if selected_object.type == 'MESH':

                bpy.ops.object.empty_add(type='SINGLE_ARROW', align='WORLD', location=(selected_object.location))
                mover = bpy.context.active_object
                mover.empty_display_size = 2
                selected_object.parent = mover
                selected_object.location = (0,0,0)

                # noise driver
                bpy.ops.object.empty_add(type='SPHERE', align='WORLD', location=(0,0,0))
                noise_driver = bpy.context.active_object
                noise_driver.empty_display_size = 0.2
                noise_driver.parent = mover

                # animate the noise

                # Set the in frame

                bpy.context.scene.frame_set(context.scene.loop_in)
                noise_driver.rotation_euler = (0, 0, 0)  
                noise_driver.keyframe_insert(data_path="rotation_euler", frame=context.scene.loop_in)

                # Set the out frame
                bpy.context.scene.frame_set(context.scene.loop_out+1)
                noise_driver.rotation_euler = (0, 0, 6.28319)
                noise_driver.keyframe_insert(data_path="rotation_euler", frame=context.scene.loop_out+1)

                # Make all animation linear
                for fcurve in noise_driver.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = 'LINEAR'

                # Add displace mods to plant
                if context.scene.bool_small:
                    dis_mod_small = selected_object.modifiers.new('Displace_small','DISPLACE')
                    dis_mod_small.texture = texture_small
                    dis_mod_small.texture_coords = 'OBJECT'
                    dis_mod_small.texture_coords_object = noise_driver
                    dis_mod_small.strength = context.scene.slider_small
                if context.scene.bool_large:
                    dis_mod_large = selected_object.modifiers.new('Displace_large','DISPLACE')
                    dis_mod_large.texture = texture_large
                    dis_mod_large.texture_coords = 'OBJECT'
                    dis_mod_large.texture_coords_object = noise_driver
                    dis_mod_large.strength = context.scene.slider_large

                # Add Bend
                bend_mod = selected_object.modifiers.new('wind_bend_x', 'SIMPLE_DEFORM')
                bend_mod.deform_axis = 'X'
                bend_mod.deform_method = 'BEND'
                bend_mod.angle = 0
                bend_mod.keyframe_insert(data_path='angle')
                

                bend_mod = selected_object.modifiers.new('wind_bend_y', 'SIMPLE_DEFORM')
                bend_mod.deform_axis = 'Y'
                bend_mod.deform_method = 'BEND'
                bend_mod.angle = 0
                bend_mod.keyframe_insert(data_path='angle')

                for fcurve in selected_object.animation_data.action.fcurves:
                    if 'wind_bend' in fcurve.data_path:
                        noise_mod = fcurve.modifiers.new('NOISE')
                        noise_mod.scale = context.scene.plant_scale
                        noise_mod.strength = context.scene.plant_strength
                        noise_mod.offset = 1000 * random.random()

                        noise_mod.use_restricted_range = True
                        noise_mod.frame_start = context.scene.loop_in
                        noise_mod.frame_end = context.scene.loop_out

                        noise_mod.blend_in = context.scene.plant_blend_frames
                        noise_mod.blend_out = context.scene.plant_blend_frames
                count = count+1
            bpy.ops.ed.undo_push()
            
        self.report({'INFO'}, 'Added Wind Modifiers to '+str(count)+' Objects')
        return {'FINISHED'}
    
class MVFX_PLANT_ANIM_PANEL(bpy.types.Panel):
    bl_label = 'MVFX Plant Animator'
    bl_idname = 'MVFX_PT_PLANT_ANIMATOR_PANEL'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MVFX Plant Animator'


    
    def draw(self, context):

        layout = self.layout
        #row = layout.row()
        #image = bpy.data.images.load(os.path.join(os.path.dirname(__file__),'splash.jpg'))
        #print (os.path.join(os.path.dirname(__file__),'splash.jpg'))
        #row.template_preview(image)
        
        row = layout.box()
        row.label(text='Distortion Frenquency Selection')
        row.prop(context.scene, 'bool_small')
        row.prop(context.scene, 'slider_small')
        row.prop(context.scene, 'bool_large')
        row.prop(context.scene, 'slider_large')
        
        sep = row.separator()
        
        box = layout.box()
        box.label(text='Wind Loop In-Out Frames')
        row = box.row(align = True)
        row.prop(context.scene, 'loop_in')
        row.prop(context.scene, 'loop_out')
        row = box.row()
        row.prop(context.scene, 'plant_blend_frames')
        box = layout.box()
        box.label(text='Wind Bend Settings')
        row= box.row()
        row.prop(context.scene, 'plant_scale')
        row.prop(context.scene, 'plant_strength')

        row = layout.row()
        row.scale_y = 2
        row.operator('object.mvfxplantanim_operator')


classes = [MVX_PLANT_ANIM_EXEC, MVFX_PLANT_ANIM_PANEL]

def register():

    bpy.types.Scene.loop_in = bpy.props.IntProperty(name='In', default=0)
    bpy.types.Scene.loop_out = bpy.props.IntProperty(name='Out', default=100)
    bpy.types.Scene.plant_blend_frames = bpy.props.IntProperty(name='In-Out Softness', default=20)

    bpy.types.Scene.bool_small = bpy.props.BoolProperty(name='Use Small Frequency', default=True)
    bpy.types.Scene.slider_small = bpy.props.FloatProperty(name='Small Frequency', default=0.02)
    bpy.types.Scene.bool_large = bpy.props.BoolProperty(name='Use Large Frequency', default=True)
    bpy.types.Scene.slider_large = bpy.props.FloatProperty(name='Large Frequency', default=0.3)

    bpy.types.Scene.plant_strength = bpy.props.FloatProperty(name='Strength', default=0.5)
    bpy.types.Scene.plant_scale = bpy.props.FloatProperty(name='Frequency', default=20)

    for i in classes:
        bpy.utils.register_class(i)

def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)

    del bpy.types.Scene.bool_small
    del bpy.types.Scene.slider_small 
    del bpy.types.Scene.bool_large
    del bpy.types.Scene.slider_large

    del bpy.types.Scene.loop_in
    del bpy.types.Scene.loop_out
    del bpy.types.Scene.plant_blend_frames

    del bpy.types.Scene.plant_strength
    del bpy.types.Scene.plant_scale

