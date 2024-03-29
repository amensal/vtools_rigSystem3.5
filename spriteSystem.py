import bpy
import importlib
import os
#armUtils = bpy.data.texts["LIB_armatureUtils"].as_module()

if "LIB_armatureUtils" in locals():
    importlib.reload(LIB_armatureUtils)
else:
    from vtools_rigSystem import LIB_armatureUtils
    importlib.reload(LIB_armatureUtils)


armUtils = LIB_armatureUtils


from bpy_extras.image_utils import load_image
from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import AddObjectHelper
from bpy.props import (StringProperty, BoolProperty, EnumProperty, FloatProperty,CollectionProperty,)


# ------------- LOCAL VARIABLES ---------- #ç

propSpriteIDName = "vtsp_spriteID"
spriteNodeListNames = ["mapping_VTSP", "uv_VTSP", "XPos_VTSP", "YPos_VTSP", "combine_VTSP", "invert_VTSP"]

# ------------  DEF ------------- #

def loadSprite(pFilePath):
    sprite = None
    return sprite

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

def findNodeByImage(pObjectName, pImageName):
    node = None
    obj = bpy.data.objects[pObjectName]
    
    if (len(obj.data.materials) > 0):
        mat = obj.data.materials[0]
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE":
                if n.image.name == pImageName:
                    node = n
                    break
                
    return node


def findNodeListByType(pObjectName, pType):
    
    obj = bpy.data.objects[pObjectName]
    nodeList = []
    
    if (len(obj.data.materials) > 0):
        mat = obj.data.materials[0]
        for n in mat.node_tree.nodes:
            if n.type.find(pType) != -1:
                nodeList.append(n.name)
    
    return nodeList
    
def setAsSprite(pObjName, pTexNode):
    
    obj = bpy.data.objects[pObjName]
    
    if pTexNode.image != None:
            
        #CREATE CUSTOM PROPERTIES
        obj[propSpriteIDName] = pObjName
        obj["vtsp_columns"] = 1
        obj["vtsp_rows"] = 1
        obj["vtsp_fps"] = 12
        obj["vtsp_stepX"] = 0.5
        obj["vtsp_stepY"] = 0.5
        obj["vtsp_image"] = pTexNode.image.name
        
        #LIBRARY OVERRIDE
        obj.property_overridable_library_set('["vtsp_columns"]', True)
        obj.property_overridable_library_set('["vtsp_rows"]', True)
        obj.property_overridable_library_set('["vtsp_fps"]', True)
        obj.property_overridable_library_set('["vtsp_stepX"]', True)
        obj.property_overridable_library_set('["vtsp_stepY"]', True)
        
        #CONFIGURE CUSTOM PROPERTIES   
        cpStepX = obj.id_properties_ui("vtsp_stepX")
        cpStepX.update(step = 0.01)
        
        cpStepY = obj.id_properties_ui("vtsp_stepY")
        cpStepY.update(step = 0.01)
        
        cpColumns = obj.id_properties_ui("vtsp_columns")
        cpColumns.update(max = 16)
        cpColumns.update(min = 1)
        cpColumns.update(default = 1)
        cpColumns.update(step = 1)
        
        cpRows = obj.id_properties_ui("vtsp_rows")
        cpRows.update(max = 16)
        cpRows.update(min = 1)
        cpRows.update(default = 1)
        cpRows.update(step = 1)
        
        cpfps = obj.id_properties_ui("vtsp_fps")
        cpfps.update(max = 60)
        cpfps.update(min = 1)
        cpfps.update(default = 12)
        cpfps.update(step = 1)
        
        #CREATE SPRITE TEXTURE
        textureName = "VTSP_TEX_" + obj[propSpriteIDName] + "_" + pTexNode.image.name
        newTexture = bpy.data.textures.new(textureName, type = "IMAGE")
    
def createSpriteControlPanel():
    spritePlaneName = None
    
    #ADD OBJECT
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0.5, -0.5, 0), scale=(1, 1, 1))
    spritePlane = bpy.context.object
    
    #RENAME
    spritePlaneName = spritePlane.name + "_VTSP"
    spritePlane.name = spritePlaneName
    
    #CREATE CUSTOM PROPERTIES
    spritePlane["vtsp_columns"] = 1
    spritePlane["vtsp_rows"] = 1
    spritePlane["vtsp_fps"] = 12
    
    
    #CONFIGURE CUSTOM PROPERTIES
    cpColumns = spritePlane.id_properties_ui("vtsp_columns")
    cpColumns.update(max = 16)
    cpColumns.update(min = 1)
    cpColumns.update(default = 1)
    cpColumns.update(step = 1)
    
    cpRows = spritePlane.id_properties_ui("vtsp_rows")
    cpRows.update(max = 16)
    cpRows.update(min = 1)
    cpRows.update(default = 1)
    cpRows.update(step = 1)
    
    
    cpfps = spritePlane.id_properties_ui("vtsp_fps")
    cpfps.update(max = 60)
    cpfps.update(min = 1)
    cpfps.update(default = 12)
    cpfps.update(step = 1)

    
    return spritePlaneName

def removeSpriteNodes(pMat):
    mat = pMat
    for nName in spriteNodeListNames: 
        if mat.node_tree.nodes.find(nName) != -1:
            mat.node_tree.nodes.remove(mat.node_tree.nodes[nName])
         
def configureSpriteMaterial(pObjBaseName, pTexNode, pShaderNode ):
    spMat = None
    obj = bpy.data.objects[pObjBaseName]
    mat = obj.data.materials[0]
    texNode = pTexNode
    shaderNode = pShaderNode
    
    #MAKE UNIQUE MATERIAL    
    if mat.users > 1:
        obj.data.materials[0] = mat.copy()
        mat = obj.data.materials[0]
        texNode = findNodeByImage(pObjBaseName, pTexNode.image.name)
        shaderNode = findNodeByType(pObjBaseName, "BSDF")
    
    #REMOVE EXISTING NODES
    removeSpriteNodes(mat)
    
            
    #CONFIGURE MATERIAL
    mat.blend_method = "CLIP"
    mat.shadow_method = "CLIP"
    
    #CREATE UV MAPPING AND UV NDOES
    mappingNode = mat.node_tree.nodes.new(type="ShaderNodeMapping")
    mappingNode.vector_type = "POINT"
    mappingNode.name = "mapping_VTSP"
    uvNode = mat.node_tree.nodes.new(type="ShaderNodeUVMap")
    uvNode.uv_map = obj.data.uv_layers[0].name
    uvNode.name = "uv_VTSP"
    
    #CRATE VALUE NODES FOR DRIVES
    xValueNode = mat.node_tree.nodes.new(type="ShaderNodeValue")
    xValueNode.name = "XPos_VTSP"
    yValueNode = mat.node_tree.nodes.new(type="ShaderNodeValue")
    yValueNode.name = "YPos_VTSP"
    combineVector = mat.node_tree.nodes.new(type="ShaderNodeCombineXYZ")
    combineVector.name = "combine_VTSP"
    invertMath = mat.node_tree.nodes.new(type="ShaderNodeMath")
    invertMath.operation = "MULTIPLY"
    invertMath.inputs[1].default_value = 1
    invertMath.name = "invert_VTSP"
    

    #CONNECT NODES
    if texNode != None:
        mat.node_tree.links.new(mappingNode.outputs[0], texNode.inputs["Vector"])  
        mat.node_tree.links.new(uvNode.outputs["UV"], mappingNode.inputs["Vector"])
        mat.node_tree.links.new(combineVector.outputs["Vector"], mappingNode.inputs["Location"])
        mat.node_tree.links.new(xValueNode.outputs["Value"], combineVector.inputs["X"])
        mat.node_tree.links.new(invertMath.outputs["Value"], combineVector.inputs["Y"])    
        mat.node_tree.links.new(yValueNode.outputs["Value"], invertMath.inputs["Value"])    
        """
        if shaderNode != None:
            mat.node_tree.links.new(texNode.outputs["Alpha"], shaderNode.inputs["Alpha"])
        """
        
    return spMat

def addSpriteControlBone(pArmName, pObjName):
    
    obj = bpy.data.objects[pObjName]
    arm = bpy.data.objects[pArmName]
    spriteBone = None
    newBoneName = "spriteControl_" + obj[propSpriteIDName]
    boneFound = False
    
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    
    for n in arm.pose.bones:
        if n.name == newBoneName:
            boneFound = True
            break
        
    if boneFound == False:
        ulSprite = arm.vtRigSpritesCollection
        ulSpriteID = arm.vtRigSpritesCollection_ID
        xBasePos = 1.2*len(ulSprite)
        spriteBone = armUtils.createNewBone(arm, newBoneName, (xBasePos,0,-2), (xBasePos,0,-1), False)
    else:
        print("bone found")
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[pObjName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[pObjName]
    
    return newBoneName
    
def getSpriteControlBone(pObjName):
    
    spriteBone = None
    obj = bpy.data.objects[pObjName]
    spriteBoneName = "spriteControl_" + obj[propSpriteIDName]
    arm = obj.parent
    
    if arm != None:
        boneID = arm.pose.bones.find(spriteBoneName)
        if boneID != -1:
            spriteBone = arm.pose.bones[boneID]
    
    return spriteBone

def getSelectedSpriteItem(pArm):
    
    spriteItem = None
    
    ulSprite = pArm.vtRigSpritesCollection
    ulSpriteID = pArm.vtRigSpritesCollection_ID
    numItems = len(ulSprite)
    
    if ulSpriteID != -1 and ulSpriteID < numItems  and numItems > 0:
        spriteItem = ulSprite[ulSpriteID]
    
    return spriteItem

def createSpriteArmature(pSpriteGeoName):
    arm = None
    pSpriteGeo = bpy.data.objects[pSpriteGeoName]
    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    arm = bpy.context.object
    arm.name = pSpriteGeo.name + "ARM"
    arm.parent = pSpriteGeo
    arm.location -= arm.parent.location
        
    for n in arm.pose.bones:
        n.name = "spControl.000"
        n.rotation_mode = "XYZ"
    
    return arm.name


def createSpriteShapeKeys(pObjBaseName):
    
    obj = bpy.data.objects[pObjBaseName]
    if obj.data.shape_keys == None:
        obj.shape_key_add(name="Basis")
    
    #REMOVE EXISTING DRIVER AND SHAPE KEY
    animData = obj.data.shape_keys.animation_data
    if animData != None:
        driverList = obj.data.shape_keys.animation_data.drivers
        for dv in driverList:
            if dv.data_path.find("XPos_VTSP") or dv.data_path.find("YPos_VTSP") :
                driverList.remove(dv)
                break
    
    #FIND  SHAPE KEYS
    xPosFound = False             
    yPosFound = False             
    for sk in obj.data.shape_keys.key_blocks:
        if sk.name.find("XPos_VTSP") != -1:
            xPosFound = True
        elif sk.name.find("YPos_VTSP") != -1:
            yPosFound = True
                
            
    #ADD SHAPE KEY IF NOT FOUND
    if xPosFound == False:
        obj.shape_key_add(name="XPos_VTSP")
    if yPosFound == False:
        obj.shape_key_add(name="YPos_VTSP")
    

    return {'FINISHED'}

def createDriverVariable(pName, pTransType, pDriver, pArmName, pControlBoneName):
    
    tmpV = pDriver.driver.variables.new()
    tmpV.name = pName
    tmpV.type = 'TRANSFORMS'
    tmpV.targets[0].id = bpy.data.objects[pArmName]
    tmpV.targets[0].bone_target = pControlBoneName
    tmpV.targets[0].transform_type = pTransType
    tmpV.targets[0].transform_space = "LOCAL_SPACE"
    
def setDrivers(pArmName, pObjBaseName, pControlBoneName):
    driver = None
    
    obj = bpy.data.objects[pObjBaseName]
    mat = obj.data.materials[0]
    
    #REMOVE EXISTING MATERIAL DRIVERS
    animData = mat.node_tree.animation_data
    if animData != None:
        driverList = mat.node_tree.animation_data.drivers
        for dv in driverList:
            driverList.remove(dv)
                
    #SHAPE KEY DRIVERS
    for sk in obj.data.shape_keys.key_blocks:
        if sk.name == "XPos_VTSP":
            
            tmpD = sk.driver_add("value")
            tmpD.driver.type = 'AVERAGE'
            createDriverVariable("xPos", "LOC_X", tmpD, pArmName, pControlBoneName)

            #COPY TO MATERIAL
            nodeDriver = mat.node_tree.nodes["XPos_VTSP"].outputs["Value"].driver_add("default_value")
            nodeDriver.driver.type = 'AVERAGE'
            createDriverVariable("xPos", "LOC_X", nodeDriver, pArmName, pControlBoneName)

        if sk.name == "YPos_VTSP":
            
            tmpD = sk.driver_add("value")
            tmpD.driver.type = 'AVERAGE'
            createDriverVariable("zPos", "LOC_Y", tmpD, pArmName, pControlBoneName)

            #COPY TO MATERIAL    
            nodeDriver = mat.node_tree.nodes["YPos_VTSP"].outputs["Value"].driver_add("default_value")
            nodeDriver.driver.type = 'AVERAGE'
            createDriverVariable("zPos", "LOC_Y", nodeDriver, pArmName, pControlBoneName)
    
    
    return driver


def isSprite(pObject):
    sprite = False
    
    isSprite = armUtils.findCustomProperty(pObject,propSpriteIDName) 
    if bpy.context.object.type == "MESH" and isSprite != "":
        sprite = True
    
    return sprite



# ------------- MENU --------------------#

class VTOOLS_MT_textureImageNodes(bpy.types.Menu):
    bl_label = "Set As Sprite"
    #bl_idname = "VTOOLS_MT_textureImageNodes"


    def draw(self, context):
        arm = bpy.context.object
        
        layout = self.layout
        layout.operator_context = "EXEC_DEFAULT";
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                textureNodes = findNodeListByType(obj.name, "TEX_IMAGE")
                for tnName in textureNodes:
                    tn = obj.data.materials[0].node_tree.nodes[tnName]
                    if tn.image != None:
                        op = layout.operator(VTOOLS_OT_createSprite.bl_idname, text=tn.image.name) 
                        op.selectedTexNode = tn.image.name
                        op.targetObjectName = obj.name
    
# ---------- OPERATORS ---------------------------- #

        
class VTOOLS_OT_createSprite(bpy.types.Operator):
    bl_idname = "vtool.createsprite"
    bl_label = "Create Sprite"
    bl_description = "Create a sprite contol using the image from selected mesh"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    selectedTexNode : bpy.props.StringProperty(default="")
    targetObjectName : bpy.props.StringProperty(default="")
    
    def execute(self, context):

        if self.targetObjectName != "" and bpy.data.objects.find(self.targetObjectName) != -1:
    
            obj = bpy.data.objects[self.targetObjectName]
            arm = obj.parent

            if obj.type == "MESH" and arm.type == "ARMATURE":
                objName = obj.name
                spArmName = arm.name
                texNode = None
                
                #FIND SHADER AND TEXTURE NODE
                if self.selectedTexNode == "":
                    texNode = findNodeByType(objName, "TEX_IMAGE")
                else:
                    texNode = findNodeByImage(objName, self.selectedTexNode)
                    
                shaderNode = findNodeByType(objName, "BSDF")
                
                #print("NODES TEX ", texNode, " SHADER ", shaderNode)
                
                #CREATE SPRITE
                if len(obj.data.materials) > 0 and texNode != None and shaderNode != None:
                    setAsSprite(objName, texNode)
                    configureSpriteMaterial(objName, texNode, shaderNode)
                    spControlBoneName = addSpriteControlBone(spArmName, objName)
                    createSpriteShapeKeys(objName)
                    setDrivers(spArmName, objName, spControlBoneName)
                    
                    #ADD SPRITE TO ULLIST
                    ulSprite = arm.vtRigSpritesCollection
                    ulSpriteID = arm.vtRigSpritesCollection_ID
                    
                    newSpriteItem = ulSprite.add()
                    newSpriteItem.spriteImageName = texNode.image.name
                    newSpriteItem.spriteMeshName = objName
                    newSpriteItem.spriteBoneName = spControlBoneName
                    
                    ulSpriteID = len(ulSprite) - 1
                    
                    
                    
            bpy.context.view_layer.objects.active = bpy.data.objects[objName]
                        
        return {'FINISHED'}


class VTOOLS_OT_setSpriteImage(bpy.types.Operator):
    bl_idname = "vtool.setspriteimage"
    bl_label = "Create Sprite"
    bl_description = "Create a sprite contol using the image from selected mesh"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
        
        obj = bpy.context.object
        
        #GET TEXTURE
        texNode = findNodeByImage(obj.name, obj["vtsp_image"])
        textureName = "VTSP_TEX_" + obj[propSpriteIDName] + "_" + texNode.image.name
        if bpy.data.textures.find(textureName) == -1:
            tex = bpy.data.textures.new(textureName, type = "IMAGE")
        
        tex = bpy.data.textures[textureName]
        tex.extension = "CLIP"
        tex.repeat_x = 1
        tex.repeat_y = 1
        tex.use_alpha = False
        
        #GET IMAGE FROM SELECTED SPRITE
        
        if texNode != None:
            if texNode.image != None:
                tex.image = None
                tex.image = texNode.image
                
 
        #armUtils.updateScene()
            
        return {'FINISHED'}
    
class VTOOLS_OT_spriteAutokey(bpy.types.Operator):
    bl_idname = "vtool.spriteautokey"
    bl_label = "Autokey"
    bl_description = "Animation auto keyframe depending on settings"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
        
        obj = bpy.context.object
        objName = obj.name
        spriteBone = getSpriteControlBone(obj.name)
        arm = obj.parent
        
        #REMOVE ANIMATION DATA 
        
        
        #SETTINGS
        cols = obj["vtsp_columns"]
        rows = obj["vtsp_rows"]
        fps = obj["vtsp_fps"]
        fpsScene = bpy.context.scene.render.fps
        
        colDist = 1/cols
        rowDist = 1/rows
        step = int(fpsScene / fps)
        
        stepCont = 0
        insertFrame = bpy.context.scene.frame_start
        
        for i in range(0,rows):
            j = 0
            for j in range(0,cols):
                
                #BONE POSITION
                spriteBone.location.x = j*colDist
                spriteBone.location.z = i*rowDist
                #INSERT KEYFRAME
                spriteBone.keyframe_insert("location", index=0, frame=insertFrame)
                spriteBone.keyframe_insert("location", index=2, frame=insertFrame)
                
                insertFrame += step
                
        armUtils.setFCurveInterpolation(arm,  spriteBone.name, "CONSTANT")        
            
        return {'FINISHED'}
 
#MOVE BONE DEPENDING ON ROW COLUMNS AUTOMATICALLY
class VTOOLS_OT_moveSpriteControlBone(bpy.types.Operator):
    bl_idname = "vtool.movespritecontrolbone"
    bl_label = "Move Sprite Control"
    bl_description = "Move sprite control bone depending on options"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    boneName : bpy.props.StringProperty()
    bonePos : bpy.props.StringProperty()
    action : bpy.props.StringProperty()
    targetMesh : bpy.props.StringProperty()
    
    def execute(self, context):
        
        arm = bpy.context.object
        obj = bpy.data.objects[self.targetMesh]

        if arm != None:
            
            #COLLECT PROPERTIES
            cols = obj["vtsp_columns"]
            rows = obj["vtsp_rows"]
            
            stepX = obj["vtsp_stepX"]
            stepY = obj["vtsp_stepY"]
            
            #MOVE BONE
            if arm.type == "ARMATURE":
                
                if arm.pose.bones.find(self.boneName) != -1:
                    controlBone = arm.pose.bones[self.boneName]
                    
                    if self.bonePos == "X_axi":
                        if self.action == "ADD":
                            controlBone.location.x += stepX   
                        elif self.action == "REMOVE":
                            controlBone.location.x -= stepX
                    elif self.bonePos == "Y_axi": 
                        if self.action == "ADD":
                            controlBone.location.y += stepY
                        elif self.action == "REMOVE":
                            controlBone.location.y -= stepY
                    
                    #CONTROL COLS AND ROW MAX
                    if  controlBone.location.x*cols > cols:
                        controlBone.location.x = 1
                    elif controlBone.location.x < 0:
                        controlBone.location.x = 0
                        
                    if  controlBone.location.z*rows > rows:
                        controlBone.location.z = 1
                    elif controlBone.location.z < 0:
                        controlBone.location.z = 0
            
        return {'FINISHED'}

class VTOOLS_OT_selectSpriteControlBones(bpy.types.Operator):
    bl_idname = "vtool.selectspritecontrolbones"
    bl_label = "Select Visibility Bones"
    bl_description = "Select visibility bones from skin armature"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    allBones : bpy.props.BoolProperty(default=False)
    
    def execute(self, context):
        selectedObjectNames = armUtils.getSelectedObjectNames()
        arm = bpy.context.object
        
        print("select")
        if arm.type == "ARMATURE":
            #IF ALL BONES SELECT ALL CONTROL BONES
            if self.allBones == True:
                print("all bones")    
                for bone in arm.pose.bones:
                    wildCard = "spriteControl_"
                    print(bone.name)
                    if bone.name.find(wildCard) != -1:
                        print("select")
                        bone.bone.select = True
            else:
                #IF NOT ALL, SELECT ONLY SELECTED SPRITE
                spriteItem = getSelectedSpriteItem(arm)
                if spriteItem != None:
                    if arm.pose.bones.find(spriteItem.spriteBoneName) != -1:
                        arm.pose.bones[spriteItem.spriteBoneName].bone.select = True
                        #armUtils.selectBonesByName(arm,wildCard)
                   
        return {'FINISHED'}

class VTOOLS_OT_calculateSpriteAnimationStep(bpy.types.Operator):
    bl_idname = "vtool.calculatespriteanimstep"
    bl_label = "Calculate Sprite Animation Step"
    bl_description = "Calculate Sprite Cell distance based on colums and rows"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self, context):
        obj = bpy.context.object
        arm = obj.parent

        #COLLECT PROPERTIES
        cols = obj["vtsp_columns"]
        rows = obj["vtsp_rows"]
        
        obj["vtsp_stepX"] = 1/cols
        obj["vtsp_stepY"] = 1/rows
            
               
        return {'FINISHED'}

class VTOOLS_OT_deleteSprite(bpy.types.Operator):
    bl_idname = "vtool.deletesprite"
    bl_label = "Remove as sprite"
    bl_description = "Remove sprite configuration"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    targetObjectName : bpy.props.StringProperty(default="")
    
    def execute(self, context):
        
        arm = bpy.context.object
        spriteItem = getSelectedSpriteItem(arm)
        controlBone = None
        
        if bpy.data.objects.find(self.targetObjectName) != -1:
            
            bpy.ops.object.mode_set(mode='EDIT')
            if arm.data.edit_bones.find(spriteItem.spriteBoneName) != -1:
                controlBone = arm.data.edit_bones[spriteItem.spriteBoneName]
                arm.data.edit_bones.remove(controlBone)
            bpy.ops.object.mode_set(mode='POSE')
                
            ulSprite = arm.vtRigSpritesCollection
            ulSpriteID = arm.vtRigSpritesCollection_ID
            
            ulSprite.remove(ulSpriteID)
            ulSpriteID = -1
            
            obj = bpy.data.objects[self.targetObjectName]
            
            del obj[propSpriteIDName]
            del obj["vtsp_columns"]
            del obj["vtsp_rows"]
            del obj["vtsp_fps"]
            del obj["vtsp_stepX"]
            del obj["vtsp_stepY"]
            del obj["vtsp_image"]
            
            removeSpriteNodes(obj.data.materials[0])

               
        return {'FINISHED'}    

class VTOOLS_OT_importSpritesFromFolder(bpy.types.Operator):
    bl_idname = "vtool.importspritesfromfolder"
    bl_label = "Import Sprites from Folder"
    bl_description = "Import all sprites within a folder"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    planeOffset : bpy.props.FloatProperty()
    
    def execute(self, context):
        if os.path.isdir(bpy.context.scene.vtRig2DSpriteFolder) == True:
            armUtils.loadImagesFromFolder(bpy.context.scene.vtRig2DSpriteFolder, self.planeOffset)
               
        return {'FINISHED'}   
    

                    
# --------------- PANELS -------------------------------------------------------------- #

#UI MENU

class VTOOLS_PT_importSprite(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_parent_id = "VTOOLS_PT_rigSystem"
    bl_region_type = 'UI'
    bl_label = "VT - Sprite Tools"
    bl_category = 'Tool'
    bl_options = {'DEFAULT_CLOSED'} 
    

    @classmethod
    def poll(cls, context):
        return (context.mode == "OBJECT" or context.mode == "POSE")
    
    def draw(self,context):
        tex = None
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(bpy.context.scene, "vtRig2DSpriteFolder", text="")
        op = col.operator(VTOOLS_OT_importSpritesFromFolder.bl_idname, text="Load Sprites")
        op.planeOffset = 0.01
        
        if len(bpy.context.selected_objects) > 0 and bpy.context.object.type == "MESH":
           #layout.operator(VTOOLS_OT_createSprite.bl_idname, text="Set as Sprite")
           layout.menu("VTOOLS_MT_textureImageNodes")
           
        elif len(bpy.context.selected_objects) > 0 and bpy.context.object.type == "ARMATURE":
            
            arm = bpy.context.object
            layout.label(text="Sprites")
            layout.template_list("VTOOLS_UL_vtRigSprites", "", arm , "vtRigSpritesCollection", arm, "vtRigSpritesCollection_ID", rows=3)
            
            spriteItem = getSelectedSpriteItem(arm)
            
            if spriteItem != None:
                
                """
                layout.prop(spriteItem, "spriteImageName")
                layout.prop(spriteItem, "spriteMeshName")
                layout.prop(spriteItem, "spriteBoneName")
                """
                
                row = layout.row(align=True)
                obj = bpy.data.objects[spriteItem.spriteMeshName]
                
                op = row.operator(VTOOLS_OT_deleteSprite.bl_idname, text="Delete Sprite")
                op.targetObjectName = obj.name
                
                #CHECK IF GEOMETRY IS SPRITE
                spID = armUtils.findCustomProperty(obj,"vtsp_spriteID")
                if spID != "":
                    #box1 = layout.box()
                    #RESET SPRITE
                    op = row.operator(VTOOLS_OT_createSprite.bl_idname, text="Reset Sprite")
                    op.selectedTexNode = obj["vtsp_image"]
                
                    box2 = layout.box()
                    
                    col = box2.column(align=True)
                    
                    spCol = armUtils.findCustomProperty(obj,"vtsp_columns")
                    if spCol != "":
                        col.prop(obj, '["vtsp_columns"]', text="Columns")
                    
                    spRow = armUtils.findCustomProperty(obj,"vtsp_rows")
                    if spRow != "":
                        col.prop(obj, '["vtsp_rows"]', text="Rows")
                    
                    spFPS = armUtils.findCustomProperty(obj,"vtsp_fps")
                    if spFPS != "":
                        col.prop(obj, '["vtsp_fps"]', text="fps")
                    
                    spriteBone = arm.pose.bones[spriteItem.spriteBoneName]
                        
                    if spriteBone != None:
                        box3 = layout.box()
                        rowStep = box3.row(align=True)
                        
                        rowStep.prop(obj, '["vtsp_stepX"]', text="")
                        rowStep.prop(obj, '["vtsp_stepY"]', text="")
                        rowStep.operator(VTOOLS_OT_calculateSpriteAnimationStep.bl_idname, text="", icon ="CON_ACTION")
                        
                        col2 = box3.column(align=True)
                        
                        rowCol = col2.row(align=True)
                        
                        #BONE X PROPERTY
                        spriteCell_x = "Col " + str(int(1 + spriteBone.location.x*obj["vtsp_columns"]))
                        rowCol.prop(spriteBone, "location", index=0, text=str(spriteCell_x))
                        
                        #ADD X
                        op = rowCol.operator(VTOOLS_OT_moveSpriteControlBone.bl_idname, text="", icon='ADD')
                        op.boneName = spriteBone.name
                        op.bonePos = "X_axi"
                        op.action = "ADD"
                        op.targetMesh = obj.name
                        
                        #REMOVE X
                        op = rowCol.operator(VTOOLS_OT_moveSpriteControlBone.bl_idname, text="", icon='REMOVE')
                        op.boneName = spriteBone.name
                        op.bonePos = "X_axi"
                        op.action = "REMOVE"  
                        op.targetMesh = obj.name
                        
                        #BONE Z PROPERTY
                        rowCol2 = col2.row(align=True)                   
                        spriteCell_z = "Row " + str(int(1 + spriteBone.location.z*obj["vtsp_rows"]))
                        rowCol2.prop(spriteBone, "location", index=1, text=spriteCell_z)
                        
                        #ADD Z
                        op = rowCol2.operator(VTOOLS_OT_moveSpriteControlBone.bl_idname, text="", icon='ADD')                   
                        op.boneName = spriteBone.name
                        op.bonePos = "Y_axi"
                        op.action = "ADD"
                        op.targetMesh = obj.name
                        
                        #REMOVE Z
                        op = rowCol2.operator(VTOOLS_OT_moveSpriteControlBone.bl_idname, text="", icon='REMOVE')
                        op.boneName = spriteBone.name
                        op.bonePos = "Y_axi"
                        op.action = "REMOVE"
                        op.targetMesh = obj.name
                        
                        box4 = layout.box()
                        box4.label(text="Select Control Bones", icon="EYEDROPPER")
                        row = box4.row(align=True)
                        row.operator(VTOOLS_OT_selectSpriteControlBones.bl_idname, text="Selected")
                        op = row.operator(VTOOLS_OT_selectSpriteControlBones.bl_idname, text="All")
                        op.allBones = True
                    
# ------------ UI LIST --------------------#

class VTOOLS_UL_vtRigSprites(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        arm = bpy.context.object
        row = layout.row(align=True)
        
        row.prop(item, "spriteMeshName", text="", emboss=False) 
        #row.prop(item, "spriteImageName", text="", emboss=False) 
        #row.prop(item, "spriteBoneName", text="", emboss=False) 


    def filter_items(self, context, data, propname):        
        collec = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, collec, "spriteMeshName",
                                                          reverse=self.use_filter_sort_reverse)
        return flt_flags, flt_neworder


        
class VTOOLS_CC_vtRigSpritesCollection(bpy.types.PropertyGroup):
       
    spriteImageName : bpy.props.StringProperty(default='')
    spriteMeshName : bpy.props.StringProperty(default='')
    spriteBoneName: bpy.props.StringProperty(default='')
         
# ------------- REGISTER ---------------------#

classes = (
    VTOOLS_OT_createSprite, VTOOLS_PT_importSprite, VTOOLS_OT_setSpriteImage,
    VTOOLS_OT_moveSpriteControlBone, VTOOLS_OT_spriteAutokey,
    VTOOLS_OT_selectSpriteControlBones, VTOOLS_OT_calculateSpriteAnimationStep,
    VTOOLS_OT_deleteSprite, VTOOLS_MT_textureImageNodes,
    VTOOLS_UL_vtRigSprites, VTOOLS_CC_vtRigSpritesCollection,
    VTOOLS_OT_importSpritesFromFolder,  
     )


def register_spriteSystem():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Object.vtRigSpritesCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_vtRigSpritesCollection)
    bpy.types.Object.vtRigSpritesCollection_ID = bpy.props.IntProperty(default = -1, override={"LIBRARY_OVERRIDABLE"})
    bpy.types.Scene.vtRig2DSpriteFolder = bpy.props.StringProperty(subtype='DIR_PATH')


def unregister_spriteSystem():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Object.vtRigSpritesCollection
    del bpy.types.Object.vtRigSpritesCollection_ID
    del bpy.types.Scene.vtRig2DSpriteFolder


if __name__ == "__main__":
    #unregister()
    register_spriteSystem()