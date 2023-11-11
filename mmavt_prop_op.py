import bpy
import mathutils
from mathutils import Vector

from bpy.types import Operator
from bpy.types import Armature
from .mmavt_functions import MMil
from .milan_property import MMAVT_instance, MMAVT_mbody_data, MMAVT_hfem_data,MMAVT_hfem,MMAVT_mbody


class Milan_OT_AddMBodyToMMAVT(Operator):

    bl_idname = "object.addmbodytommavt"
    bl_label = "Add Property"
    bl_description = "Add mbody to armature"
    
    arm_ref : bpy.props.StringProperty(name = "Armature to Add Property To", default="")
    default_name = "variable"

    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        
        if bpy.context.mode == 'OBJECT' or bpy.context.mode == 'POSE':
            return True
        
        return False
    
    def execute(cls,context):
        # test:str = cls.strprop_to_add + "/" + cls.arm_ref
        # print(test)
        mmavt:MMAVT_instance = MMil.get_mmavt_from_arm_name(cls.arm_ref)
        mbody_list:MMAVT_mbody = mmavt.mbody_list
        uniqueName = generate_unique_name(cls.default_name,mbody_list)
        new_mbody = mbody_list.add()
        new_mbody.name = uniqueName
        new_mbody.old = ""
        new_mbody.arm = mmavt.arm
        MMil.adjust_mmavt_property(new_mbody)
        return {"FINISHED"}
    
class Milan_OT_DeleteMBodyFromMMAVT(Operator):

    bl_idname = "object.deletembodyfrommmavt"
    bl_label = "Delete mbody"
    bl_description = "Delete mody from mmavt"

    strprop_to_remove : bpy.props.StringProperty(name = "Property to Remove", default="")
    arm_ref : bpy.props.StringProperty(name = "Armature to Remove Property From", default="")

    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        
        return True
    
    def execute(cls,context):
        mmavt = MMil.get_mmavt_from_arm_name(cls.arm_ref)
        mmavt.arm.name
        propToRemove = cls.strprop_to_remove
        counter = 0
        for prop in mmavt.mbody_list:
            if propToRemove == prop.name:
                for obj in prop.data_list:
                    MMil.remove_driver(obj.name)
                mmavt.mbody_list.remove(counter)
                del bpy.data.objects[mmavt.arm.name].pose.bones["MMAVT_Controller"][propToRemove]
            counter +=1
        return {"FINISHED"}
    
class Milan_OT_AddObjToMbody(Operator):

    bl_idname = "object.addobjtombody"
    bl_label = "Add obj to mbody"
    bl_description = "Add object to mbody group"

    arm_ref : bpy.props.StringProperty(name = "Armature reference", default="")
    propToAddTo : bpy.props.StringProperty(name = "Property to add to", default="")

    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        
        return True
    
    def execute(cls,context):
        test:str = cls.propToAddTo + "/" + cls.arm_ref
        print(test)
        mmavt = MMil.get_mmavt_from_arm_name(cls.arm_ref)
        props:MMAVT_mbody = mmavt.mbody_list
        prop = MMil.get_mbody_from_list(cls.propToAddTo,props)
        prop.foldout = True
        data:MMAVT_mbody_data = prop.data_list.add()
        data.arm:Armature = mmavt.arm
        data.prop_name = cls.propToAddTo
        return {"FINISHED"}
    
class Milan_OT_RemoveObjFromMbody(Operator):

    bl_idname = "object.removeobjfrommbody"
    bl_label = "Remove object from mbody"
    bl_description = "Remove object from mbody group"

    arm_ref : bpy.props.StringProperty(name = "Armature reference", default="")
    propToRemoveFrom : bpy.props.StringProperty(name = "Property to remove from", default="")
    objToRemove : bpy.props.IntProperty(name="object to remove")
    name : bpy.props.StringProperty(name="name of object to be removed")

    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        
        # for item in objs:
        #     if item.name == cls.arm_to_ready:
        #         return True
        
        return True
    
    def execute(cls,context):
        mmavt = MMil.get_mmavt_from_arm_name(cls.arm_ref)   
        props = mmavt.mbody_list
        prop = MMil.get_mbody_from_list(cls.propToRemoveFrom,props)
        prop.data_list.remove(cls.objToRemove)
        MMil.remove_driver(cls.name)
        return {"FINISHED"}

    
def generate_unique_name(nameToUse:str,properties:MMAVT_mbody):
    goofyName = nameToUse + str(1)
    for prop in properties:
        if prop.name == goofyName:
            newName = generate_unique_name(goofyName,properties)
            return newName
    return goofyName
