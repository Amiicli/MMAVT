import bpy

from .MMAVT_property import MMAVT_instance,MMAVT_mbody_data,MMAVT_hfem_data,MMAVT_hfem,MMAVT_mbody
from .milan_utilities import MUtil
from bpy.types import Context, Panel
from bpy.types import PropertyGroup
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty
                       )
from .mmavt_locale import *


class MMAVT_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "MMAVT"
    bl_category = "Milan Util"


    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        
        if bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE':
            return True
        return False

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        ob = context.object
        row = layout.row()
        col = row.column()
        isArmature = False
        user_lang = bpy.context.preferences.view.language

        for item in context.selected_objects:
            item:bpy.types.Object = item
            if HasItem(item):
                LOCALE_already_armature = bpy.app.translations.pgettext('{} is already an MMAVT armature').format(item.name)
                col.label(text= LOCALE_already_armature)
                isArmature = True
                break
            if item.type == 'ARMATURE':
                isArmature = True
                op = col.operator("object.rdyarm")
                op.arm_to_ready = item.name

        if isArmature == False:
            col.label(text="Select an armature to begin")
        box = layout.box()
        box.alignment = 'LEFT'

        for mmavt in bpy.context.scene.mmavt_list:
            mmavt:MMAVT_instance = mmavt
            row = box.row()
            row.scale_y = 2.5
            row.prop(mmavt,"foldout",text="",icon="DOWNARROW_HLT" if mmavt.foldout else "RIGHTARROW_THIN",emboss=False)
            rowArm = row.row()
            rowArm.prop(mmavt,"arm",text="",icon="OUTLINER_OB_ARMATURE")
            rowArm.enabled = False #TODO: Make it so you can transfer all of your values to a new armature
            row.operator("object.rmvarm",text="",icon="X").arm_to_delete = mmavt.arm.name
            if mmavt.foldout:
                canUse = mmavt.can_use_hfem
                title = box.row()
                title.alignment='LEFT'
                indent(title)
                if canUse == True:
                    title.prop(mmavt,"foldout_hfem",text="",icon="DOWNARROW_HLT" if mmavt.foldout_hfem else "RIGHTARROW_THIN",emboss=False)
                if canUse == False:
                    op = title.operator("object.instantiate_hfem_properties",text="",icon="LIGHT_SUN",emboss=True)
                    op.arm_ref = mmavt.arm.name
                title.label(text="HFEM",icon="MATSHADERBALL")
                title.prop(mmavt,"eye_usage_type",text="",emboss=True)
                if mmavt.foldout_hfem:
                    counter = 0
                    for hfem in mmavt.hfem_list:
                        if counter == 2:
                            if mmavt.eye_usage_type != 'EYE_ONLY' and mmavt.eye_usage_type != 'BOTH_SYSTEMS':
                                counter +=1
                                continue
                        if counter == 3 or counter == 4:
                            if mmavt.eye_usage_type != 'LR_EYES_ONLY' and mmavt.eye_usage_type != 'BOTH_SYSTEMS':
                                counter +=1
                                continue
                        HFEMProp(hfem,counter,box,hfem.name,MUtil.get_HFEM_icon(counter),canUse)
                        counter +=1
                        ...
                
                layout.active = True
                layout.enabled = True
                title = box.row()
                title = box.row()


                title.alignment = 'LEFT'
                indent(title)
                title.prop(mmavt,"foldout_mbody",text="",icon="DOWNARROW_HLT" if mmavt.foldout_mbody else "RIGHTARROW_THIN",emboss=False)
                title.label(text="BODY",icon="ARMATURE_DATA")
                op = title.operator("object.addmbodytommavt",text="",icon="ADD")
                op.arm_ref = mmavt.arm.name
                indent(title)
                if mmavt.foldout_mbody: ##TODO: Add thickness for triangle
                    for mbody in mmavt.mbody_list:
                        newLine2 : bpy.types.UILayout = box.row()
                        newLine2.alignment = 'LEFT'
                        newLine2.scale_y = 1
                        indent(newLine2)
                        indent(newLine2)
                        newLine2.prop(mbody,"foldout",text="",icon="DOWNARROW_HLT" if mbody.foldout else "RIGHTARROW_THIN",emboss=False)
                        op = newLine2.operator("object.addobjtombody",text="",icon="ADD")
                        op.arm_ref = mmavt.arm.name
                        op.propToAddTo = mbody.name
                        newLine2.prop(mbody,"is_visible",text="",icon="HIDE_OFF" if mbody.is_visible else "HIDE_ON") #TODO: Make functional
                        newLine2.prop(mbody,property="is_zero_indexed",text="",icon="LINENUMBERS_OFF" if mbody.is_zero_indexed else "LINENUMBERS_ON")
                        newLine2.scale_x = 0.9
                        newLine2.prop(mbody,property="name",text="",expand=True)
                        newLine2.emboss='NONE'
                        mmvmCtr = bpy.data.objects[mmavt.arm.name].pose.bones["MMAVT_Controller"]
                        poseName = "[\"" + mbody.name + "\"]"

                        newLine2.prop(mmvmCtr,poseName,text="",emboss=False,expand=True)
                        op = newLine2.operator("object.deletembodyfrommmavt",text='',icon="X",emboss=False)
                        op.strprop_to_remove = mbody.name
                        op.arm_ref = mmavt.arm.name
                        counter = 0
                        if mbody.foldout:
                            numberCache = []
                            for object in mbody.data_list:
                                newLine3 = box.row()
                                newLine3.alignment = 'LEFT'
                                indent(newLine3)
                                indent(newLine3)
                                indent(newLine3)
                                newLine3.scale_x = 0.3
                                newLine3.prop(object,property="number",text="",emboss=False)
                                newLine3.scale_x = 1
                                newLine3.prop(object,property="obj_ref",text="",icon='MESH_CUBE')

                                op = newLine3.operator("object.removeobjfrommbody",text="",icon="X",emboss=False)
                                op.arm_ref = mmavt.arm.name
                                op.propToRemoveFrom = mbody.name
                                op.objToRemove = counter
                                op.name = object.name
                                numberCache.append(object.number)

                                counter += 1

def CheckNumber(ogNum,list:list):
    for item in list:
        if ogNum == item:
            ogNum += 1
            ogNum = CheckNumber(ogNum,list)

    return ogNum

def HasItem(armToTest: bpy.types.Armature):

    for mmavt in bpy.context.scene.mmavt_list:
        if mmavt.arm.name == armToTest.name:
            return True
    return False
def indent(line:bpy.types.UILayout):
    line.label(text="", icon="BLANK1")

def HFEMProp(kind:MMAVT_hfem,index:int,layout:bpy.types.UILayout,title:str,icon:str,isActive:bool):
    newLineF = layout.row()
    newLineF.active = isActive
    newLineF.enabled = isActive
    newLineF.alignment = 'LEFT'

    mmvmCtr = bpy.data.objects[kind.parent_arm.name].pose.bones.get("MMAVT_Controller")
    if mmvmCtr is  None:
        return #return here so that we don't end up referencing an empty bone when we delete during MMAVT deletion
    hfemEnum = MUtil.get_HFEM_enum(index)
    indent(newLineF)
    indent(newLineF)
    
    newLineF.prop(kind,"foldout",text="",icon="DOWNARROW_HLT" if kind.foldout else "RIGHTARROW_THIN",emboss=False)
    op = newLineF.operator("object.add_hfem_data",text="",icon="ADD")
    op.arm_ref = kind.parent_arm.name
    op.hfem_index = index
    op.propToAddTo = str(hfemEnum)
    
    newLineF.prop(kind,"is_visible",text="",icon="HIDE_OFF" if kind.is_visible else "HIDE_ON") #TODO: Make functional
    newLineF.label(icon=icon)
    # newLineF = newLineF.row()
    newLineF.label(text=title)
    poseName = "[\"" + hfemEnum + "\"]"
    newLineF.prop(mmvmCtr,property=poseName,text="",emboss=True)

    if kind.foldout != True:
        return
    counter = 0
    for obj in kind.list:
        newLineObj = layout.row()
        newLineObj.alignment = 'LEFT'
        indent(newLineObj)
        indent(newLineObj)
        indent(newLineObj)
        newLineObj.scale_x = 0.05
        set_hfem_param(obj,newLineObj)
        newLineObj.scale_x = 1
        newLineObj.prop(obj,property="obj_ref",text="",icon='MESH_CUBE')
        op = newLineObj.operator("object.remove_hfem_data",text='',icon="X",emboss=False)
        op.arm_ref = kind.parent_arm.name
        op.propToRemoveFrom = kind.name
        op.objToRemove = counter
        op.name = obj.name
        counter += 1
        

def set_hfem_param(hfem_obj:MMAVT_hfem_data,newLineObj:bpy.types.UILayout):
    newLineObj.label(text="H")
    newLineObj.prop(hfem_obj,property="head",text="",emboss=False)
    if hfem_obj.prop_name == "FACE" or hfem_obj.prop_name == "EYE" or hfem_obj.prop_name == "MOUTH" or hfem_obj.prop_name == "EYELEFT" or hfem_obj.prop_name == "EYERIGHT":
        newLineObj.label(text="F")
        newLineObj.prop(hfem_obj,property="face",text="",emboss=False)
    if hfem_obj.prop_name == "EYE":
        newLineObj.label(text="E")
        newLineObj.prop(hfem_obj,property="eye",text="",emboss=False)
    if hfem_obj.prop_name == "EYELEFT":
        newLineObj.label(text="E")
        newLineObj.prop(hfem_obj,property="eyeLeft",text="",emboss=False)
    if hfem_obj.prop_name == "EYERIGHT":
        newLineObj.label(text="E")
        newLineObj.prop(hfem_obj,property="eyeRight",text="",emboss=False)
    if hfem_obj.prop_name == "MOUTH":
        newLineObj.label(text="M")
        newLineObj.prop(hfem_obj,property="mouth",text="",emboss=False)
    ...

