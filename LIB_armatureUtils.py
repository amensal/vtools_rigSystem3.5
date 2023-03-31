import bpy

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