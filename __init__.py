import bpy
import csv
from mathutils import Vector, Euler
import os

# information needed
# Plane name
# Plane Position
# Plane Rotation
# Plane Scale
# Plane image (if any)
# Plane Video (how to get this?)
# Plane Index (Take the value of z value) (Handle the duplicates)

#Sort the planes based on the z value


bl_info = {
    "name": "Export Parallax",
    "author": "Vishwas Prakash",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Object > Export Parallax",
    "description": "Export selected objects transforms to CSV",
    "category": "Import-Export",
}

def write_selected_to_csv(context, filepath):
    # Get all selected objects
    selected_objects = sorted(context.selected_objects, key=lambda obj: obj.location.z, everse=True)
    objects_data = []
    
    for obj in selected_objects:
        # Get basic transform data
        location = obj.location
        rotation = obj.rotation_euler
        scale = obj.scale
        
        # Get hierarchy information
        children = [child.name for child in obj.children]
        children_str = "|".join(children) if children else "None"
        parent = obj.parent.name if obj.parent else "None"
        
        # Prepare data for each object
        object_data = {
            "name": obj.name,
            "type": obj.type,
            "parent": parent,
            "children": children_str,
            "location_x": location.x,
            "location_y": location.y,
            "location_z": location.z,
            "rotation_x": rotation.x,
            "rotation_y": rotation.y,
            "rotation_z": rotation.z,
            "scale_x": scale.x,
            "scale_y": scale.y,
            "scale_z": scale.z,
            "visible": obj.visible_get()
        }
        objects_data.append(object_data)
    
    # Define CSV headers
    fieldnames = [
        "name", "type", "parent", "children",
        "location_x", "location_y", "location_z",
        "rotation_x", "rotation_y", "rotation_z",
        "scale_x", "scale_y", "scale_z",
        "visible"
    ]
    
    # Write to CSV
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(objects_data)
    
    return True

class ExportSelectedTransformOperator(bpy.types.Operator):
    bl_idname = "object.export_selected_transform"
    bl_label = "Export Selected Objects"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0
    
    def execute(self, context):
        if not self.filepath:
            self.filepath = "//selected_transforms.csv"
            
        filepath = bpy.path.abspath(self.filepath)
        if not filepath.endswith('.csv'):
            filepath += '.csv'
            
        if write_selected_to_csv(context, filepath):
            self.report({'INFO'}, f"Exported {len(context.selected_objects)} objects to {filepath}")
            return {'FINISHED'}
        return {'CANCELLED'}
    
    def invoke(self, context, event):
        self.filepath = "//selected_transforms.csv"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class VIEW3D_MT_parallax_menu(bpy.types.Menu):
    bl_label = "Export Parallax"
    bl_idname = "VIEW3D_MT_parallax_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(ExportSelectedTransformOperator.bl_idname, 
                       text="Export Selected Objects to CSV")

def menu_func(self, context):
    self.layout.menu(VIEW3D_MT_parallax_menu.bl_idname)

def register():
    bpy.utils.register_class(ExportSelectedTransformOperator)
    bpy.utils.register_class(VIEW3D_MT_parallax_menu)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ExportSelectedTransformOperator)
    bpy.utils.unregister_class(VIEW3D_MT_parallax_menu)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()