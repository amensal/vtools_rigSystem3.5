import bpy

#-- DEF CALLBACKS ---#

    
def cb_selectPaintingLayer(self,value):
    
    return None
    
                

def cb_setLayerVisibilty(self, value):
    
    return None
        

def cb_renamePaintingLayer(self, value):

    return None


# --- DEF --- #
def getSelectedChainList():
    item = None
    chainSelected = bpy.context.object.vtIKFKCollection_ID
    item = bpy.context.object.vtIKFKCollection[chainSelected]
    return item

def rigUIAddChain(pArmName, pSocketBoneName):
    
    layerID = -1
    if pSocketBoneName != None:
        if pSocketBoneName != "":
            cName = pSocketBoneName.replace("SOCKETCHAIN-", "")
            newChain = bpy.context.object.vtIKFKCollection.add()
            newChain.socketName = pSocketBoneName
            newChain.chainName = cName
            newChain.armatureName = pArmName
            newChain.name = cName
            newChain.visibleIK = True
            newChain.visibleFK = True
            newChain.visibleFR = True
            
            
    return layerID

def findCustomProperty(pBone, pWildCat):
        
    id = ""
    
    for k in pBone.keys():
        if k.find(pWildCat) != -1:
            id = k
            break
    
    return id

def setChainVisibility(pVisible, pType):
    
    arm = bpy.context.object
    bonesFound = []
    if arm != None:
        
        strToFind = ""
        
        if pType == "IK":
            strToFind = "ikTarget"
        elif pType == "FK":
            strToFind = "FKChain"
        elif pType == "FR":
            strToFind = "FreeChain"
            
        if arm.type == "ARMATURE":
            bpy.ops.object.mode_set(mode='POSE')
            chainItem = getSelectedChainList()
            if chainItem != None:
                socketBoneName = chainItem.socketName
                for b in arm.pose.bones:
                    customProp = findCustomProperty(b, "chainSocket")
                    if customProp != "":
                        if b[customProp] == chainItem.socketName:
                            if b.name.find(strToFind) != -1:
                                b.bone.hide = pVisible
                                b.bone.select = pVisible
                                
                                if pVisible == False:
                                    arm.data.bones.active = bpy.context.object.data.bones[b.name]
                                bonesFound.append(b.name)

                
         
    return True

def removeChain(pSocketName):
    
    chainList = bpy.context.object.vtIKFKCollection
    for chain in chainList:
        if chain.socketName == pSocketName:
            chainList.remove(chain)
            
            

# --- PAINTING LAYER TREE --- #

class VTOOLS_UL_vtIKFKChains(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        image = None
        arm = bpy.context.object
        socketFound = arm.pose.bones.find(item.socketName)
        if item.armatureName == arm.name:
            row = layout.row(align=True)
            row.prop(item, "chainName", text="", emboss=False,  icon="TRIA_RIGHT" )


    def filter_items(self, context, data, propname):        
        collec = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, collec, "chainName",
                                                          reverse=self.use_filter_sort_reverse)
        return flt_flags, flt_neworder


        
class VTOOLS_CC_vtIKFKchainsCollection(bpy.types.PropertyGroup):
       
    chainName : bpy.props.StringProperty(default='', update = cb_renamePaintingLayer)
    name : bpy.props.StringProperty(default='', update = cb_renamePaintingLayer)
    chainID : bpy.props.IntProperty()
    socketName : bpy.props.StringProperty(default="")
    armatureName : bpy.props.StringProperty(default="")
    visible : bpy.props.BoolProperty(default=True, update=cb_setLayerVisibilty)
    visibleIK : bpy.props.BoolProperty(default=True)
    visibleFK : bpy.props.BoolProperty(default=True)
    visibleFR : bpy.props.BoolProperty(default=True)


# -------- OPERATOR -------------- #

    
class VTOOLS_OP_removeChainFromList(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.removechainfromlist"
    bl_label = "Remove selected chain from list"
    bl_description = "Remove selected chain from list not any bone from armature"
    
    def execute(self, context):
        
        chainSelected = bpy.context.object.vtIKFKCollection_ID
        bpy.context.object.vtIKFKCollection.remove(chainSelected)
        return {'FINISHED'}

class VTOOLS_OP_addChainFromSelected(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.addchainfromselected"
    bl_label = "Add Chain to List"
    bl_description = "Add a chain to the list from a selected IK/FK chain"
    
    def execute(self, context):
        
        activeBone = bpy.context.object.pose.bones[bpy.context.active_bone.name]
        customProp = findCustomProperty(activeBone, "chainSocket")
        if customProp != "":
            rigUIAddChain(bpy.context.object.name, activeBone[customProp])
            
        return {'FINISHED'}
    
class VTOOLS_OP_showChain(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.showchain"
    bl_label = "Show selected chain"
    bl_description = "Show selected chain from active chain"
    
    action : bpy.props.StringProperty(default="IK")
    
    def execute(self, context):
        
        chain = getSelectedChainList()
        if chain != None:
            propName = "visible" + self.action
            visibility = getattr(chain, propName)
            setChainVisibility(visibility, self.action)
            chain[propName] = not visibility
            
        return {'FINISHED'}

# -------- PANEL ----------------#

class VTOOLS_PT_vtRigUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "IK/FK Chains"
    #bl_category = 'Rig vTools'
    bl_parent_id = "VTOOLS_PT_ikfkControls"
    bl_options = {'HIDE_HEADER'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self,context):
        
        arm = bpy.context.object
        
        if arm.type == "ARMATURE" and bpy.context.mode == "POSE":    
            layout = self.layout
            layout.label(text="IK/FK Chains Visibility")
            row = layout.row()
            row.template_list('VTOOLS_UL_vtIKFKChains', "chainID ", context.object, "vtIKFKCollection", context.object, "vtIKFKCollection_ID", rows=4)
            #row.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
            
            
            col = row.column(align=True)
            col.scale_x = 0.33
            op = col.operator(VTOOLS_OP_showChain.bl_idname, text="IK")      
            op.action = "IK"
            
            op = col.operator(VTOOLS_OP_showChain.bl_idname, text="FK")      
            op.action = "FK"
            
            op = col.operator(VTOOLS_OP_showChain.bl_idname, text="FR")      
            op.action = "FR"
            
            col.separator()
            col.operator(VTOOLS_OP_removeChainFromList.bl_idname, text="", icon="REMOVE")
            col.operator(VTOOLS_OP_addChainFromSelected.bl_idname, text="", icon="ADD")
            
        


# ----- REGISTER -------------#


def register():
    
    bpy.utils.register_class(VTOOLS_PT_vtRigUI)
    bpy.utils.register_class(VTOOLS_UL_vtIKFKChains)
    bpy.utils.register_class(VTOOLS_CC_vtIKFKchainsCollection)
    bpy.utils.register_class(VTOOLS_OP_showChain)
    bpy.utils.register_class(VTOOLS_OP_removeChainFromList)
    bpy.utils.register_class(VTOOLS_OP_addChainFromSelected)
    
    bpy.types.Object.vtIKFKCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_vtIKFKchainsCollection)
    bpy.types.Object.vtIKFKCollection_ID = bpy.props.IntProperty(update=cb_selectPaintingLayer, default = -1)

    return {'FINISHED'}

def unregister():
    
    bpy.utils.unregister_class(VTOOLS_PT_vtRigUI)
    bpy.utils.unregister_class(VTOOLS_UL_vtIKFKChains)
    bpy.utils.unregister_class(VTOOLS_CC_vtIKFKchainsCollection)
    bpy.utils.unregister_class(VTOOLS_OP_showChain)
    bpy.utils.unregister_class(VTOOLS_OP_removeChainFromList)
    bpy.utils.unregister_class(VTOOLS_OP_addChainFromSelected)
    
    del bpy.types.Object.vtIKFKCollection
    del bpy.types.Object.vtIKFKCollection_ID
    

    return {'FINISHED'}

if __name__ == "__main__":
    #unregister()
    register()
