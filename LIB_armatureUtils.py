import bpy
import os
import math
import mathutils
from bpy_extras.image_utils import load_image

def updateScene():
    bpy.context.scene.frame_current += 1
    bpy.context.scene.frame_current -= 1 

def moveBoneToLayer(pArm, pSelBoneBone, pLayerDest):
        
        bpy.ops.object.mode_set(mode='POSE')
        if pSelBoneBone in pArm.pose.bones != False:
            pArm.pose.bones[pSelBoneBone].bone.layers[pLayerDest] = True
            
            cont = 0
            for l in pArm.data.bones[pSelBoneBone].layers:
                if cont != pLayerDest:
                    pArm.pose.bones[pSelBoneBone].bone.layers[cont] = False
                cont += 1
                    
def findCustomProperty(pBone, pWildCat):
        
    id = ""
    
    for k in pBone.keys():
        if k.find(pWildCat) != -1:
            id = k
            break
    
    return id

def createNewBone(pArm, pNewBoneName, pHeadLoc, pTailLoc, pDef):
    
    newBoneName = None
    bpy.ops.object.mode_set(mode='EDIT')
    
    if pArm.data.edit_bones.find(pNewBoneName) == -1:
        newBone = pArm.data.edit_bones.new(pNewBoneName)
        newBone.tail = pTailLoc
        newBone.head = pHeadLoc
        newBone.name = newBoneName = pNewBoneName
        newBone.use_deform = pDef 
    else:
        newBoneName = pNewBoneName
        
    bpy.ops.object.mode_set(mode='OBJECT') 
    
    return newBoneName

def duplicateBone(pNewBoneName, pArm, pBoneName, pParenting, pDeform):
    

    newBoneName = None    
    arm = pArm
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    
    boneId = arm.data.edit_bones.find(pBoneName)
    newBoneName = None
    
    if boneId != -1:
        oldBone = arm.data.edit_bones[boneId]
        
        newBone = arm.data.edit_bones.new(pNewBoneName)
        newBone.name = pNewBoneName
        newBone.head = oldBone.head
        newBone.tail = oldBone.tail
        newBone.matrix = oldBone.matrix
        newBone.use_deform = pUseDeform
        newBoneName = newBone.name
                
        if (pParenting == True) and (oldBone.parent != None):
            newBone.use_connect = oldBone.use_connect
            newBone.parent = oldBone.parent
    
        bpy.ops.object.mode_set(mode='EDIT')
             
    return newBoneName

def setFCurveInterpolation(pArm, pBoneName, pInterpolationType ):
    
    pDataPath = pBoneName
    arm = pArm
    if arm.animation_data != None:
        ac = arm.animation_data.action
        if ac != None:
            for fc in ac.fcurves:
                if fc.lock == False:
                    if fc.data_path.find(pDataPath) != -1:
                        for k in fc.keyframe_points:
                            k.interpolation = pInterpolationType
                            k.easing = 'AUTO'
                

def selectBonesByName(pObjectName, pArm, pWildCardName):
    
    #SELECT ARMATURE
    arm = pArm
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    #FIND AND SELECT VISIBILITY BONES
    for b in arm.data.edit_bones:
        if b.name.find(pWildCardName) != -1:
            b.select = True
            
    bpy.ops.object.mode_set(mode='OBJECT')
    #bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.data.objects[pObjectName].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[pObjectName]
                
                
def getSelectedObjectNames():
    
    selectedNames = []
    
    for o in bpy.context.selected_objects:
        selectedNames.append(o.name)
        
    return selectedNames

def crateSpritePlane(pSpriteName):
    
    spritePlane = None
    
    if bpy.data.objects.find(pSpriteName) != -1:
        obj = bpy.data.objects[pSpriteName]
        bpy.data.objects.remove(obj)

    
    bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    spritePlane = bpy.context.object
    spritePlane.name = pSpriteName
    
    return spritePlane

def placeSpritePlane(pObjName, pRotation, pImageOffset):
    
    plane = bpy.data.objects[pObjName]
    plane.rotation_euler.x = math.radians(pRotation.x)
    plane.rotation_euler.y = math.radians(pRotation.y)
    plane.rotation_euler.z = math.radians(pRotation.z)
    
    plane.location.y -= pImageOffset
    
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    
    return True

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

def createSpriteMaterial(pSpritePlane, pImage):
    
    spriteMaterial = None
    obj = bpy.data.objects[pSpritePlane]
    
    #CREATE NEW MATERIAL
    #bpy.ops.material.new()
    
    #REMOVE MATERIAL IF MATERIAL EXISTS
    
    matID = bpy.data.materials.find(pSpritePlane) 
    if matID != -1:
        matToRemove = bpy.data.materials[pSpritePlane]
        bpy.data.materials.remove(matToRemove)
    
    mat = bpy.data.materials.new(pSpritePlane)
    mat.use_nodes = True
    obj.data.materials.append(mat)
    
    """
    #ADD MATERIAL NODES
    #OUTPUT
    outputNode = mat.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    outputNode.name = "vtsp_outputShader"

    #SHADER
    shaderNode = mat.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    shaderNode.name = "vtsp_shaderNode"
    
    #SHADER LINKS
    mat.node_tree.links.new(shaderNode.outputs["BSDF"], outputNode.inputs["Surface"])
    
    #TEXTURE
    texNode = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
    texNode.name = "vtsp_texNode"
    
    #TEXTURE LINKS
    mat.node_tree.links.new(texNode.outputs["Color"], shaderNode.inputs["Base Color"]) 
    mat.node_tree.links.new(texNode.outputs["Alpha"], shaderNode.inputs["Alpha"]) 
    """     
    
    #TEXTURE
    texNode = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
    texNode.name = "vtsp_texNode"
    
    shaderNode = findNodeByType(pSpritePlane, "BSDF")
    shaderNode.name = "vtsp_shaderNode"
    
    #CONFIGURE MATERIAL
    if texNode != None and shaderNode != None:
        #CONFIGURE MATERIAL
        mat.blend_method = "CLIP"
        mat.shadow_method = "NONE"
        mat.use_backface_culling = True

        #SET IMAGE        
        texNode.image = pImage
        texNode.image.alpha_mode = "PREMUL"
        
        #LINKS
        mat.node_tree.links.new(texNode.outputs["Color"], shaderNode.inputs["Base Color"]) 
        mat.node_tree.links.new(texNode.outputs["Color"], shaderNode.inputs["Emission"]) 
        mat.node_tree.links.new(texNode.outputs["Alpha"], shaderNode.inputs["Alpha"]) 
        
    
    return spriteMaterial    
    
def loadImagesFromFolder(pFolderPath, pImageOffset):
    
    loadedImages = []
    fileList = sorted(os.listdir(pFolderPath)) #GET FOLDER FILE LIST

    placeCont = 0
    for filePath in fileList:
        if filePath.lower().endswith(".png"):
            #LOAD PNG IMAGE, else ignore
            image = load_image(filePath,pFolderPath, check_existing =True, force_reload = True )
            
            #CREATE PLANE
            spritePlaneName = os.path.splitext(filePath)[0]
            spritePlane = crateSpritePlane(spritePlaneName)

            placeSpritePlane(spritePlaneName, mathutils.Vector((90,0,0)), pImageOffset*placeCont)
            #CREATE MATERIAL
            createSpriteMaterial(spritePlane.name, image)
            
            placeCont +=1
            
    return loadedImages 