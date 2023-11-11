import bpy
import os
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


def generate_mbody_expr(numberToInsert):
    strVar = str(numberToInsert)
    tempVal = '0 if var == ' + strVar + ' else 1'
    return tempVal

def generate_hfem_expr(hfem_data):
    from .mmavt_functions import MMil
    hfem_data:MMAVT_hfem_data = hfem_data
    tempval = ''
    if hfem_data.prop_name == "HEAD":
        tempVal = '0 if head == ' + str(hfem_data.head) + ' else 1'
    if hfem_data.prop_name == "FACE":
        tempVal = '0 if head == ' + str(hfem_data.head) + ' and face == ' + str(hfem_data.face) + ' else 1'
    if hfem_data.prop_name == "EYE":
        tempVal = '0 if head == ' + str(hfem_data.head) + ' and face == ' + str(hfem_data.face) + ' and eye == ' + str(hfem_data.eye) + ' else 1'
    if hfem_data.prop_name == "EYELEFT":
        tempVal = '0 if head == ' + str(hfem_data.head) + ' and face == ' + str(hfem_data.face) + ' and eyeleft == ' + str(hfem_data.eyeLeft) + ' and eye == -1 ' + ' else 1'
    if hfem_data.prop_name == "EYERIGHT":
        tempVal = '0 if head == ' + str(hfem_data.head) + ' and face == ' + str(hfem_data.face) + ' and eyeright == ' + str(hfem_data.eyeRight) + ' and eye == -1 ' + ' else 1'
    if hfem_data.prop_name == "MOUTH":
        tempVal = '0 if head == ' + str(hfem_data.head) + ' and face == ' + str(hfem_data.face) + ' and mouth == ' + str(hfem_data.mouth) + ' else 1'
    return tempVal

def make_driver_path(armatureName:str,propertyName:str):
    tempVal = 'pose.bones[\"' + armatureName + '\"]'
    tempVal2 = "[\"" + propertyName + "\"]"
    return tempVal + tempVal2
    
def set_mbody_driver(data):
    from .mmavt_functions import MMil
    data:MMAVT_mbody_data = data
    obj = data.obj_ref
    data.name = data.obj_ref.name
    nameIs = "propety name to look for is: " + data.prop_name
    print(nameIs)
    prop = MMil.GetPropertyFromArmature(data.arm,data.prop_name)
    bpy.data.objects[data.name].driver_remove("hide_viewport")
    if data.old_name != "":
        bpy.data.objects[data.old_name].driver_remove("hide_viewport")
    obj.driver_remove("hide_viewport")
    dri = obj.driver_add("hide_viewport")
    dri.driver.expression = generate_mbody_expr(data.number)
    var = dri.driver.variables.new()
    var.name = "var"
    var.type = "SINGLE_PROP"
    var.targets[0].id_type = "OBJECT"
    var.targets[0].id = bpy.data.objects[data.arm.name]
    driverPath = make_driver_path("MMAVT_Controller",data.prop_name)
    var.targets[0].data_path = driverPath
    dri.driver.expression += " "
    dri.driver.expression = dri.driver.expression[:-1]
    dri.driver.expression = dri.driver.expression

def set_hfem_driver(data):
    from .mmavt_functions import MMil
    data:MMAVT_hfem_data = data
    obj:bpy.types.Object = data.obj_ref
    data.name = data.obj_ref.name
    nameIs = "propety name to look for is: " + data.prop_name
    print(nameIs)
    prop = MMil.GetPropertyFromArmature(data.arm,data.prop_name)
    bpy.data.objects[data.name].driver_remove("hide_viewport")
    if data.old_name != "":
        bpy.data.objects[data.old_name].driver_remove("hide_viewport")
    obj.driver_remove("hide_viewport")
    dri = obj.driver_add("hide_viewport")
    dri.driver.expression = generate_hfem_expr(data)
    if data.prop_name == "HEAD" or data.prop_name == "FACE" or data.prop_name == "EYE" or data.prop_name == "EYELEFT" or data.prop_name == "EYERIGHT" or data.prop_name == "MOUTH":
        make_hfem_driver_var(data,dri.driver,"head",'HEAD')
    if data.prop_name == "FACE" or data.prop_name == "EYE" or data.prop_name == "EYELEFT" or data.prop_name == "EYERIGHT" or data.prop_name == "MOUTH":
        make_hfem_driver_var(data,dri.driver,"face",'FACE')
    if data.prop_name == "EYE" or data.prop_name == "EYELEFT" or data.prop_name == "EYERIGHT":
        make_hfem_driver_var(data,dri.driver,"eye",'EYE')
    if data.prop_name == "EYELEFT":
        make_hfem_driver_var(data,dri.driver,"eyeleft",'EYELEFT')
    if data.prop_name == "EYERIGHT":
        make_hfem_driver_var(data,dri.driver,"eyeright",'EYERIGHT')
    if data.prop_name == "MOUTH":
        make_hfem_driver_var(data,dri.driver,"mouth",'MOUTH')
    dri.driver.expression += " "
    dri.driver.expression = dri.driver.expression[:-1]
    dri.driver.expression = dri.driver.expression

def make_hfem_driver_var(data, driver:bpy.types.Driver,var_name:str,path_name:str):
    from .mmavt_functions import MMil
    data:MMAVT_hfem_data = data
    var:bpy.types.DriverVariable = driver.variables.new()
    var.name = var_name
    var.type = "SINGLE_PROP"
    var.targets[0].id_type = "OBJECT"
    var.targets[0].id = bpy.data.objects[data.arm.name]
    driverPath = make_driver_path("MMAVT_Controller",path_name)
    var.targets[0].data_path = driverPath
    
def update_data_names(self,context):
        for data in self.data_list:
            data.prop_name = self.name
            print(data.prop_name)

def update_mbody_driver_path(self,context):
    update_data_names(self,context)
    for data in self.data_list:
        set_mbody_driver(data)

def update_hfem_driver_path(self,context):
    update_data_names(self,context)
    for data in self.data_list:
        set_hfem_driver(data)

def fix_mbody_property_name(self,context):
    from .mmavt_functions import MMil
    
    MMil.adjust_mmavt_property(self)
    update_mbody_driver_path(self,context)

def fix_hfem_property_name(self,context):
    from .mmavt_functions import MMil
    nameIs = "name is: " + self.old_name
    print(nameIs)
    MMil.adjust_mmavt_property(self)
    update_hfem_driver_path(self,context)

def MMAVT_FixDupNum(self,context):
    prop = bpy.data.objects[self.obj_ref.name].animation_data.drivers
    print(prop.find("hide_viewport"))
    if prop.find("hide_viewport"):
        prop.find("hide_viewport").driver.expression = generate_mbody_expr(self.number)
    update_mbody_driver_path(self,context)

def update_mbody_obj_data(self,context):
    from .mmavt_functions import MMil
    set_mbody_driver(self)

def update_hfem_obj_data(self,context):
    from .mmavt_functions import MMil
    set_hfem_driver(self)

def AddCustomProperty(self,context):
    from .mmavt_functions import MMil
    self:MMAVT_mbody_data = self
    scream = "SELF: " + str(self)
    print(scream)
    MMil.adjust_mmavt_property(self)
    for data in self.data_list:
        MMAVT_FixDupNum(self.data,context)
        print(self.name)
        data.prop_name = self.name
        set_mbody_driver(data)

class MMAVT_mbody_data(PropertyGroup):
    
    def get_name(self): #thank you batFINGER
        return self.get("name", "")

    def set_name(self, value):
        self["old_name"] = self.get("name","")
        self["name"] = value
        combo = str(self.old_name) + "/" + str(self.name)
        print(combo)
        print("HI")

    number : IntProperty(min=0,max=99,update=MMAVT_FixDupNum)
    obj_ref : PointerProperty(type=bpy.types.Object,update=update_mbody_obj_data)
    name : StringProperty(get=get_name,set=set_name)
    old_name : StringProperty()
    prop_name : StringProperty()
    arm : PointerProperty(type=bpy.types.Armature)
    # dri : PointerProperty()

class MMAVT_hfem_data(MMAVT_mbody_data):
    field : StringProperty()
    kind = EnumProperty(
        items = [('HEAD','Head','','EVENT_H',0), 
            ('FACE','Face','','EVENT_F',1),
            ('EYE','Eyes','','EVENT_E',2),
            ('EYELEFT','Left Eye','','EVENT_L',3),
            ('EYERIGHT','Right Eye','','EVENT_R',4),
            ('MOUTH','Mouth','','EVENT_M',5)])
    head : IntProperty(min=-1,max=99)
    face : IntProperty(min=-1,max=99)
    eye : IntProperty(min=-1,max=99)
    eyeLeft : IntProperty(min=-1,max=99)
    eyeRight : IntProperty(min=-1,max=99)
    mouth : IntProperty(min=-1,max=99)
    obj_ref : PointerProperty(type=bpy.types.Object,update=update_hfem_obj_data)


class MMAVT_hfem(PropertyGroup):
    name : StringProperty()
    kind = EnumProperty(
        items = [('HEAD','Head','','EVENT_H',0), 
            ('FACE','Face','','EVENT_F',1),
            ('EYE','Eyes','','EVENT_E',2),
            ('EYELEFT','Left Eye','','EVENT_L',3),
            ('EYERIGHT','Right Eye','','EVENT_R',4),
            ('MOUTH','Mouth','','EVENT_M',5)])
    list : CollectionProperty(type=MMAVT_hfem_data)
    index : IntProperty
    parent_arm : PointerProperty(type=bpy.types.Armature) #TODO: Make this arm for simplicity
    foldout : BoolProperty()
    is_visible : BoolProperty(default=True)

class MMAVT_mbody(PropertyGroup):
    def get_name(self): #thank you batFINGER
        return self.get("name", "Temp")

    def set_name(self, value):
        self["old_name"] = self.get("name","Temp")
        self["name"] = value
        combo = str(self.old_name) + "/" + str(self.name)
        print(combo)

    name : StringProperty(update=fix_mbody_property_name,get=get_name,set=set_name)
    old_name : StringProperty()
    arm : PointerProperty(type=bpy.types.Armature)
    data_list : CollectionProperty(type=MMAVT_mbody_data) #TODO: Make this and MMAVT_HFEM have the same list name for better compatibility
    list_index : IntProperty(description="index for data_list")
    foldout : BoolProperty()
    is_zero_indexed : BoolProperty(default=True,description="Use zero-indexing for property names")
    is_visible : BoolProperty(default=True)

class MMAVT_instance(PropertyGroup):
    can_use_hfem : BoolProperty(name="Can use HFEM",description="Has generated properties for HFEM use",default=False)
    arm : PointerProperty(type=bpy.types.Armature)
    mbody_list : CollectionProperty(type=MMAVT_mbody)
    hfem_list : CollectionProperty(type=MMAVT_hfem)
    name_field : StringProperty()
    foldout : BoolProperty(name="",description="Fold out armature properties",default=False)
    foldout_hfem : BoolProperty(name="",description="Fold out HFEM properties",default=False)
    foldout_mbody : BoolProperty(name="",description="Fold out body properties",default=False)
    eye_usage_type : EnumProperty(name="",items = [('EYE_ONLY','Single Eye','','PIVOT_ACTIVE',1),
        ('LR_EYES_ONLY','L&R Eyes','','PIVOT_INDIVIDUAL',0),                                                   
        ('BOTH_SYSTEMS','Both Systems','','OUTLINER_OB_POINTCLOUD',2)])
    folder_export_path : StringProperty(subtype="FILE_PATH" )