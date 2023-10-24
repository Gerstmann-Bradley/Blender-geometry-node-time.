# Metadata about the add-on
bl_info = {
    "name" : "Geometry Node Execution Time",
    "author" : "一尘不染",  # Author's name (一尘不染 in this case)
    "blender" : (3, 0, 0),  # Compatible Blender version
    "version" : (1, 3, 0),  # Version of the add-on
    "category" : "Node"  # Category where the add-on is located
}

# Import necessary modules
import bpy
from bpy import props
import bpy.utils.previews
import blf
import os
import mathutils
from bpy.app.handlers import persistent

# Function to update the interface when a property changes
def update_show_in_interface(self, context):
    updated_prop = self.show_in_interface
    if updated_prop:
        function_start_draw_gn_time()
    else:
        for i in range(2):
            if handler_time:
                bpy.types.SpaceNodeEditor.draw_handler_remove(handler_time[0], 'WINDOW')
                handler_time.pop(0)
                for a in context.screen.areas: 
                    a.tag_redraw()

# Initialize a list to store draw handler information
handler_time = []

# Function to add properties to the Geometry Node Editor's overlay panel
def add_to_node_pt_overlay_show_time(self, context):
    addon_prefs = context.preferences.addons[__name__].preferences
    if context.area.ui_type == 'GeometryNodeTree':
        layout = self.layout
        layout.separator(factor=0.5)
        layout.prop(addon_prefs, 'show_in_header', text='Show in Header')
        layout.prop(addon_prefs, 'show_in_interface', text='Show in Interface')

# Function to get the execution time of the Geometry Nodes
def get_gn_execution_time():
    try:
        context = bpy.context
        tree = context.space_data.edit_tree
        active = context.object.modifiers.active
        addon_prefs = context.preferences.addons[__name__].preferences
        if context.area.ui_type == 'GeometryNodeTree':
            for modifier in context.object.modifiers:
                if modifier.type == "NODES" and modifier.node_group.name == tree.name:
                    mod_name = modifier.name
            if active.name == mod_name:
                DependencyGraph = context.evaluated_depsgraph_get()
                EvaluatedObject = context.object.evaluated_get(DependencyGraph)
                modifier = EvaluatedObject.modifiers[mod_name]
                time = modifier.execution_time
                return str(time * 1000)[:addon_prefs.time_length] + "ms"
    except:
        return ""

# Function to add execution time to the header of the Geometry Node Editor
def add_to_node_ht_header_show_time(self, context):
    if context.preferences.addons[__name__].preferences.show_in_header:
        layout = self.layout
        if context.area.ui_type == 'GeometryNodeTree':
            layout.label(text=get_gn_execution_time(), icon_value=118)

# Function to draw execution time information in the interface
def draw_time_in_interface():
    context = bpy.context
    addon_prefs = context.preferences.addons[__name__].preferences
    if context.area.ui_type == 'GeometryNodeTree':
        font_id = 0
        if addon_prefs.font_type and os.path.exists(addon_prefs.font_type):
            font_id = blf.load(addon_prefs.font_type)
        if font_id == -1:
            print("Couldn't load font!")
        else:
            width = context.area.width - 50.0
            height = context.area.height - 50.0
            position_corner = addon_prefs.position_corner
            corner = {
                'Bottom Right': (width, 50),
                'Top Right': (width, height),
                'Top Left': (50, height),
                'Bottom Left': (50, 50)
            }
            x_offect, y_offect = tuple(mathutils.Vector(corner[position_corner]) + mathutils.Vector(addon_prefs.position_offect))
            blf.position(font_id, x_offect, y_offect, 0)
            if bpy.app.version >= (3, 4, 0):
                blf.size(font_id, addon_prefs.font_size)
            else:
                blf.size(font_id, addon_prefs.font_size, 72)
            clr = addon_prefs.font_color
            blf.color(font_id, clr[0], clr[1], clr[2], clr[3])
            if 15:
                blf.enable(font_id, blf.WORD_WRAP)
                blf.word_wrap(font_id, 15)
            if 0.0:
                blf.enable(font_id, blf.ROTATION)
                blf.rotation(font_id, 0.0)
            blf.enable(font_id, blf.WORD_WRAP)
            blf.draw(font_id, get_gn_execution_time())
            blf.disable(font_id, blf.ROTATION)
            blf.disable(font_id, blf.WORD_WRAP)

# Define preferences for the add-on
class AddonPreferences_Show_GN_Time(bpy.types.AddonPreferences):
    bl_idname = __name__
    show_in_header:    props.BoolProperty(name='Show_in_Header', description='Show in Header', default=True)
    show_in_interface: props.BoolProperty(name='Show_in_Interface', description='Show_in_Interface', default=False, 
                                          update=update_show_in_interface)
    font_size:         props.IntProperty(name='Font_Size', description='', default=20, subtype='NONE')
    font_color:        props.FloatVectorProperty(name='Font_Color', description='', size=4, default=(1, 1, 1, 1.0), 
                                                 subtype='COLOR', unit='NONE', min=0.0, max=1.0, step=3, precision=6)
    font_type:         props.StringProperty(name='Font_Type', description='', default='', subtype='FILE_PATH', maxlen=0)
    time_length:       props.IntProperty(name='Time_Length', description='', default=5, subtype='NONE', min=2, max=10)

    def position_corner_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    position_corner:   props.EnumProperty(name='Position_Corner', description='', 
                                            items=[('Bottom Left', 'Bottom Left', '', 0, 0), 
                                                   ('Top Left', 'Top Left', '', 0, 1), 
                                                   ('Bottom Right', 'Bottom Right', '', 0, 2),
                                                   ('Top Right', 'Top Right', '', 0, 3) ])
    position_offset:   props.IntVectorProperty(name='Position_Offset', description='', size=2, default=(0, 1), subtype='NONE')

# Function to draw the preferences in Blender's Preferences panel
def draw(self, context):
    addon_prefs = context.preferences.addons[__name__].preferences
    layout = self.layout

    split_0 = layout.split(factor=0.5)
    split_0.label(text='Show in Header:')
    split_0.prop(addon_prefs, 'show_in_header', text='', icon_value=0, emboss=True)

    split_0 = layout.split(factor=0.5)
    split_0.label(text='Show in Interface:')
    split_0.prop(addon_prefs, 'show_in_interface', text='')

    split_1 = layout.split(factor=0.5)
    split_1.label(text='Font Size:')
    split_1.prop(addon_prefs, 'font_size', text='', icon_value=0, emboss=True)

    split_2 = layout.split(factor=0.5)
    split_2.label(text='Font Color:')
    split_2.prop(addon_prefs, 'font_color', text='')

    split_3 = layout.split(factor=0.5)
    split_3.label(text='Font Type:')
    split_3.prop(addon_prefs, 'font_type', text='')

    split_4 = layout.split(factor=0.5)
    split_4.label(text='Number Length:')
    split_4.prop(addon_prefs, 'time_length', text='')

    split_5 = layout.split(factor=0.5)
    split_5.label(text='Position Corner:')
    split_5.prop(addon_prefs, 'position_corner', text='')

    split_6 = layout.split(factor=0.5)
    split_6.label(text='Position Offset:')
    split_6.prop(addon_prefs, 'position_offect', text='')

# Function to handle events after loading the file
@persistent
def load_post_handler_draw(dummy):
    if bpy.context.preferences.addons[__name__].preferences.show_in_interface:
        function_start_draw_gn_time()

# Function to start drawing execution time
def function_start_draw_gn_time():
    handler_time.append(bpy.types.SpaceNodeEditor.draw_handler_add(draw_time_in_interface, (), 'WINDOW', 'POST_PIXEL'))
    for a in bpy.context.screen.areas: 
        a.tag_redraw()

# Register the add-on
def register():
    bpy.types.NODE_PT_overlay.append(add_to_node_pt_overlay_show_time)
    bpy.types.NODE_HT_header.append(add_to_node_ht_header_show_time)
    bpy.utils.register_class(AddonPreferences_Show_GN_Time)
    bpy.app.handlers.load_post.append(load_post_handler_draw)

# Unregister the add-on
def unregister():
    bpy.types.NODE_PT_overlay.remove(add_to_node_pt_overlay_show_time)
    bpy.types.NODE_HT_header.remove(add_to_node_ht_header_show_time)
    bpy.utils.unregister_class(AddonPreferences_Show_GN_Time)
    bpy.app.handlers.load_post.remove(load_post_handler_draw)
    if handler_time:
        bpy.types.SpaceNodeEditor.draw_handler_remove(handler_time[0], 'WINDOW')
        handler_time.pop(0)
