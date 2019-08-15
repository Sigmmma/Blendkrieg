from bpy.utils import register_class, unregister_class
from bpy.types import Menu, TOPBAR_MT_editor_menus

class TOPBAR_MT_krieg(Menu):
    bl_idname = "TOPBAR_MT_krieg_ext"
    bl_label = "Krieg"

    def draw(self, context):
        layout = self.layout

        layout.menu("TOPBAR_MT_krieg_import", icon='IMPORT')
        layout.menu("TOPBAR_MT_krieg_export", icon='EXPORT')

        layout.separator()

        layout.operator(
            "wm.url_open", text="Manual", icon='HELP'
        ).url = "https://github.com/gbMichelle/Blendkrieg/wiki"
        layout.operator(
            "wm.url_open", text="GitHub", icon='URL'
        ).url = "https://github.com/gbMichelle/Blendkrieg"


class TOPBAR_MT_krieg_import(Menu):
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout

        # Halo 1:

        layout.separator()

        # Whatever else:


class TOPBAR_MT_krieg_export(Menu):
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout

        # Halo 1:

        layout.separator()

        # Whatever else:


# Enumerate all classes for easy register/unregister.
classes = (
    TOPBAR_MT_krieg,
    TOPBAR_MT_krieg_import,
    TOPBAR_MT_krieg_export,
)

# When appended to another menu class
# this will execute after the built in draw()
def draw_krieg_button(self, context):
    '''
    When appended to another menu class this
    function will execute after the built-in draw(),
    and draw the 'Krieg' button.
    '''
    self.layout.menu(TOPBAR_MT_krieg.bl_idname, text=TOPBAR_MT_krieg.bl_label)

def register():
    for cls in classes:
        register_class(cls)

    TOPBAR_MT_editor_menus.append(draw_krieg_button)

def unregister():
    TOPBAR_MT_editor_menus.remove(draw_krieg_button)

    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
