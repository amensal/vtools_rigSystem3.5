import bpy
import importlib
#armUtils = bpy.data.texts["LIB_armatureUtils"].as_module()

from vtools_rigsystem import LIB_armatureUtils
if "LIB_armatureUtils" in locals():
    importlib.reload(LIB_armatureUtils)
    
armUtils = LIB_armatureUtils

#--------- LOCAL VARS  -----------------#

boneVisibilityId = "visibility_"
propSkinIDName = "vtsk_skinID"


# ----------- LOCAL FUNCTIONS ------------------#

    
def getVisibilityKey(pObjName):
    obj = bpy.data.objects[pObjName]
    vKey = None
    
    vKey = obj.data.shape_keys.key_blocks["skinVisiblity_VTSP"]
        
    return vKey

def getVisibilityNode(pObjName):
    
    obj = bpy.data.objects[pObjName]
    vNode = None
    if len(obj.data.materials) > 0:
        mat = obj.data.materials[0]
        idNode = mat.node_tree.nodes.find("skinVisibilityNode_VTSP") 
        if idNode != -1:
            vNode = mat.node_tree.nodes[idNode]
    
    return vNode
    
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
    
    
def addSkinMatNodes(pObjectName):
    
    obj = bpy.data.objects[pObjectName]
    mat = None
    nodeListNames = ["skinVisibilityNode_VTSP", "transparentShaderNode_VTSP", "mixShaderNode_VTSP"]
    
    #CHECK MATERIAL
    if len(obj.data.materials) == 0:
        #CREATE DEFAULT MATERIAL
        bpy.data.materials.new("newMat")
        
    mat = obj.data.materials[0]
    
    #CONFIGURE MATERIAL
    mat.blend_method = "CLIP"
    mat.shadow_method = "CLIP"
    
    
    #REMOVE EXISTING NODES
    for nName in nodeListNames: 
        if mat.node_tree.nodes.find(nName) != -1:
            mat.node_tree.nodes.remove(mat.node_tree.nodes[nName])

    #FIND TEX, OUTPUT AND SHADER NODES
    texNode = findNodeByType(pObjectName, "TEX_IMAGE")
    shaderNode = findNodeByType(pObjectName, "BSDF")
    outputNode = findNodeByType(pObjectName, "OUTPUT")
    
    #CREATE TRANSPARENT SHADER
    transparentShader = mat.node_tree.nodes.new(type="ShaderNodeBsdfTransparent")
    transparentShader.name = "transparentShaderNode_VTSP"
    
    #CREATE MIX SHADER
    mixShader = mat.node_tree.nodes.new(type="ShaderNodeMixShader")
    mixShader.name = "mixShaderNode_VTSP"
    
    #CREATE SKIN ALPHA NODES
    alphaValueNode = mat.node_tree.nodes.new(type="ShaderNodeValue")
    alphaValueNode.name = "skinVisibilityNode_VTSP"
    alphaValueNode.outputs["Value"].default_value = 1
    
    #CONNECT NODES
    if shaderNode != None and texNode != None:
        mat.node_tree.links.new(alphaValueNode.outputs["Value"], mixShader.inputs["Fac"])
        mat.node_tree.links.new(shaderNode.outputs[0], mixShader.inputs[2])
        mat.node_tree.links.new(transparentShader.outputs[0], mixShader.inputs[1])
        mat.node_tree.links.new(mixShader.outputs["Shader"], outputNode.inputs["Surface"])
    
def createVisibilityShapeKey(pObjName):
    obj = bpy.data.objects[pObjName]
    found = False
    
    #IF NOT SHAPE KEY CREATES BASIS
    
    if obj.data.shape_keys == None:
        obj.shape_key_add(name="Basis")
        
    #ADD SHAPE KEY IF NOT FOUND
    for sk in obj.data.shape_keys.key_blocks:
        if sk.name.find("skinVisiblity_VTSP") != -1:
            found = True
    
    if found == False:
        obj.shape_key_add(name="skinVisiblity_VTSP")

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
        
    
    """
    tmpV = pDriver.driver.variables.new()
    tmpV.name = pName
    tmpV.type = 'TRANSFORMS'
    tmpV.targets[0].id = bpy.data.objects[pArmName]
    tmpV.targets[0].bone_target = "spControl.000"
    tmpV.targets[0].transform_type = pTransType
    tmpV.targets[0].transform_space = "LOCAL_SPACE"
    """

def renamePreviousFCurves(pObjName, pOldName):
    #IF FIND A VISIBILITY CURVE RENAME IT TO THE GEOMETRY NAME
    
    obj = bpy.data.objects[pObjName]
    skinId = obj[propSkinIDName]
    animData = obj.animation_data
    
    if animData != None:
        action = animData.action
        if action != None:
            for fcurve in action.fcurves:
                visfcurve = fcurve.data_path.find(skinId)
                if visfcurve != -1:
                    oldName = boneVisibilityId + pOldName
                    newName = boneVisibilityId + pObjName
                    fcurve.data_path = fcurve.data_path.replace(oldName, newName)
        
    return {"FINISHED"}
    
    
def setVisibilityDriver(pObjName, pVisibilityBoneName):
    
    obj = bpy.data.objects[pObjName]
    arm = obj.parent
    #vNode = getVisibilityNode(pObjName) 
    visBone = arm.pose.bones[pVisibilityBoneName] #getVisibilityBone(pObjName)
    
    print ("VIS BONE ", visBone)
    
    #REMOVE EXISTING VISIBILITY DRIVER
    """
    animationData = obj.data.materials[0].node_tree.animation_data
    if animationData != None:
        driverList = animationData.drivers
        for dv in driverList:
            if dv.data_path.find("skinVisibilityNode_VTSP") != -1:
                driverList.remove(dv)
                break
    """
    
    animationData = obj.data.shape_keys.animation_data
    if animationData != None:
        driverList = animationData.drivers
        for dv in driverList:
            if dv.data_path.find("skinVisiblity_VTSP") != -1:
                driverList.remove(dv)
                break
    
    animationData = obj.animation_data
    if animationData != None:
        driverList = animationData.drivers
        for dv in driverList:
            if dv.data_path.find("hide_viewport") != None:
                driverList.remove(dv)
            
              
    #CONFIGURE DRIVERS DRIVER
    """
    #MATERIAL
    matDriver = vNode.outputs["Value"].driver_add("default_value")
    matDriver.driver.type = 'AVERAGE'
    #createDriverVariable("skinVisibility", "SINGLE_PROP", matDriver, pObjName, "skinVisibility")
    createDriverVariable("skinVisibility", "TRANSFORMS", matDriver, arm.name, visBone.name, None, "LOC_Y")
    """
    
    print ("VIS BONE ", visBone)
    
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

def getVisibilityBone(pObjName):
    
    obj = bpy.data.objects[pObjName]
    visBone = None
    visBoneName = None
    
    skinIDProp = armUtils.findCustomProperty(obj, "vtsk_skinID")
    if skinIDProp != "":
        visBoneName = boneVisibilityId + obj["vtsk_skinID"] #+ "_VTVISNODE"
        
        if visBoneName != "":
            obj = bpy.data.objects[pObjName]
            if obj != None:
                arm = obj.parent
                if arm != None and arm.type == "ARMATURE":
                    boneID = arm.pose.bones.find(visBoneName)
                    
                    if boneID != None:
                        visBone = arm.pose.bones[boneID]
                 
    return visBone

def createVisibilityBones(pBaseObjectName, pSkinName):
    
    visBoneName = None
    arm = bpy.data.objects[pBaseObjectName].parent
    
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    
    newBoneName = boneVisibilityId + pBaseObjectName #+ "_VTVISNODE"
    if pSkinName == "":
        visBoneName = armUtils.createNewBone(arm, newBoneName, (0,0,0), (0,0,1), False)
    else:
        oldBoneName = boneVisibilityId + pSkinName
        arm.pose.bones[oldBoneName].name = newBoneName
        visBoneName = newBoneName
    
    if visBoneName != None:
        #MOVE BONE TO VISIBLE (1)
        bpy.ops.object.mode_set(mode='POSE')
        arm.pose.bones[visBoneName].location.y = 1
        
        #MOVE BONE LAYER
        print("MOVE BONE TO LAYER ")
        armUtils.moveBoneToLayer(arm, visBoneName, 31)
    
    #SET ACTIVE OBJECT
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[pBaseObjectName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[pBaseObjectName]
    
    return visBoneName
    
def getSkinVisibility(pObjName):
    
    visible = False
    vBone = getVisibilityBone(pObjName)
    if vBone != None:
        if vBone.location.y == 1:
            visible = True
        
    return visible
           

def isMeshSkin(pObjName):
    
    skin = ""
    obj = bpy.data.objects[pObjName]
    skinID = armUtils.findCustomProperty(obj,propSkinIDName) 
    if obj.type == "MESH" and skinID != "":

        skin = obj[propSkinIDName]
        
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


def getSelectedObjectNames():
    names = []
    for o in bpy.context.selected_objects:
        if o.type == "MESH":
            names.append(o.name)
        
    return names
        
# ---------- OPERATORS ---------------------------- #

class VTOOLS_OT_selectVisibilityBones(bpy.types.Operator):
    bl_idname = "vtool.selectvisibilitybones"
    bl_label = "Select Visibility Bones"
    bl_description = "Select visibility bones from skin armature"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
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
    
class VTOOLS_OT_setSkinVisibility(bpy.types.Operator):
    bl_idname = "vtool.setskinvisibility"
    bl_label = "Toggle Visibility"
    bl_description = "Set skin visibility for all selectd objects"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    visible : bpy.props.BoolProperty(default=True)
    
    def execute(self, context):
        
        selectedObjects = []
        obj = bpy.context.object
   
        visibility = obj.hide_viewport
        
        #COLLECT OBJECTS
        if obj.hide_viewport == True:
            #FROM OUTLINER IF ACTIVE OBJECT IS HIDE
            selectedObjects = getOutlinerSelectedObjects(isOutlinerOpen())
        else:
            #FROM SCENE IF NOT
            selectedObjects = getSelectedObjectNames()

        for o in selectedObjects:
            #IF IS SKIN HAS VISIBILITY NODE
            visBone = getVisibilityBone(o)
            
            if visBone != None:
                
                #if self.visible == True:
                #ALL OBJECTS GET ACTIVE OBJECT VISIBILITY
                if visibility == True:
                    visBone.location.y = 1
                else:
                    visBone.location.y = 0
                
                visBone.keyframe_insert("location", index=1)
                armUtils.setFCurveInterpolation(o, visBone, "CONSTANT")
            
            armUtils.updateScene()
        
        return {'FINISHED'}


class VTOOLS_OT_setSkinVisibilityFromArmature(bpy.types.Operator):
    bl_idname = "vtool.setskinvisibilityfromarmature"
    bl_label = "Toggle Visibility"
    bl_description = "Set skin visibility for the skin"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    visible : bpy.props.BoolProperty(default=True)
    targetObject : bpy.props.StringProperty(default = "")
    
    def execute(self, context):
        
        arm = bpy.context.object
        visBone = getVisibilityBone(self.targetObject)
        if visBone != None:
            if self.visible == True:
                visBone.location.y = 1
            else:
                visBone.location.y = 0
            
            visBone.keyframe_insert("location", index=1)
            armUtils.setFCurveInterpolation(self.targetObject, visBone, "CONSTANT")
        
        armUtils.updateScene()
        
        return {'FINISHED'}


class VTOOLS_OT_configureSkin(bpy.types.Operator):
    bl_idname = "vtool.configureskin"
    bl_label = "Configure Skin"
    bl_description = "Skin System"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    action : bpy.props.StringProperty(default="NEW")
    
    def execute(self, context):
        
        objectNames = getSelectedObjectNames()
        
        if self.action != "RESET":
            for o in objectNames:
                obj = bpy.data.objects[o]
                if obj.parent != None:
                    arm = obj.parent
                    createVisibilityShapeKey(o)
                    #addSkinMatNodes(o)
                    isSkin = isMeshSkin(o)
                    
                    
                    #CREATE VISIBILITY BONE
                    visBoneName = None
                    if isSkin != "" and isSkin != None:
                        #IF IS SKIN RENAME OLD BONE IF NAME CHANGED
                        visBoneName = createVisibilityBones(o, obj[propSkinIDName])
                        #IF OBJECT CHANGED NAME
                        if obj.name != obj[propSkinIDName]:
                            renamePreviousFCurves(obj.name, obj[propSkinIDName])   
                    else:
                        #ADD NEW BONE 
                        print("NEW SKIN")
                        visBoneName = createVisibilityBones(o, "")
                        print("BONE NAME ", visBoneName)
                    
                    if visBoneName != None and visBoneName != "":  
                        print("ADD DRIVER") 
                        setVisibilityDriver(obj.name, visBoneName)
                    
                        
                    #SET A ID NAME FOR THE SKIN
                    obj[propSkinIDName] = obj.name
                    
                    #armUtils.updateScene()
        
        else:
            print("RESET")
            obj = bpy.context.object
            visBone = getVisibilityBone(obj.name)
            
            if visBone != None:
                #RENAME BONE
                visBoneName = boneVisibilityId + obj.name #+ "_VTVISNODE"
                visBone.name = visBoneName
                
                #RENAME FCURVES
                fCurveName = boneVisibilityId + obj["vtsk_skinID"]
                for ac in bpy.data.actions:
                    for fc in ac.fcurves:
                        if fc.data_path.find(fCurveName) != None:
                            newDataPath = fc.data_path.replace(fCurveName, visBoneName)
    
            obj["vtsk_skinID"] = obj.name
        
        
        return {'FINISHED'}
    

class VTOOLS_OT_deleteSkin(bpy.types.Operator):
    bl_idname = "vtool.deleteskin"
    bl_label = "Delete as Skin"
    bl_description = "Remove skin configuration"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
        obj = bpy.context.object
        
        if isMeshSkin(obj.name):
            #REMOVE DRIVERS
            ad = obj.animation_data
            if ad != None:
                for d in ad.drivers:
                    if d.data_path.find("hide_viewport") != -1:
                        ad.drivers.remove(d)
            
            #REMOVE FCURVES
            fCurveName = boneVisibilityId + obj["vtsk_skinID"]
            for ac in bpy.data.actions:
                for fc in ac.fcurves:
                    if fc.data_path.find(fCurveName) != -1:
                        ac.fcurves.remove(fc)
            
            #REMOVE SHAPE KEYS
            skID = obj.data.shape_keys.key_blocks.find("skinVisiblity_VTSP")
            print("SK ID ", skID)
            if skID != -1:
                obj.shape_key_remove(obj.data.shape_keys.key_blocks[skID])
                
            #REMOVE VISIBILITY BONE
            arm = obj.parent
            visBone = getVisibilityBone(obj.name)
            visBoneName = visBone.name
            if visBone != None:
                
                #SET ACTIVE OBJECT TO ARM
                bpy.data.objects[arm.name].select_set(True)
                bpy.context.view_layer.objects.active = bpy.data.objects[arm.name]
                bpy.ops.object.mode_set(mode='EDIT')
                
                arm.data.edit_bones.remove(arm.data.edit_bones[visBoneName])
                
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.data.objects[arm.name].select_set(False)
                bpy.context.view_layer.objects.active = bpy.data.objects[obj.name]
                        
            #REMOVE CUSTOM PROPERTY
            del obj[propSkinIDName]
            
                           
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
    
    def findActionInconsistency(self):
        error = False
        arm = bpy.context.object.parent
        animData = arm.animation_data 
        if animData!= None:
            mainAction = animData.action
            if mainAction != None:
                for o in bpy.context.selected_objects:
                    if o.type == "MESH":
                        tmpArm = o.parent
                        if tmpArm.animation_data != None:
                            if mainAction != tmpArm.animation_data.action:
                                error = True
                                break
                        else:
                            error = True
        return error
    
    def drawMeshPanel(self, pContext, pObj, pLayout):
        
        obj = pObj
        objName = obj.name
        layout = pLayout
        
        row = layout.row()
        row.use_property_split = True
        
        box = layout.box()
        row = box.row(align=True)
        
        if obj["vtsk_skinID"] == obj.name:
            
            box.operator(VTOOLS_OT_deleteSkin.bl_idname,text="Remove Skin")
            #row.label(text="", icon = "DECORATE_KEYFRAME")
            
            objectParent = bpy.context.object.parent
            row = box.row(align=True)
            if objectParent != None:
                if objectParent.type == "ARMATURE":
                    row.template_ID(bpy.context.object.parent.animation_data, "action")
                    if self.findActionInconsistency() == True:
                        op = row.operator(VTOOLS_OT_linkSkinActions.bl_idname,text="", icon="ERROR")
            
            box = layout.box()            
            visBone = getVisibilityBone(objName)
            if visBone != None:
                row = box.row(align = True)
                row.prop(visBone, "location", index=1, text="Visible")

                visible = getSkinVisibility(objName)
                if visible == False:
                    op = row.operator(VTOOLS_OT_setSkinVisibility.bl_idname,text="", icon = "HIDE_ON")
                    op.visible = False
                else:
                    op = row.operator(VTOOLS_OT_setSkinVisibility.bl_idname,text="", icon = "HIDE_OFF")
                    op.visible = True
            
                row.operator(VTOOLS_OT_selectVisibilityBones.bl_idname, text="", icon = "EYEDROPPER")
        else:
            op = box.operator(VTOOLS_OT_configureSkin.bl_idname,text="Reset Skin")
            op.action = "RESET"
        
    def drawArmaturePanel(self, context, pObj, pLayout):
        
        layout = pLayout
        obj = pObj
        obj = bpy.context.object
        
        layout.menu("VTOOLS_MT_armatureSkins")
        
        """
        if obj.type == "ARMATURE":
            layout = self.layout
            layout.label(text="Skins Visibility")
            
            box = layout.box()
            for child in obj.children:
                if isMeshSkin(child.name) != "":
                    childName = child.name
                    visible = getSkinVisibility(childName)
                    visBone = getVisibilityBone(childName)
                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.label(text=childName)
                    row.prop(visBone, "location", index=1, text="")
                    
                    if visible == False:
                        op = row.operator(VTOOLS_OT_setSkinVisibilityFromArmature.bl_idname,text="", icon = "HIDE_ON")
                        op.visible = True
                        op.targetObject = childName
                    else:
                        op = row.operator(VTOOLS_OT_setSkinVisibilityFromArmature.bl_idname,text="", icon = "HIDE_OFF")
                        op.visible = False
                        op.targetObject = childName
        """
            
    @classmethod
    def poll(cls, context):
        return (context)
    
    def draw(self,context):
        visibleText = "Visible"
        obj = bpy.context.object
        objName = obj.name
        layout = self.layout
        #layout.use_property_split = True
        #layout.use_property_decorate = True
        
        isSkin = isMeshSkin(objName)
        if isSkin != "" and isSkin != None:
            self.drawMeshPanel(context, obj, layout)
            
        elif obj.type == "MESH":
            op = layout.operator(VTOOLS_OT_configureSkin.bl_idname,text="Set as Skin")
            op.action = "NEW"
        elif obj.type == "ARMATURE":
            self.drawArmaturePanel(context, obj, layout)
            

        #layout.prop(obj, "skinVisibility", text=visibleText, toggle=True) 
        
        #layout.prop(getVisibilityKey(obj.name), "value")
         
# ------------- MENU --------------------#

class VTOOLS_MT_armatureSkins(bpy.types.Menu):
    bl_label = "Skins"
    #bl_idname = "VTOOLS_MT_textureImageNodes"


    def draw(self, context):
        obj = bpy.context.object
        
        if obj.type == "ARMATURE":
            layout = self.layout
            
            for child in obj.children:
                if isMeshSkin(child.name) != "":
                    childName = child.name
                    visible = getSkinVisibility(childName)
                    visBone = getVisibilityBone(childName)
                    row = layout.row(align=True)
                    row.label(text=childName)
                    row.prop(visBone, "location", index=1, text="")
                    
                    if visible == False:
                        op = row.operator(VTOOLS_OT_setSkinVisibilityFromArmature.bl_idname,text="", icon = "HIDE_ON")
                        op.visible = True
                        op.targetObject = childName
                    else:
                        op = row.operator(VTOOLS_OT_setSkinVisibilityFromArmature.bl_idname,text="", icon = "HIDE_OFF")
                        op.visible = False
                        op.targetObject = childName

                    layout.separator()
                    """
                    tn = obj.data.materials[0].node_tree.nodes[tnName]
                    op = layout.operator(VTOOLS_OT_createSprite.bl_idname, text=tn.image.name) 
                    op.selectedTexNode = tn.image.name   
                    """
# ------------- REGISTER ---------------------#

classes = (VTOOLS_PT_skinSystem,VTOOLS_OT_configureSkin, VTOOLS_OT_setSkinVisibilityFromArmature, VTOOLS_OT_setSkinVisibility, VTOOLS_OT_linkSkinActions, VTOOLS_OT_selectVisibilityBones, VTOOLS_OT_deleteSkin, VTOOLS_MT_armatureSkins, )
    

def register_skinSystem():
    for cls in classes:
        bpy.utils.register_class(cls)

    #bpy.types.Object.isMeshSkin = bpy.props.BoolProperty(default = False)
    
def unregister_skinSystem():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    #del bpy.types.Object.isMeshSkin
if __name__ == "__main__":
    #unregister()
    register_skinSystem()
    
