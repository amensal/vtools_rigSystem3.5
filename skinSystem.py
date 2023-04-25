import bpy
import importlib
#armUtils = bpy.data.texts["LIB_armatureUtils"].as_module()

from vtools_rigsystem import LIB_armatureUtils
if "LIB_armatureUtils" in locals():
    importlib.reload(LIB_armatureUtils)
    
armUtils = LIB_armatureUtils

#--------- LOCAL VARS  -----------------#

prop_boneVisibilityId = "visibility_"
prop_SkinIDName = "vtsk_skinID"
prop_skinShapeKeyName = "skinVisiblity_VTSP"

# ----------- LOCAL FUNCTIONS ------------------#

    
def getVisibilityKey(pObjName):
    obj = bpy.data.objects[pObjName]
    vKey = None
    
    vKey = obj.data.shape_keys.key_blocks[prop_skinShapeKeyName]
        
    return vKey

def findNodeByType(pObjectName, pType):
    node = None
    obj = bpy.data.objects[pObjectName]
    
    if (len(obj.data.materials) > 0):
        mat = obj.data.materials[0]
        for n in mat.node_tree.nodes:
            if n.type.find(pType) != -1:
                node = n
                break       
    return node

def getNodeValueIndex(pConnection, pName, pType):
    
    nodeInputID = None
    for i in range(0,len(pConnection)):
        if pConnection[i].name == pName and pConnection[i].type == pType:
            nodeInputID = i
    
    return nodeInputID
    
    
def createVisibilityShapeKey(pObjName):
    obj = bpy.data.objects[pObjName]
    found = False
    
    #IF NOT SHAPE KEY CREATES BASIS
    
    if obj.data.shape_keys == None:
        obj.shape_key_add(name="Basis")
        
    #ADD SHAPE KEY IF NOT FOUND
    for sk in obj.data.shape_keys.key_blocks:
        if sk.name.find(prop_skinShapeKeyName) != -1:
            found = True
    
    if found == False:
        obj.shape_key_add(name=prop_skinShapeKeyName)

def createDriverVariable(pName, pType, pDriver, pObjectName, pSubtarget, pData_Path, pTransType):
    
    tmpV = pDriver.driver.variables.new()
    tmpV.name = pName
    tmpV.type = pType
    tmpV.targets[0].id = bpy.data.objects[pObjectName]
    
    if pSubtarget != None:
        tmpV.targets[0].bone_target = pSubtarget
        
    if pData_Path != None:
        tmpV.targets[0].data_path = pData_Path
    elif pTransType != None:
        tmpV.targets[0].transform_type = pTransType
        tmpV.targets[0].transform_space = "LOCAL_SPACE"
        
def renamePreviousFCurves(pObjName, pOldName):
    #IF FIND A VISIBILITY CURVE RENAME IT TO THE GEOMETRY NAME
    
    obj = bpy.data.objects[pObjName]
    skinId = obj[prop_SkinIDName]
    animData = obj.animation_data
    
    if animData != None:
        action = animData.action
        if action != None:
            for fcurve in action.fcurves:
                visfcurve = fcurve.data_path.find(skinId)
                if visfcurve != -1:
                    oldName = prop_boneVisibilityId + pOldName
                    newName = prop_boneVisibilityId + pObjName
                    fcurve.data_path = fcurve.data_path.replace(oldName, newName)
        
    return {"FINISHED"}
    
    
def setVisibilityDriver(pObjName, pVisibilityBoneName):
    
    obj = bpy.data.objects[pObjName]
    arm = obj.parent
    visBone = arm.pose.bones[pVisibilityBoneName]
    
    print ("VIS BONE ", visBone)
    
    #REMOVE EXISTING VISIBILITY DRIVER
    animationData = obj.data.shape_keys.animation_data
    if animationData != None:
        driverList = animationData.drivers
        for dv in driverList:
            if dv.data_path.find(prop_skinShapeKeyName) != -1:
                driverList.remove(dv)
                break
    
    animationData = obj.animation_data
    if animationData != None:
        driverList = animationData.drivers
        for dv in driverList:
            if dv.data_path.find("hide_viewport") != None:
                driverList.remove(dv)
            
              
    #CONFIGURE DRIVERS DRIVER
    if visBone != None:
        #SHAPE KEY
        visKey = getVisibilityKey(pObjName)
        skDriver = visKey.driver_add("value")
        skDriver.driver.type = 'AVERAGE'
        #createDriverVariable("skinVisibility", "SINGLE_PROP", skDriver, pObjName, "skinVisibility")
        createDriverVariable("skinVisibility", "TRANSFORMS", skDriver, arm.name, visBone.name, None, "LOC_Y")
        
        
        #OBJECT VISIBLITY
        visDrive = obj.driver_add("hide_viewport")
        visDrive.driver.type = 'SCRIPTED'
        visDrive.driver.expression = "1 - skinVisibility"
        createDriverVariable("skinVisibility", "TRANSFORMS", visDrive, arm.name, visBone.name, None, "LOC_Y")
        
           
    return visBone


def createVisibilityBones(pArmName, pBaseObjectName, pSkinName):
    
    visBoneName = None
    arm = bpy.data.objects[pArmName]
    
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    
    newBoneName = prop_boneVisibilityId + pBaseObjectName #+ "_VTVISNODE"
    if pSkinName == False:
        visBoneName = armUtils.createNewBone(arm, newBoneName, (0,0,0), (0,0,1), False)
    else:
        oldBoneName = prop_boneVisibilityId + pSkinName
        arm.pose.bones[oldBoneName].name = newBoneName
        visBoneName = newBoneName
    
    if visBoneName != None:
        #MOVE BONE TO VISIBLE (1)
        bpy.ops.object.mode_set(mode='POSE')
        arm.pose.bones[visBoneName].location.y = 1
        
        #MOVE BONE LAYER
        armUtils.moveBoneToLayer(arm, visBoneName, 31)
    
    #SET ACTIVE OBJECT
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
    return visBoneName
    

def isMeshSkin(pObjName):
    
    skin = False
    if bpy.data.objects.find(pObjName) != -1:
        for skinLayer in bpy.context.object.vtRigSkinCollection:
            if skinLayer.objectName == pObjName: 
                skin = True
        
    return skin

def isOutlinerOpen():
    areaOverride = None
    for area in bpy.context.screen.areas:
        if area.type == "OUTLINER":
            areaOverride=area
            
    return areaOverride

def getOutlinerSelectedObjects(pArea):
    
    selectedObjects = []
    
    if pArea != None:
        with bpy.context.temp_override(area=pArea):
            for obj in bpy.context.selected_ids:
                selectedObjects.append(obj.name)

    return selectedObjects

        
# ---------- OPERATORS ---------------------------- #

class VTOOLS_OT_selectVisibilityBones(bpy.types.Operator):
    bl_idname = "vtool.selectvisibilitybones"
    bl_label = "Select Visibility Bones"
    bl_description = "Select visibility bones from skin armature"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
        
        #FIND AND SELECT VISIBILITY BONES
        arm = bpy.context.object
        
        bpy.ops.object.mode_set(mode='EDIT')

        skinCollection = bpy.context.object.vtRigSkinCollection
        for skinLayer in skinCollection:
            arm.data.edit_bones[skinLayer.visibilityBoneName].select = True
               
        bpy.ops.object.mode_set(mode='POSE')
        
        """
        skinCollection = bpy.context.object.vtRigSkinCollection
        for skinLayer in vtRigSkinCollection:
            skinLayer.objectName:
            
        for o in bpy.context.selected_objects:
            currentObjectName = o.name
            arm = o.parent
            if arm != None:
                #SELECT ARMATURE
                arm.select_set(True)
                bpy.context.view_layer.objects.active = arm
                
                bpy.ops.object.mode_set(mode='EDIT')
                
                #FIND AND SELECT VISIBILITY BONES
                for b in arm.data.edit_bones:
                    if b.name.find("visibility_") != -1:
                        b.select = True
                        
                bpy.ops.object.mode_set(mode='OBJECT')
                #bpy.ops.object.select_all(action='DESELECT')
                arm.select_set(True)
                bpy.data.objects[currentObjectName].select_set(True)
                bpy.context.view_layer.objects.active = bpy.data.objects[currentObjectName]
            """
                    
        return {'FINISHED'}
    
class VTOOLS_OT_linkSkinActions(bpy.types.Operator):
    bl_idname = "vtool.linkskinactions"
    bl_label = "Link Skin Actions"
    bl_description = "Set active objectt's action to selected"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
        
        mainAction = bpy.context.object.parent.animation_data.action
        for o in bpy.context.selected_objects:
            arm = o.parent
            if arm != None:
                if arm.animation_data == None:
                    arm.animation_data = bpy.context.object.animation_data
                
                if mainAction != arm.animation_data.action:
                    arm.animation_data.action = mainAction
                
        return {'FINISHED'}
    
class VTOOLS_OT_setConstantVisibility(bpy.types.Operator):
    bl_idname = "vtool.setconstantvisibility"
    bl_label = "Toggle Visibility"
    bl_description = "Set skin visibility for all selectd objects"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    visible : bpy.props.BoolProperty(default=True)
    
    def execute(self, context):
        
        arm = bpy.context.object
        skinCollection = bpy.context.object.vtRigSkinCollection
        for skinLayer in skinCollection:
            armUtils.setFCurveInterpolation(arm, skinLayer.visibilityBoneName, "CONSTANT")
        
        armUtils.updateScene()
        
        return {'FINISHED'}

class VTOOLS_OT_configureSkin(bpy.types.Operator):
    bl_idname = "vtool.configureskin"
    bl_label = "Configure Skin"
    bl_description = "Skin System"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    action : bpy.props.StringProperty(default="NEW")
    
    def execute(self, context):
        
        arm = bpy.context.object
        
        for obj in bpy.context.selected_objects:
            objName = obj.name
            if obj.type == "MESH":
                
                visBoneName = None
                isSkin = isMeshSkin(objName)
                
                if isSkin == False:    
                    visBoneName = createVisibilityBones(arm.name, objName, isSkin)
                    
                    if visBoneName != None:
                        newItem = arm.vtRigSkinCollection.add()
                        newItem.objectName = obj.name
                        newItem.visibilityBoneName = visBoneName
                        newItem.visible = 1
                    
                    createVisibilityShapeKey(objName)
                    setVisibilityDriver(objName, visBoneName)
                    
        return {'FINISHED'}
    

class VTOOLS_OT_deleteSkin(bpy.types.Operator):
    bl_idname = "vtool.deleteskin"
    bl_label = "Delete as Skin"
    bl_description = "Remove skin configuration"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
        arm = bpy.context.object
        skinCollection = bpy.context.object.vtRigSkinCollection
        selectedSkin = bpy.context.object.vtRigSkinCollection_ID
        
        objName = skinCollection[selectedSkin].objectName
        visBoneName = skinCollection[selectedSkin].visibilityBoneName
        
        if isMeshSkin(objName) == True:
            print("REMOVE ", objName)
            obj = bpy.data.objects[objName]
            #REMOVE DRIVERS
            ad = obj.animation_data
            if ad != None:
                for d in ad.drivers:
                    if d.data_path.find("hide_viewport") != -1:
                        ad.drivers.remove(d)
            
            #REMOVE FCURVES
            fCurveName = visBoneName#prop_boneVisibilityId + objName #obj["vtsk_skinID"]
            for ac in bpy.data.actions:
                for fc in ac.fcurves:
                    if fc.data_path.find(fCurveName) != -1:
                        ac.fcurves.remove(fc)
            
            #REMOVE SHAPE KEYS
            skID = obj.data.shape_keys.key_blocks.find(prop_skinShapeKeyName)
            print("SK ID ", skID)
            if skID != -1:
                obj.shape_key_remove(obj.data.shape_keys.key_blocks[skID])
                
            #REMOVE VISIBILITY BONE

            if visBoneName != "":
                
                #SET ACTIVE OBJECT TO ARM
                bpy.data.objects[arm.name].select_set(True)
                bpy.context.view_layer.objects.active = bpy.data.objects[arm.name]
                bpy.ops.object.mode_set(mode='EDIT')
                
                arm.data.edit_bones.remove(arm.data.edit_bones[visBoneName])
                
                skinCollection.remove(selectedSkin)
        else:
            skinCollection.remove(selectedSkin)
                     
            #REMOVE CUSTOM PROPERTY
            #del obj[prop_SkinIDName]
            
        bpy.ops.object.mode_set(mode='OBJECT')
                           
        return {'FINISHED'}  
    
# --------------- PANELS -------------------------------------------------------------- #

#UI PANEL
class VTOOLS_PT_skinSystem(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_parent_id = "VTOOLS_PT_rigSystem"
    bl_region_type = 'UI'
    bl_label = "VT - Skin System"
    bl_category = 'Tool'
    bl_options = {'DEFAULT_CLOSED'} 
        
    def drawArmaturePanel(self, context, pObj, pLayout):
        
        layout = pLayout
        obj = pObj
        obj = bpy.context.object
        
        row = layout.row()
        
        
        row.template_list("VTOOLS_UL_vtRigSkins", "", obj , "vtRigSkinCollection", obj, "vtRigSkinCollection_ID", rows=3)
        
        rowCol = row.column(align=True)
        rowCol.operator(VTOOLS_OT_configureSkin.bl_idname, text="", icon="ADD")
        rowCol.operator(VTOOLS_OT_deleteSkin.bl_idname, text="", icon="REMOVE")
        rowCol.separator()
        rowCol.operator(VTOOLS_OT_selectVisibilityBones.bl_idname, text="", icon="EYEDROPPER")
        rowCol.operator(VTOOLS_OT_setConstantVisibility.bl_idname,text="", icon = "IPO_CONSTANT")
                  
            
    @classmethod
    def poll(cls, context):
        return (context.mode == "OBJECT" or context.mode == "POSE")
    
    def draw(self,context):
        
        if bpy.context.object.type == "ARMATURE":
            
            visibleText = "Visible"
            obj = bpy.context.object
            objName = obj.name
            layout = self.layout
            #layout.use_property_split = True
            #layout.use_property_decorate = True
            
            if obj.type == "ARMATURE":
                self.drawArmaturePanel(context, obj, layout)
            else:
                layout.label(text="Select an Armature Object")
         
# ------------- MENU --------------------#


# ------------ UI LIST --------------------#

class VTOOLS_UL_vtRigSkins(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        arm = bpy.context.object
        visBone = arm.pose.bones[item.visibilityBoneName]
        
        if visBone != None:
            row = layout.row(align=True)
            
            visIcon = "HIDE_ON"
            if visBone.location.y > 0:
                visIcon = "HIDE_OFF"
            
            row.label(text="", icon=visIcon)
            row.prop(item, "objectName", text="", emboss=False) #icon="TRIA_RIGHT" 
            row = layout.row()
            row.scale_x = 0.4
            row.prop(visBone, "location", index=1, text="", slider=True)
            

    def filter_items(self, context, data, propname):        
        collec = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, collec, "objectName",
                                                          reverse=self.use_filter_sort_reverse)
        return flt_flags, flt_neworder


        
class VTOOLS_CC_vtRigSkinsCollection(bpy.types.PropertyGroup):
       
    objectName : bpy.props.StringProperty(default='')
    visibilityBoneName: bpy.props.StringProperty(default='')
    #visible: bpy.props.IntProperty(max = 1, min = 0)
    visible : bpy.props.BoolProperty()

# ----------- UI CALLBACK -----------------#

def cb_selectSkinLayer(self,value):
    
    print("SELECT")
    
    
# ------------- REGISTER ---------------------#

classes = (VTOOLS_PT_skinSystem,VTOOLS_OT_configureSkin, VTOOLS_OT_setConstantVisibility, 
VTOOLS_OT_linkSkinActions, VTOOLS_OT_selectVisibilityBones, VTOOLS_OT_deleteSkin, 
VTOOLS_UL_vtRigSkins, VTOOLS_CC_vtRigSkinsCollection, )
    

def register_skinSystem():
    for cls in classes:
        bpy.utils.register_class(cls)

    #bpy.types.Object.isMeshSkin = bpy.props.BoolProperty(default = False)
    
    bpy.types.Object.vtRigSkinCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_vtRigSkinsCollection)
    bpy.types.Object.vtRigSkinCollection_ID = bpy.props.IntProperty(default = -1)

    
def unregister_skinSystem():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    #del bpy.types.Object.isMeshSkin
    del bpy.types.Object.vtRigSkinCollection 
    del bpy.types.Object.vtRigSkinCollection_ID
    
if __name__ == "__main__":
    #unregister()
    register_skinSystem()
    
