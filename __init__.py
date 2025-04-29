bl_info = {
    "name": "Projectile Motion Modifier",
    "author": "Daniel W",
    "version": (0, 1),
    "blender": (4, 0, 0),
    "location": "Physics Properties",
    "description": "Simulates Projectile Motion With Drag",
    "category": "Physics Properties"
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup, FloatProperty, PointerProperty, StringProperty
from bpy.utils import register_class, unregister_class
from mathutils import Matrix, Vector
import math


def center_of_mass(object_name):
    context = bpy.context
    scene = context.scene
    
    object = scene.objects[object_name]
    object_data = object.data
    origin = sum((vert.co for vert in object_data.vertices), Vector()) / len(object_data.vertices)
    
    return origin

def projectile_motion():
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    mytool.is_projectile = 1
    
def simulate_projectile():
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    object = context.active_object
    
    if mytool.Clear_Previous_Simulation == True:
        object.animation_data_clear()
    
    com = center_of_mass(object.name)
    v_x = mytool.projectile_vector_x
    v_y = mytool.projectile_vector_y
    v_z = mytool.projectile_vector_z
    
    gty = mytool.gravity
    rho = mytool.density
    if rho == 0:
        rho = 0.01
    g = gty
    Cd = mytool.drag
    if Cd == 0:
        Cd = 0.01
    r = object.scale.x / 2
    A = math.pi * (r**2)
    m = mytool.mass
    t_i = mytool.frame_start
    t_f = mytool.frame_end
    
    v_t = math.sqrt((2*m*g)/(Cd*A*rho))
    h = ((v_t**2)/(2*g)) * math.log(((v_z**2)+(v_t**2))/(v_t**2))
    t = (t_f - t_i) / 24
    
    frame_count = t * 24
    
    loc_i_x = object.location.x
    loc_i_y = object.location.y
    loc_i_z = object.location.z
    
    for n in range(int(frame_count)):
        d_t = n / 24
        v = (v_t*(v_z-(v_t*math.tan((d_t*g)/v_t))))/(v_t+(v_z*math.tan((d_t*g)/v_t)))
        z = ((v_t**2)/(2*g)) * math.log(((v_z**2)+(v_t**2))/((v**2)+(v_t**2)))
        x = ((v_t**2)/g) * math.log(((v_t**2)+(g*v_x*d_t))/(v_t**2))
        y = ((v_t**2)/g) * math.log(((v_t**2)+(g*v_y*d_t))/(v_t**2))
        
        object.location.x = loc_i_x + x
        object.location.y = loc_i_y + y
        object.location.z = loc_i_z + z
        
        object.keyframe_insert(data_path="location", frame=int((n + bpy.data.scenes[0].frame_start)))
        


class ProjectileMotion(bpy.types.Operator):
    """Projectile Motion"""
    bl_idname = "object.projectile_motion"
    bl_label = "Projectile Motion"
    
    def execute(self, context):
        context = bpy.context
        scene = context.scene
        mytool = scene.settings
        
        projectile_motion()
        return {'FINISHED'} 
    
class SimulateProjectile(bpy.types.Operator):
    """Simulate Projectile"""
    bl_idname = "object.simulate_projectile"
    bl_label = "Simulate Projectile"
    
    def execute(self, context):
        context = bpy.context
        scene = context.scene
        mytool = scene.settings
        
        simulate_projectile()
        return {'FINISHED'}
    
class Settings(PropertyGroup):

#    file_name : bpy.props.StringProperty(name = "File Path")
    
    Clear_Previous_Simulation : bpy.props.BoolProperty(default=True)
    
    is_projectile : bpy.props.IntProperty(name = "is_projectile", default = 1, min = 0, max = 1)

    frame_start : bpy.props.IntProperty(name = "Frame Start", min = 0, default = bpy.data.scenes[0].frame_start)
    frame_end : bpy.props.IntProperty(name = "Frame End", min = 0, default = bpy.data.scenes[0].frame_end)
    
    projectile_vector_x : bpy.props.FloatProperty(name = "Velocity X (m/s)", min = -100, max = 100, default = 0)
    projectile_vector_y : bpy.props.FloatProperty(name = "Velocity Y (m/s)", min = -100, max = 100, default = 0)
    projectile_vector_z : bpy.props.FloatProperty(name = "Velocity Z (m/s)", min = -100, max = 100, default = 1.00)
    
    projectile_velocity : bpy.props.FloatProperty(name = "Velocity (m/s)", min = 0, max = 500, default = 1)

    gravity : bpy.props.FloatProperty(name = "Gravity", min = 0, max = 500, default = 9.81)
    
    drag : bpy.props.FloatProperty(name = "Drag", min = 0, max = 10, default = 0.47)
    density : bpy.props.FloatProperty(name = "Density", min = 0, max = 100, default = 1.23)
    
    mass : bpy.props.FloatProperty(name = "Mass", min = 0, max = 500, default = 1)

class PhysicsPanel(bpy.types.Panel):
    """Projectile Motion"""
    bl_label = "Projectile Motion"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        settings = context.scene.settings
        scene = context.scene
        mytool = scene.settings
        
#        layout.prop(mytool, "is_projectile")

        row.operator(ProjectileMotion.bl_idname, text="Projectile Motion", icon="TRACKING_REFINE_FORWARDS")     
        
        if mytool.is_projectile == 1:

            layout.prop(mytool, "frame_start")
            layout.prop(mytool, "frame_end")
            
            row = layout.row()
            row.label(text="Velocity of Projectile")
            
            layout.prop(mytool, "projectile_vector_x")
            layout.prop(mytool, "projectile_vector_y")
            layout.prop(mytool, "projectile_vector_z")
            
            row = layout.row()
            row.label(text="Gravity")
            
            layout.prop(mytool, "gravity")
            
            row = layout.row()
            row.label(text="Mass of Object")
            
            layout.prop(mytool, "mass")
            
            row = layout.row()
            row.label(text="Air Properties")
            
            layout.prop(mytool, "drag")
            layout.prop(mytool, "density")
            
            row = layout.row()
            row.prop(mytool, "Clear_Previous_Simulation")
            
            row = layout.row()
            row.operator(SimulateProjectile.bl_idname, text="Simulate Projectile")     
   
            
#            row = layout.row()
 #           row.label(text="Velocity of Projectile")
            
  #          layout.prop(mytool, "projectile_velocity")

            
_classes = [
    PhysicsPanel,
    ProjectileMotion,
    SimulateProjectile,
    Settings
]


def register():
    for c in _classes: register_class(c)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=Settings)
    
def unregister():
    for c in _classes: unregister_class(c)
    del bpy.types.Scene.settings
    
context = bpy.context
scene = context.scene
mytool = scene.settings

mytool.is_projectile = 0


if __name__ == "__main__":    
    register()
    
