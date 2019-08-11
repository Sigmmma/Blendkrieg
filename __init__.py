bl_info = {
    "name": "Blendkrieg",
    "author": "Multiple Authors",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Add Halo CE importers and exporters",
    "warning": "",
    "wiki_url": "https://github.com/gbMichelle/Blendkrieg/branches",
    "category": "Import-Export"
    }

if "bpy" in locals():
    import importlib
    pass  # reload the addons to register/unregister
else:
    pass  # import the addons to register/unregister

import bpy

# Register
classes = [
]

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
