bl_info = {
    "name": "Blendkrieg",
    "author": "gbMichelle & Mimickal",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Top-Bar > Krieg",
    "description": "Adds Halo importers, exporters, and Helper tools.",
    "warning": "",
    "wiki_url": "https://github.com/gbMichelle/Blendkrieg/wiki",
    "category": "Import-Export"
    }


def register():
    '''
    Registers classes on load by calling the
    register functions in their respective modules.
    '''
    pass

def unregister():
    '''
    Unregisters classes on unload by calling the
    unregister functions in their respective modules.
    '''
    pass

if __name__ == "__main__":
    register()
