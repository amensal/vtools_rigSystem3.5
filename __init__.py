bl_info = {
    "name": "vtools - Rig System",
    "author": "Antonio Mendoza - Campero Games",
    "version": (0, 3, 4),
    "blender": (3, 00, 0),
    "location": "View3D > Tool Panel > Tool Tab >  vTools Rig System",
    "warning": "",
    "description": "Simple Rig system to create IK/FK Chain Bones",
    "category": "Animation",
}

import bpy
import importlib

class VTOOLS_PT_rigSystem(bpy.types.Panel):
    bl_label = "VT - Rig Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return (context.mode == "OBJECT" or context.mode == "POSE")
    
    def draw(self, context):
        layout = self.layout

# -- REGISTRATION -- #        
modules = ()
classes = (VTOOLS_PT_rigSystem,)



        
    
def register():
    
    from .rigSystem import register_rigsystem
    register_rigsystem()
    
    from .curveTools import register_curveTools
    register_curveTools()
    
    from .boneTools import register_bonetools
    register_bonetools()
    
    from .spriteSystem import register_spriteSystem
    register_spriteSystem()
    
    from .skinSystem import register_skinSystem
    register_skinSystem()
    

def unregister():

    from .rigSystem import unregister_rigsystem
    unregister_rigsystem()
    
    from .curveTools import unregister_curveTools
    unregister_curveTools()
    
    from .boneTools import unregister_bonetools
    unregister_bonetools()
    
    from .spriteSystem import unregister_spriteSystem
    unregister_spriteSystem()
    
    from .skinSystem import unregister_skinSystem
    unregister_skinSystem()
    
    for c in classes:
        bpy.utils.unregister_class(c)

"""
def register_main():
    for c in classes:
        bpy.utils.register_class(c)
        
if __name__ == "__main__":
    register_main()

"""