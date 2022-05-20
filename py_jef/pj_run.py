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

import bpy
import datetime
from io import StringIO
import sys

DEFAULT_TEXTBLOCK_NAME = "py_text"

def get_output_textblock(output_textblock_name, always_new_textblock):
    if output_textblock_name == "":
        output_textblock_name = DEFAULT_TEXTBLOCK_NAME
    output_textblock = None
    if always_new_textblock:
        output_textblock = bpy.data.texts.new(output_textblock_name)
    else:
        # try to get TextBlock or make new one if needed
        output_textblock = bpy.data.texts.get(output_textblock_name)
        if output_textblock == None:
            output_textblock = bpy.data.texts.new(output_textblock_name)
    return output_textblock

def run_codetext_return_output(self, context, codetext, output_options, comment_options):
    exec_locals = { "self": self, "context": context }
    exception_str = None
    finish_or_cancel = {'FINISHED'}

    # redirect stdout so print() statements can be captured
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    try:
        exec(codetext, {}, exec_locals)
    #Exception, e:    # Blender 2.79, because Python 2.x
    except Exception as e:  # Blender 2.8+, because Python 3.x
        exception_str = str(e)
        finish_or_cancel = {'CANCELLED'}
        self.report({"ERROR"}, "Exception: " + exception_str)

    # return stdout to normal
    sys.stdout = old_stdout

    out_codetext = ""
    # format result output
    if output_options.get("output_show_code"):
        out_codetext = codetext
    out_exception_str = None
    if output_options.get("output_show_exceptions"):
        out_exception_str = exception_str
    out_print_stmts = ""
    if output_options.get("output_show_print_stmts"):
        out_print_stmts = mystdout.getvalue()

    run_result_str = output_run_to_textblock(out_codetext, out_exception_str, out_print_stmts, comment_options)
    return run_result_str, finish_or_cancel

def output_run_to_textblock(code_text, exception_msg, print_stmt_str, comment_options):
    text_to_write = ""
    if comment_options.get("comment_run_start_time"):
        start_now = datetime.datetime.now()
        if comment_options.get("comment_time_microsecond"):
            text_to_write = text_to_write + start_now.strftime("### Start Time: { %p %I:%M:%S.%f").rstrip('0')
            text_to_write = text_to_write + start_now.strftime(" } Start Date: { %B %d, %Y }\n")
        else:
            text_to_write = text_to_write + start_now.strftime("### Start Time: { %p %I:%M:%S } " +
                                                               "Start Date: { %B %d, %Y }\n")
    # write any exception message
    if exception_msg != None:
        if code_text != "":
            # add comment hashtags, if needed, to codetext
            output_codetext = code_text
            if comment_options.get("comment_codetext_on_exception") or \
                comment_options.get("comment_codetext"):
                output_codetext = "#" + code_text.replace("\n", "\n#")
            # write code text
            text_to_write = text_to_write + output_codetext + "\n"
        if exception_msg != "":
            # add comment hashtags, if needed, to exception message
            output_exception_msg = exception_msg
            if comment_options.get("comment_exception_msg"):
                output_exception_msg = "# " + exception_msg.replace("\n", "\n#")
            # write exception message
            text_to_write = text_to_write + "### Exception:\n" + output_exception_msg + "\n"
    # if no exception then write code text with newline appended
    else:
        if code_text != "":
            # add comment hashtags, if needed, to codetext
            output_codetext = code_text
            if comment_options.get("comment_codetext"):
                output_codetext = "#" + code_text.replace("\n", "\n#")
            # write code text
            text_to_write = text_to_write + output_codetext + "\n"
    # add print() statement(s) output, if any
    if print_stmt_str != None and print_stmt_str != "":
        # add comment hashtags, if needed, to print() statements
        output_print_stmts = print_stmt_str
        if comment_options.get("comment_print_stmts"):
            output_print_stmts = "#" + output_print_stmts.replace("\n", "\n#")
        # write code text
        text_to_write = text_to_write + "### print() Statements:\n" + output_print_stmts + "\n"

    # finally, add the run end time comment if needed
    if comment_options.get("comment_run_end_time"):
        end_now = datetime.datetime.now()
        # use microseconds?
        if comment_options.get("comment_run_time_micros"):
            text_to_write = text_to_write + end_now.strftime("### End Time: { %p %I:%M:%S.%f").rstrip('0')
            text_to_write = text_to_write + end_now.strftime(" } End Date: { %B %d, %Y }\n")
        else:
            text_to_write = text_to_write + end_now.strftime("### End Time: { %p %I:%M:%S } End Date: { %B %d, %Y }\n")

    # add final newline as a separator
    text_to_write = text_to_write + "\n"
    # return the_text string to signal success
    return text_to_write

class PYJEF_OT_RunCodeLine(bpy.types.Operator):
    bl_idname = "pyjef.run_codeline"
    bl_label = "Run Code Line"
    bl_description = "Run the following line of code"
    bl_options = {'REGISTER', 'UNDO'}

    def run_code_line(self, context, codetext, output_options, comment_options):
        output_textblock = get_output_textblock(output_options.get("output_textblock_name"), output_options.get("output_always_new_textblock"))
        if output_textblock is None:
            self.report({"ERROR"}, "Unable to get output Textblock")
            return {'CANCELLED'}

        # run the code
        run_result_str, final_return_val = run_codetext_return_output(self, context, codetext, output_options,
                                                                      comment_options)
        # write the output of the run to Textblock
        output_textblock.write(run_result_str)

        # update the Output Textblock property, in case a new output_textblock was created
        if output_textblock != None:
            context.scene.PYJEF_OutputTextBlock = output_textblock.name
        return final_return_val

    def execute(self, context):
        scn = context.scene
        output_options = {
            "output_textblock_name": scn.PYJEF_OutputTextBlock,
            "output_show_code": scn.PYJEF_OutputShowCode,
            "output_show_exceptions": scn.PYJEF_OutputShowExceptions,
            "output_show_print_stmts": scn.PYJEF_OutputShowPrintStmts,
            "output_always_new_textblock": scn.PYJEF_AlwaysNewTextblock,
        }
        comment_options = {
            "comment_codetext": scn.PYJEF_CommentCodeText,
            "comment_codetext_on_exception": scn.PYJEF_CommentCodeTextOnException,
            "comment_exception_message": scn.PYJEF_CommentExceptionMessage,
            "comment_print_stmts": scn.PYJEF_CommentPrintStmts,
            "comment_run_start_time": scn.PYJEF_CommentRunStartTime,
            "comment_run_end_time": scn.PYJEF_CommentRunEndTime,
            "comment_run_time_micros": scn.PYJEF_CommentTimeMicrosecond,
        }
        return self.run_code_line(context, scn.PYJEF_CodeLineToRun, output_options, comment_options)

class PYJEF_OT_RunTextblock(bpy.types.Operator):
    bl_idname = "pyjef.run_textblock"
    bl_label = "Run Textblock"
    bl_description = "Run the following Textblock as a script"
    bl_options = {'REGISTER', 'UNDO'}

    def run_textblock(self, context, code_textblock_name, output_options, comment_options):
        output_textblock = get_output_textblock(output_options.get("output_textblock_name"), output_options.get("output_always_new_textblock"))
        if output_textblock is None:
            self.report({"ERROR"}, "Unable to get/create output Textblock")
            return {'CANCELLED'}
        # get the contents of the Textblock as a string
        code_textblock = bpy.data.texts.get(code_textblock_name)
        if code_textblock is None:
            self.report({"ERROR"}, "Unable to get input Textblock")
            return {'CANCELLED'}
        codetext = code_textblock.as_string()

        # run the code
        run_result_str, final_return_val = run_codetext_return_output(self, context, codetext, output_options, comment_options)
        # write the output of the run to Textblock
        output_textblock.write(run_result_str)

        # update the Output Textblock property, in case a new output_textblock was created
        if output_textblock != None:
            context.scene.PYJEF_OutputTextBlock = output_textblock.name
        return final_return_val

    def execute(self, context):
        scn = context.scene
        output_options = {
            "output_textblock_name": scn.PYJEF_OutputTextBlock,
            "output_show_code": scn.PYJEF_OutputShowCode,
            "output_show_exceptions": scn.PYJEF_OutputShowExceptions,
            "output_show_print_stmts": scn.PYJEF_OutputShowPrintStmts,
            "output_always_new_textblock": scn.PYJEF_AlwaysNewTextblock,
        }
        comment_options = {
            "comment_codetext": scn.PYJEF_CommentCodeText,
            "comment_codetext_on_exception": scn.PYJEF_CommentCodeTextOnException,
            "comment_exception_message": scn.PYJEF_CommentExceptionMessage,
            "comment_print_stmts": scn.PYJEF_CommentPrintStmts,
            "comment_run_start_time": scn.PYJEF_CommentRunStartTime,
            "comment_run_end_time": scn.PYJEF_CommentRunEndTime,
            "comment_run_time_micros": scn.PYJEF_CommentTimeMicrosecond,
        }
        return self.run_textblock(context, scn.PYJEF_TextblockToRun, output_options, comment_options)
