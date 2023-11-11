import bpy
from .MMAVT_property import MMAVT_instance, MMAVT_mbody_data, MMAVT_hfem_data, MMAVT_hfem, MMAVT_mbody

class MUtil():

    def get_mmavt_from_arm_name(nameToFind:str) -> MMAVT_instance:
        for property in bpy.context.scene.mmavt_list:
            if property.arm.name == nameToFind:
                return property
        return None

    def HasNoRepeat(nameToUse:str,properties):
        for prop in properties:
            if prop.name == nameToUse:
                return False
        return True
    
    def get_mbody_from_list(nameToFind:str,properties) -> MMAVT_mbody:
        for prop in properties:
            if prop.name == nameToFind:
                return prop
        return None
    def get_hfem_from_list(nameToFind:str,properties) -> MMAVT_hfem:
        for prop in properties:
            if prop.name == nameToFind:
                return prop
        return None
    
    def adjust_mmavt_property(prop):
        mmvmCtr = bpy.data.objects[prop.arm.name].pose.bones["MMAVT_Controller"]
        temp = 0
        if prop.old_name in mmvmCtr:
            temp = mmvmCtr[prop.old_name]
            del mmvmCtr[prop.old_name]
        
        mmvmCtr[prop.name] = temp
        mmvmCtr.id_properties_ensure()
        property_manager = mmvmCtr.id_properties_ui(prop.name)
        if type(prop) == MMAVT_mbody:
            property_manager.update(min=0,max=99,soft_min=0,soft_max=99,description="Change model through this custom property")
        else:
            property_manager.update(min=-1,max=99,soft_min=0,soft_max=99,description="Change model through this custom property")

    def RemoveCustomProperty(arm:MMAVT_instance,prop_name):
        mmvmCtr = bpy.data.objects[arm.name].pose.bones["MMAVT_Controller"]
        print(prop_name)

    def GetPropertyFromArmature(arm:bpy.types.Armature,prop_name):
        return bpy.data.objects[arm.name].pose.bones["MMAVT_Controller"][prop_name]
    def get_HFEM_enum(number:int):
        match number:
            case 0:
                return 'HEAD'
            case 1:
                return 'FACE'
            case 2:
                return 'EYE'
            case 3:
                return 'EYELEFT'
            case 4:
                return 'EYERIGHT'
            case 5:
                return 'MOUTH'
            case _:
                return 'ERROR'
    def get_HFEM_icon(number:int):
        match number:
            case 0:
                return 'EVENT_H'
            case 1:
                return 'EVENT_F'
            case 2:
                return 'EVENT_E'
            case 3:
                return 'EVENT_L'
            case 4:
                return 'EVENT_R'
            case 5:
                return 'EVENT_M'
            case _:
                return 'ERROR'
    
    def remove_driver(name:str):
        objects = bpy.context.scene.objects.keys()
        objDrivers = ''
        if name in objects:
            objDrivers = bpy.data.objects[name].animation_data.drivers
        else:
            return
        obj = bpy.data.objects[name]
        if objDrivers.find("hide_viewport"):
            obj.driver_remove("hide_viewport")