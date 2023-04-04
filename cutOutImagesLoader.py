import bpy
import json


#IMAGENES: G:\Unidades compartidas\Voodoo Hybrid\01SliceItAll\Art\Assets\Characters\ChefCouteau\05_Animation\resources


#1) CARGAR IMAGENES CON IMAGES AS PLANES


#2 )LEE JSON PAR COLOCAR Y ESCALA
print(" ------------ INIT ---------------") 

def xmlLoadeR():
    """
    with open("G:/Unidades compartidas/Voodoo Hybrid/01SliceItAll/Art/Assets/Characters/ChefCouteau/04_Rig/ChefCouteauOut.json", "r") as fileData:
        data = json.load(fileData)
    """

    with open("C:/Users/Usuario/Desktop/borrar/testExport/export/root.json", "r") as fileData:
        data = json.load(fileData)
            
    #print(data["skins"]["default"]["Hat"])
    cont = 0
    yDesp = -0.005
    lowestSkin = None
    skinList = []

    for key in data:
        print("NODE ", key)
        if key == "skins":
            skinData = data[key]
            for skinLayers in skinData:
                print("layers ", skinLayers)
                
                layerData = skinData[skinLayers]
                for skin in layerData:
                    objectData = layerData[skin]
                    #print(skin, ": ", objectData[skin]["x"])
                    
                    if bpy.context.view_layer.objects.find(skin) != -1:
                        
                        currentObject = bpy.context.view_layer.objects[skin]
                        skinList.append(currentObject)
                        
                        posx = objectData[skin]["x"]/100
                        posy = objectData[skin]["y"]/100
                        dimx = objectData[skin]["width"]/100
                        dimy = objectData[skin]["height"]/100
                            
                        currentObject.location.x = posx  
                        currentObject.location.z = posy
                        currentObject.location.y = cont*yDesp
                        
                        
                        currentObject.dimensions.x = dimx
                        bpy.context.view_layer.update()
                        currentObject.dimensions.y = dimy
                        bpy.context.view_layer.update()

                        print("SKIN: ", skin, " ", posx, " ", posy, " ", dimx, " ", dimy)
                        
                        
                        #LOWEST OBJECT
                        if lowestSkin == None or posy < lowestSkin.location.z:
                            lowestSkin = currentObject

                    cont += 1
                    

    """
    #CREA ARMATURE Y HUESO ROOT           

    bpy.context.scene.cursor.location.x = 0
    bpy.context.scene.cursor.location.y = 0
    bpy.context.scene.cursor.location.z = 0

    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    charArm = bpy.context.object
    charArm.pose.bones[0].name = "root"

    charArm.lock_location[0] = True
    charArm.lock_location[1] = True
    charArm.lock_location[2] = True

    charArm.lock_rotation[0] = True
    charArm.lock_rotation[1] = True
    charArm.lock_rotation[2] = True
                    
    #MOVE ALL SKINS TO 0,0,0 Y EMPARETAR A ARMATURE
    vectorDesp = lowestSkin.location.copy()
    for obj in skinList:
        obj.location.x -= vectorDesp.x
        obj.location.z -= vectorDesp.z
        obj.parent = charArm
        obj.parent_type = "ARMATURE"
        obj.modifiers.new(type = "ARMATURE", name = "c2DArmature")
        obj.modifiers[len(obj.modifiers) -1].object = charArm

    """

    """    
    for skin in data["skins"]:
        print(skin)
        for skinNode in :
            print(skinNode, " ", skinNode["x"])
    """
    
def loadImagesFromFolder(pType="PNG"):
    
    
    return True






# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


# -- DEF -- #

def read_some_data(context, filepath, use_some_setting):
    print("running read_some_data...")
    f = open(filepath, 'r', encoding='utf-8')
    data = f.read()
    f.close()

    # would normally load the data here
    print(data)

    return {'FINISHED'}

# -- OPERATORS -- #

class ImportSomeData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Some Data"

    # ImportHelper mixin class uses this
    filename_ext = ".png"#".txt"
    
    """
    filter_glob: StringProperty(
        default= "*.txt",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )
    
    """

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting)

# -- PANELS -- #

#UI PANEL
class VTOOLS_PT_skinSystem(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_parent_id = "VTOOLS_PT_rigSystem"
    bl_region_type = 'UI'
    bl_label = "VT - Skin System"
    bl_category = 'Tool'
    bl_options = {'DEFAULT_CLOSED'} 
        
    @classmethod
    def poll(cls, context):
        return (context.object.type == "ARMATURE")
    
    def draw(self,context):
        layout = self.layout
        layout.label(text="Import")

            

# -- REGISTER -- #

classes = (VTOOLS_PT_skinSystem,)
    
    
def 2DCutOutLoader_register():
    
    for cls in classes:
        bpy.utils.register_class(cls)

def 2DCutOutLoader_unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    2DCutOutLoader_register()

    # test call
    #bpy.ops.import_test.some_data('INVOKE_DEFAULT')