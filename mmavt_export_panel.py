import bpy

from .milan_property import MMAVT_instance,MMAVT_mbody_data,MMAVT_hfem_data,MMAVT_hfem,MMAVT_mbody
from .mmavt_functions import MMil
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


class MMAVT_PT_export_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "MMAVT Exporter"
    bl_category = "Milan Util"


    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row()
        row.alignment ='LEFT'
        mmavt_list = bpy.context.scene.mmavt_list
        row.label(text="JSON Export")
        for mmavt in mmavt_list:
            mmavt:MMAVT_instance
            row = layout.box().row()
            row.alignment ='LEFT'
            row.label(text="", icon="DOT")
            row.label(text=mmavt.arm.name)
            op = row.operator("object.export_mmavt_to_string",text="Export to Json",icon="WORDWRAP_ON")
            op.arm_ref = mmavt.arm.name
            row.prop(mmavt,property="folder_export_path",text="path")

def indent(line:bpy.types.UILayout):
    line.label(text="", icon="BLANK1")