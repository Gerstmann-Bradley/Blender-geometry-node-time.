# Metadata about the add-on
bl_info = {
    "name": "Geometry Node Execution Time",
    "author": "一尘不染",
    "blender": (3, 0, 0),
    "version": (1, 4, 0),
    "category": "Node"
}

# Import necessary modules
import bpy
import blf
import os
import mathutils
from bpy.app.handlers import persistent

# Hardcoded configuration
DRAW_IN_INTERFACE = True
FONT_SIZE = 20
FONT_COLOR = (1, 1, 1, 1.0)
FONT_TYPE_PATH = ""
TIME_LENGTH = 5
POSITION_CORNER = 'Top Left'
POSITION_OFFSET = (-35, -25)

# Initialize a list to store draw handler information
handler_time = []

# Function to get the execution time of the Geometry Nodes
def get_gn_execution_time():
    try:
        context = bpy.context
        tree = context.space_data.edit_tree
        active = context.object.modifiers.active
        for modifier in context.object.modifiers:
            if modifier.type == "NODES" and modifier.node_group.name == tree.name:
                mod_name = modifier.name
        if active.name == mod_name:
            depsgraph = context.evaluated_depsgraph_get()
            evaluated_obj = context.object.evaluated_get(depsgraph)
            modifier = evaluated_obj.modifiers[mod_name]
            time = modifier.execution_time
            return str(time * 1000)[:TIME_LENGTH] + "ms"
    except:
        return ""

# Function to draw execution time information in the interface
def draw_time_in_interface():
    context = bpy.context
    if context.area.ui_type == 'GeometryNodeTree':
        font_id = 0
        if FONT_TYPE_PATH and os.path.exists(FONT_TYPE_PATH):
            font_id = blf.load(FONT_TYPE_PATH)
        if font_id == -1:
            return
        width = context.area.width - 50.0
        height = context.area.height - 50.0
        corner_coords = {
            'Bottom Right': (width, 50),
            'Top Right': (width, height),
            'Top Left': (50, height),
            'Bottom Left': (50, 50)
        }
        x_offset, y_offset = tuple(mathutils.Vector(corner_coords[POSITION_CORNER]) + mathutils.Vector(POSITION_OFFSET))
        blf.position(font_id, x_offset, y_offset, 0)
        if bpy.app.version >= (3, 4, 0):
            blf.size(font_id, 12)
        else:
            blf.size(font_id, FONT_SIZE, 72)
        blf.color(font_id, *FONT_COLOR)
        blf.enable(font_id, blf.WORD_WRAP)
        blf.word_wrap(font_id, 15)
        blf.draw(font_id, get_gn_execution_time())
        blf.disable(font_id, blf.WORD_WRAP)

# Function to update the draw handler based on config
def update_draw_handler():
    if DRAW_IN_INTERFACE:
        function_start_draw_gn_time()
    else:
        for i in range(2):
            if handler_time:
                bpy.types.SpaceNodeEditor.draw_handler_remove(handler_time[0], 'WINDOW')
                handler_time.pop(0)
                for a in bpy.context.screen.areas:
                    a.tag_redraw()

# Function to add a label to the node editor overlay (basic static label only)
def add_to_node_pt_overlay_show_time(self, context):
    if context.area.ui_type == 'GeometryNodeTree':
        layout = self.layout
        layout.label(text="GN Execution Time")

# Function to handle events after loading the file
@persistent
def load_post_handler_draw(dummy):
    if DRAW_IN_INTERFACE:
        function_start_draw_gn_time()

# Function to start drawing execution time
def function_start_draw_gn_time():
    if not handler_time:
        handler_time.append(bpy.types.SpaceNodeEditor.draw_handler_add(draw_time_in_interface, (), 'WINDOW', 'POST_PIXEL'))
        for a in bpy.context.screen.areas:
            a.tag_redraw()

# Register the add-on
def register():
    bpy.types.NODE_PT_overlay.append(add_to_node_pt_overlay_show_time)
    bpy.app.handlers.load_post.append(load_post_handler_draw)
    update_draw_handler()

# Unregister the add-on
def unregister():
    bpy.types.NODE_PT_overlay.remove(add_to_node_pt_overlay_show_time)
    bpy.app.handlers.load_post.remove(load_post_handler_draw)
    if handler_time:
        bpy.types.SpaceNodeEditor.draw_handler_remove(handler_time[0], 'WINDOW')
        handler_time.pop(0)

if __name__ == "__main__":
    register()
