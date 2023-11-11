# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "MMAV-T",
    "author" : "Milan Cline",
    "description" : "\"Milan's Mesh Animation Visiblity Tool\", allows the dynamic swapping of meshes",
    "blender" : (3, 61, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from .MMAVT_property import MMAVT_mbody_data,MMAVT_hfem_data,MMAVT_mbody, MMAVT_hfem, MMAVT_instance
from .mmavt_prop_op import Milan_OT_AddMBodyToMMAVT,Milan_OT_DeleteMBodyFromMMAVT,Milan_OT_AddObjToMbody,Milan_OT_RemoveObjFromMbody
from .mmavt_arm_op import Milan_OT_ReadyArmature,Milan_OT_RemoveArmatureRef,Milan_OT_export_mmavt_to_string
from .mmavt_hfem_op import Milan_OT_Add_HFEM_Data,Milan_OT_Instantiate_HFEM_Properties,Milan_OT_remove_hfem_data
from .mmavt_panel import MMAVT_PT_Panel
from .mmavt_export_panel import MMAVT_PT_export_panel
from .mmavt_locale import langs
# from . MMAVT_property import my_bool

properties = (MMAVT_mbody_data,MMAVT_hfem_data,MMAVT_hfem,MMAVT_mbody,MMAVT_instance)
operators = (Milan_OT_AddObjToMbody,Milan_OT_RemoveObjFromMbody,Milan_OT_ReadyArmature,
             Milan_OT_AddMBodyToMMAVT,Milan_OT_Add_HFEM_Data,Milan_OT_remove_hfem_data,Milan_OT_RemoveArmatureRef,Milan_OT_DeleteMBodyFromMMAVT,
             Milan_OT_Instantiate_HFEM_Properties,Milan_OT_export_mmavt_to_string)
panels = (MMAVT_PT_Panel,MMAVT_PT_export_panel)


def register():
    bpy.app.translations.register(__name__, langs)
    for p in properties:
        bpy.utils.register_class(p)
    for o in operators:
        bpy.utils.register_class(o)
    for pa in panels:
        bpy.utils.register_class(pa)
    bpy.types.Scene.mmavt_list = bpy.props.CollectionProperty(type=MMAVT_instance)

def unregister():
    for p in properties:
        bpy.utils.unregister_class(p)
    for o in operators:
        bpy.utils.unregister_class(o)
    for pa in panels:
        bpy.utils.unregister_class(pa)
    bpy.app.translations.unregister(__name__)


