# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# useful:
# https://github.com/blender/blender/blob/master/release/scripts/startup/bl_ui/space_view3d.py
# https://blender.stackexchange.com/questions/152525/appending-a-sub-menu-under-an-existing-sub-menu-in-blender-2-8
#
# https://blenderartists.org/t/emulate-hotkey-g-grab-move-by-python-script/1146527/3
#    bpy.ops.transform.translate('INVOKE_DEFAULT')
# -run from file
#   https://docs.blender.org/api/current/info_tips_and_tricks.html
#filename = "/full/path/to/myscript.py"
#exec(compile(open(filename).read(), filename, 'exec'))

bl_info = {
    "name": "Py Jef",
    "description": "Additional Python 'Run Script' buttons for Blender, in many places.",
    "author": "Dave",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3DView - Tools",
    "category": "Python",
}

import bpy
from bpy.props import (StringProperty, BoolProperty)
from .pj_run import (PYJEF_OT_RunCodeLine, PYJEF_OT_RunTextblock, PYJEF_OT_RunTextObject)

if bpy.app.version < (2,80,0):
    Region = "TOOLS"
else:
    Region = "UI"

class PYJEF_PT_RunPanel(bpy.types.Panel):
    bl_label = "Run"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "PyJef"

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        box = layout.box()
        box.label(text="Input")
        box.operator(PYJEF_OT_RunCodeLine.bl_idname)
        box.prop(context.scene, "PYJEF_CodeLineToRun")
        box.operator(PYJEF_OT_RunTextblock.bl_idname)
        box.prop_search(scn, "PYJEF_TextblockToRun", bpy.data, "texts")
        box.operator(PYJEF_OT_RunTextObject.bl_idname)
        #box.prop_search(scn, "PYJEF_TextObjectToRun", bpy.data, "objects")
        box.prop_search(scn, "PYJEF_TextObjectToRun", context.scene, "objects")
        box = layout.box()
        box.label(text="Output")
        box.prop_search(scn, "PYJEF_OutputTextBlock", bpy.data, "texts")
        box.prop(context.scene, "PYJEF_AlwaysNewTextblock")
        box.prop(context.scene, "PYJEF_OutputShowCode")
        box.prop(context.scene, "PYJEF_OutputShowExceptions")
        box.prop(context.scene, "PYJEF_OutputShowPrintStmts")
        box = layout.box()
        box.label(text="Comment Options")
        box.prop(context.scene, "PYJEF_CommentRunStartTime")
        box.prop(context.scene, "PYJEF_CommentRunEndTime")
        box.prop(context.scene, "PYJEF_CommentTimeMicrosecond")

        box.prop(context.scene, "PYJEF_CommentCodeText")
        # comment code on exception is only active if code isn't already automatically being commented
        row = box.row()
        row.active = not context.scene.PYJEF_CommentCodeText
        row.prop(context.scene, "PYJEF_CommentCodeTextOnException")
        box.prop(context.scene, "PYJEF_CommentExceptionMessage")
        box.prop(context.scene, "PYJEF_CommentPrintStmts")

classes = [
    PYJEF_PT_RunPanel,
    PYJEF_OT_RunCodeLine,
    PYJEF_OT_RunTextblock,
    PYJEF_OT_RunTextObject,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.PYJEF_OutputTextBlock = StringProperty(name="Output TextBlock",
        description="CodeText that is run will be copied to this TextBlock, with comments, etc.", default="")
    bpy.types.Scene.PYJEF_AlwaysNewTextblock = BoolProperty(name="Always New Textblock",
        description="If True then always create a new Textblock (in the Text Editor) when code text is run. " +
        "If False then code text will be added to Output Textblock", default=False)
    bpy.types.Scene.PYJEF_CodeLineToRun = StringProperty(name="Line",
        description="Python code to run in current context/space", default="print(\"jef\")")
    bpy.types.Scene.PYJEF_TextblockToRun = StringProperty(name="Textblock",
        description="Textblock to run as script, with specified output", default="")

    #bpy.types.Scene.PYJEF_TextObjectToRun = StringProperty(name="Text Object",
    #    description="Text object, with lines of code to be run", default="")
    bpy.types.Scene.PYJEF_TextObjectToRun = bpy.props.PointerProperty(type=bpy.types.Object, poll=filter_on_custom_prop,
        name="Text Object", description="Text object, with lines of code to be run")

    bpy.types.Scene.PYJEF_OutputShowCode = BoolProperty(name="Output Code",
        description="Include code that is run in the Output", default=True)
    bpy.types.Scene.PYJEF_OutputShowExceptions = BoolProperty(name="Output Exceptions",
        description="Include exception messages in the Output (only if an Exception is raised when code is run)",
        default=True)
    bpy.types.Scene.PYJEF_OutputShowPrintStmts = BoolProperty(name="Output print() Statements",
        description="Include print() statements in the Output. This will re-direct stdout to the output string", default=True)

    # comment options
    bpy.types.Scene.PYJEF_CommentCodeText = BoolProperty(name="Line of Code Text",
        description="Write hashtag (Python comment symbol) before every line of Code Text", default=False)
    bpy.types.Scene.PYJEF_CommentCodeTextOnException = BoolProperty(name="Code Text on Exception",
        description="Code Text only if Exception occurs during run of Text Code", default=True)
    bpy.types.Scene.PYJEF_CommentExceptionMessage = BoolProperty(name="Exception Message",
        description="If code text generates exception then every line of output exception message will have " +
        "comment hashtags prepended", default=True)
    bpy.types.Scene.PYJEF_CommentPrintStmts = BoolProperty(name="print() Statements",
        description="If code text generates print() statements then every line of print() statement message will " +
        "have comment hashtags prepended", default=True)
    bpy.types.Scene.PYJEF_CommentRunStartTime = BoolProperty(name="Run Start Time",
        description="If True then include time when run was started as comment, prepended to code text", default=False)
    bpy.types.Scene.PYJEF_CommentRunEndTime = BoolProperty(name="Run End Time",
        description="If True then include time when run ended as comment, appended to code text and exception message",
        default=False)
    bpy.types.Scene.PYJEF_CommentTimeMicrosecond = BoolProperty(name="Run Time(s) with Microseconds",
        description="If True then show time including microseconds (with trailing zeroes removed) in start/end time(s)", default=True)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.PYJEF_CommentTimeMicrosecond
    del bpy.types.Scene.PYJEF_CommentRunEndTime
    del bpy.types.Scene.PYJEF_CommentRunStartTime
    del bpy.types.Scene.PYJEF_CommentPrintStmts
    del bpy.types.Scene.PYJEF_CommentCodeTextOnException
    del bpy.types.Scene.PYJEF_CommentCodeText
    del bpy.types.Scene.PYJEF_CommentExceptionMessage
    del bpy.types.Scene.PYJEF_TextObjectToRun
    del bpy.types.Scene.PYJEF_TextblockToRun
    del bpy.types.Scene.PYJEF_CodeLineToRun
    del bpy.types.Scene.PYJEF_AlwaysNewTextblock
    del bpy.types.Scene.PYJEF_OutputTextBlock

if __name__ == "__main__":
    register()


#################################
## define the filter method
def filter_on_custom_prop(self, obj):
    return obj.type == 'FONT'

# define the property by using the bpy.props.PointerProperty and its poll function
#bpy.types.Object.my_object = bpy.props.PointerProperty(
#    type=bpy.types.Object,
#    poll=filter_on_custom_prop
#)
#
## add to your draw code a `prop_search`
#layout.prop_search(obj, "my_object", context.scene, "objects")
## or just simple
#layout.prop(obj, "my_object")