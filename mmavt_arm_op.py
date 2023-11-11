import bpy
import mathutils
from mathutils import Vector
import json
import os
from datetime import datetime

from bpy.types import Operator
from .milan_property import *
from .mmavt_functions import MMil

class Milan_OT_ReadyArmature(Operator):
    bl_idname = "object.rdyarm"
    bl_label = "Ready Armature"
    bl_description = "Creates data for armature to be used in MAAVT context"

    arm_to_ready : bpy.props.StringProperty(name = "Armature to Ready", default="")

    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        
        if bpy.context.mode == 'OBJECT':
            return True
        
        return False
    
    def execute(cls,context):
        scene = context.scene
        selected_obj = context.selected_objects
        phrase = "RESULT: " + cls.arm_to_ready
        print(phrase)
        targetName = ""
        for item in selected_obj:
            if item.name == cls.arm_to_ready:
                targetName = cls.arm_to_ready
        if targetName == "":
            return {"CANCELLED"}
        
        bpy.data.objects[targetName].select_set(True)
        bpy.ops.object.mode_set(mode='EDIT',toggle=False)

        arm = bpy.context.active_object
        
        ebs = arm.data.edit_bones
        origin = ""
        for bb in ebs:
            if  bb.name == "MMAVT_Controller": 
                print("A MMAVT_Controller already exists")
                new_mmavt = bpy.context.scene.mmavt_list.add()
                if arm.type == 'ARMATURE':
                    new_mmavt.arm = arm.data
                return {"FINISHED"}
            if bb.name == "origin" or bb.name == "Origin":
                origin = bb
            if bb.name == "root" or bb.name == "Root":
                origin = bb

        if origin == "":
            cls.report({"WARNING"}, "Error! No root bone found, please have a bone in your hierarchy named \"origin\" or \"root\"")
            return {"CANCELLED"}
        eb:bpy.types.Bone = ebs.new("MMAVT_Controller")
        eb.head = (0,0,0)
        eb.tail = (0,0,1)
        eb.use_deform = False
        eb.parent = origin
        
        new_mmavt = bpy.context.scene.mmavt_list.add()

        if arm.type == 'ARMATURE':
            new_mmavt.arm = arm.data
        
        print("MADE it this far")
        
        for i in range(6):
            hfemData = new_mmavt.hfem_list.add()    
            hfemData.kind = MMil.get_HFEM_enum(i)
            hfemData.parent_arm = new_mmavt.arm
        new_mmavt.eye_usage_type = 'EYE_ONLY'
        return {"FINISHED"}
    
class Milan_OT_RemoveArmatureRef(Operator):

    bl_idname = "object.rmvarm"
    bl_label = "Remove Armature"
    bl_description = "Remove armature from list of MMAVT armatures"

    arm_to_delete : bpy.props.StringProperty(name = "Armature to Delete", default="")

    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        
        # for item in objs:
        #     if item.name == cls.arm_to_ready:
        #         return True
        
        return True
    
    def execute(cls,context):
        scene = context.scene
        selected_obj = context.selected_objects
        deletePhrase = "Ready delete arm with name of: " + cls.arm_to_delete
        print(deletePhrase)
        arm_index:int = 0
        armature_name = ""
        counter:int = 0
        for mmavt in bpy.context.scene.mmavt_list:
            if mmavt.arm.name == cls.arm_to_delete:
                arm_index = counter
                for mbody in mmavt.mbody_list:
                    for data in mbody.data_list:
                        MMil.remove_driver(data.name)
                    
            counter += 1
        counter:int = 0
        for mmavt in bpy.context.scene.mmavt_list:
            if mmavt.arm.name == cls.arm_to_delete:
                arm_index = counter 
                for hfem in mmavt.hfem_list: 
                    for data in hfem.list:
                        MMil.remove_driver(data.name)      
            counter += 1

        for obj in bpy.data.objects:
            obj.select_set(False)
        bpy.data.objects[cls.arm_to_delete].select_set(True)
        # bpy.context.space_data.context = 'OBJECT'
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT',toggle=False)
        bones = bpy.data.armatures[cls.arm_to_delete].edit_bones
        for bone in bones:
            if bone.name == "MMAVT_Controller":
                bones.remove(bone)
        bpy.context.scene.mmavt_list.remove(arm_index)
        bpy.ops.object.mode_set(mode=current_mode,toggle=False)
        return {"FINISHED"}
    
class Milan_OT_export_mmavt_to_string(Operator):

    bl_idname = "object.export_mmavt_to_string"
    bl_label = "Export MMAVT data to string"
    bl_description = "Export data from MMAVT into a string that can be parsed by game engines supporting MMAVT"
    
    arm_ref : bpy.props.StringProperty(name = "Armature reference", default="")

    @classmethod
    def poll(cls, context):
        objs = context.view_layer.objects.selected
        ctx = context.mode
        # arm:bpy.types.Armature = bpy.data.objects.get(cls.arm_ref)
        # if arm is None:
        #     return False
        # mmavtCtr = arm.pose.bones.get("MMAVT_Controller")
        # if mmavtCtr is None:
        #     return False
        return True
    
    ##TODO: Make it so that people can't name something face in mobdy if they trying to generate an hfem instance
    def execute(cls,context):
        scene = context.scene
        selected_obj = context.selected_objects
        json_mmavt = Test()
        
        arm:bpy.types.Armature = bpy.data.objects[cls.arm_ref]
        mmavtCtr:bpy.types.Bone = bpy.data.objects[cls.arm_ref].pose.bones["MMAVT_Controller"]
        mmavtInst:MMAVT_instance = MMil.get_mmavt_from_arm_name(cls.arm_ref)
        hfem_list = mmavtInst.hfem_list
        mbody_list:bpy.types.CollectionProperty = mmavtInst.mbody_list

        
        json_hfem = Test()
        json_hfem.objects = []
        json_hfem.actions = []
        counter = 0
        for hfem in hfem_list:
            hfem:MMAVT_hfem
            object = Test()
            inty = len(hfem.list)
            object.name = hfem.name
            object.data = []
            json_hfem.objects.append(object)
            if inty <= 0:
                continue
            for data in hfem.list:
                data:MMAVT_hfem_data
                hfemdata = Test()
                hfemdata.name = data.obj_ref.name
                hfemdata.head = data.head
                hfemdata.face = data.face
                hfemdata.eye = data.eye
                hfemdata.eyeLeft = data.eyeLeft
                hfemdata.eyeRight = data.eyeRight
                hfemdata.mouth = data.mouth
                print(str(data))
                object.data.append(hfemdata)
        current_frame = bpy.context.scene.frame_current
        current_action = arm.animation_data.action
        for action in bpy.data.actions:
            action: bpy.types.Action
            arm.animation_data.action = action
            print("===" + action.name + "===")
            json_action = Test()
            json_hfem.actions.append(json_action)
            json_action.name = action.name
            print(action.name)
            keyframe_watcher = Test()
            keyframe_watcher.frames = []
            counter = 0
            path = mmavtCtr.path_from_id()

            # fc = action.mmavtCtrfcurves.find(path)
            # if fc is None:
            #     continue
            json_action.keyframes = []
            fcurves = action.fcurves
            bone_fcurves = [fcu for fcu in fcurves if fcu.data_path.startswith(path)]
            for fcurves in bone_fcurves:
                fcurves:bpy.types.FCurve
                for keyframe in fcurves.keyframe_points:
                    print("testy: " + action.name + " " + str(keyframe.co_ui.x))
                    frametime = keyframe.co_ui.x
                    intval = int(keyframe.co_ui.y)
                    json_keyframe = Test()
                    frametime_secs = key_to_sec(frametime)
                    json_keyframe.time = frametime_secs
                    # continue
                    
                    bpy.context.scene.frame_set(int(keyframe.co_ui.x))
                    print(bpy.context.scene.frame_current)
                    json_keyframe.head = mmavtCtr["HEAD"]
                    json_keyframe.face = mmavtCtr["FACE"]
                    json_keyframe.eye = mmavtCtr["EYE"]
                    json_keyframe.eyeLeft = mmavtCtr["EYELEFT"]
                    json_keyframe.eyeRight = mmavtCtr["EYERIGHT"]
                    json_keyframe.mouth = mmavtCtr["MOUTH"]
                    if frametime in keyframe_watcher.frames:
                        print("Duplicate frametime, skip!")
                        continue
                    else:
                        print("New frametime, append!")
                        keyframe_watcher.frames.append(frametime)
                        print(str(keyframe_watcher.frames))
                    json_action.keyframes.append(json_keyframe)

        bpy.context.scene.frame_set(current_frame)
        arm.animation_data.action = current_action
        json_mbody = Test()
        json_mbody.objects = []
        json_mbody.actions = []
        counter = 0
        for mbody in mbody_list:
            mbody:MMAVT_mbody
            object = Test()
            json_mbody.objects.append(object)
            object.name = mbody.name
            object.data = []
            for data in mbody.data_list:
                data:MMAVT_mbody_data
                object.data.append(data.obj_ref.name)
            path = mmavtCtr.path_from_id()
            full_datapath = path + encapsulate(mbody.name)
            for action in bpy.data.actions:
                json_action = Test()
                actiontest = getexistingaction(json_mbody.actions,action.name)
                if actiontest != '':
                    json_action = actiontest
                else:
                    json_action.name = action.name
                    json_action.keyframes = []
                    json_mbody.actions.append(json_action)
                fc = action.fcurves.find(full_datapath)
                print("===" + mbody.name + "===")
                for keyframe in fc.keyframe_points:
                    keyframe:bpy.types.Keyframe
                    frametime = keyframe.co_ui.x
                    intval = int(keyframe.co_ui.y)
                    frametime_secs = key_to_sec(frametime)
                    collection = getcollectionitem(mbody.data_list,intval)
                    # print(str(frametime_secs) + ": " + str(intval) + " (" + getcollectionitem(mbody.data_list,intval) + ")")
                    json_keyframe = Test()
                    json_keyframe.time = frametime_secs
                    json_keyframe.mmavtName = mbody.name
                    json_keyframe.mmavtIndex = counter
                    if(collection != 'empty'):
                        json_keyframe.objectName = collection.name
                        json_keyframe.objectIndex = collection.index
                        json_action.keyframes.append(json_keyframe)
            counter += 1

        armName_info = "Name: \'" + arm.name + '\'' 
        datetime_now = datetime.now()
        current_time = datetime_now.strftime("%Y-%b-%d %H:%M.%S")
        json_mmavt.metaData = armName_info + " " + current_time
        json_mmavt.hfem = json_hfem
        json_mmavt.mbody = json_mbody
        jason = (json.dumps(json_mmavt,default=vars,indent=2))

        filepath=mmavtInst.folder_export_path + arm.name + ".json"
        with open(filepath,'w') as f:
            f.write(jason)
        currentdirectory = os.getcwd()
        print(currentdirectory)
        ##TODO: Add way to disable this
        with open(currentdirectory +"/" +"result.json",'w') as f:
            f.write(jason)


        bpy.context.window_manager.clipboard = jason
                    
        print("framerate is: " + str(bpy.context.scene.render.fps))
        return {"FINISHED"}

def encapsulate(name:str):
    return "[\"" + name + "\"]"
def key_to_sec(frametime:float):
    fps = bpy.context.scene.render.fps
    return frametime / fps

class Test:
    ...
def getcollectionitem(list,wantednum:int)->Test: #this function is so fucking disgusting, so awfully unnecessary but I cannot find any other way to grab an item by index
    collection = Test()
    counter = 0 
    for item in list:
        print(item.name)
        if wantednum == item.number:
            obj:bpy.types.Object = item.obj_ref
            collection.name = obj.name
            print("my name is: " + collection.name)
            print("FOUND ONE!")
            collection.index = counter
            return collection
        print(str(counter))
        counter += 1

    print("COULDNT FIND SHIT!")
    return 'empty'

def get_hfem_item(list,wantednum:int)->Test:
    collection = Test()
    counter = 0 
    for item in list:
        print(item.name)
        if wantednum == item.number:
            obj:bpy.types.Object = item.obj_ref
            collection.name = item.obj_ref

            collection.head = item.head
            collection.face = item.face
            collection.eye = item.eye
            collection.eyeLeft = item.eyeLeft
            collection.eyeRight = item.eyeRight
            collection.mouth = item.mouth
            return collection
        print(str(counter))
        counter += 1

    print("COULDNT FIND SHIT!")
    return 'empty'

def getexistingaction(list,actionname:str):
    for item in list:
        if item.name == actionname:
            return item
    return ''
