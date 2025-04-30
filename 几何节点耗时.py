bl_info = {
    "name": "Geometry Node Execution Time",
    "author": "一尘不染",
    "blender": (3, 0, 0),
    "version": (2, 0, 0),
    "category": "Node"
}

import bpy
import blf
import os
import mathutils
from bpy.app.handlers import persistent

# Config
FONT_SIZE = 20
FONT_COLOR = (1, 1, 1, 1.0)
FONT_TYPE_PATH = ""
TIME_LENGTH = 5
POSITION_CORNER = 'Top Left'
POSITION_OFFSET = (-35, -25)

handler_time = []

# Toggle property
def register_properties():
    bpy.types.Scene.show_gn_execution_time = bpy.props.BoolProperty(
        name="GN Execution Time",
        description="Show Geometry Node modifier execution time",
        default=True,
        update=lambda self, context: update_draw_handler()
    )

def unregister_properties():
    del bpy.types.Scene.show_gn_execution_time

# Get execution time safely
def get_gn_execution_time():
    try:
        context = bpy.context
        obj = context.object
        if not obj or not obj.modifiers:
            return ""
        active = obj.modifiers.active
        if not active or active.type != "NODES":
            return ""
        depsgraph = context.evaluated_depsgraph_get()
        evaluated_obj = obj.evaluated_get(depsgraph)
        modifier = evaluated_obj.modifiers.get(active.name)
        if not modifier:
            return ""
        return str(modifier.execution_time * 1000)[:TIME_LENGTH] + "ms"
    except Exception:
        return ""

# Draw execution time
def draw_time_in_interface():
    context = bpy.context
    if not context.scene or not context.scene.show_gn_execution_time:
        return
    if context.area.ui_type != 'GeometryNodeTree':
        return

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

# Add toggle to overlay panel
def add_to_node_pt_overlay_show_time(self, context):
    if context.area.ui_type == 'GeometryNodeTree':
        layout = self.layout
        layout.prop(context.scene, "show_gn_execution_time")

# Redraw on load
@persistent
def load_post_handler_draw(dummy):
    update_draw_handler()

# Setup draw handler
def update_draw_handler():
    while handler_time:
        bpy.types.SpaceNodeEditor.draw_handler_remove(handler_time.pop(), 'WINDOW')

    if bpy.context.scene and bpy.context.scene.show_gn_execution_time:
        handler_time.append(
            bpy.types.SpaceNodeEditor.draw_handler_add(draw_time_in_interface, (), 'WINDOW', 'POST_PIXEL')
        )
    for area in bpy.context.screen.areas:
        if area.type == 'NODE_EDITOR':
            area.tag_redraw()

# Register functions
def register():
    register_properties()
    bpy.types.NODE_PT_overlay.append(add_to_node_pt_overlay_show_time)
    bpy.app.handlers.load_post.append(load_post_handler_draw)
    update_draw_handler()

def unregister():
    bpy.types.NODE_PT_overlay.remove(add_to_node_pt_overlay_show_time)
    bpy.app.handlers.load_post.remove(load_post_handler_draw)
    unregister_properties()
    while handler_time:
        bpy.types.SpaceNodeEditor.draw_handler_remove(handler_time.pop(), 'WINDOW')

if __name__ == "__main__":
    register()
