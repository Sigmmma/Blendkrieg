import bpy
from bpy.utils import register_class, unregister_class
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper, orientation_helper, path_reference_mode, axis_conversion

#@orientation_helper(axis_forward='-Z') Find the right value for this.
class MT_krieg_ImportHalo1Model(bpy.types.Operator, ImportHelper):
	"""
	The import operator for gbxmodel/jms models.
	This stores the properties when inside of the import dialog, and
	it specifies what to show on the side panel when importing.
	"""
	bl_idname = "import_scene.halo1_model"
	bl_label = "Import Halo 1 Model"
	bl_options = {'PRESET', 'UNDO'}

	# Import-file-dialog settings:

	filename_ext = ".gbxmodel"
	filter_glob: StringProperty(
		default="*.gbxmodel;*.model;*.jms",
		options={'HIDDEN'},
	)

	# Node settings:

	use_nodes: BoolProperty(
		name="Import Nodes",
		description="Import the nodes/frames.",
		default=True,
	)
	use_armatures: BoolProperty(
		name="Import Nodes as Armature",
		description="Import the nodes as armature.",
		default=False,
	)

	# Scaling settings:

	scale_enum: EnumProperty(
	name="Scale",
		items=(
			('METRIC', "Blender",  "Use Blender's metric scaling."),
			('MAX',    "3ds Max",  "Use 3dsmax's 100xHalo scale."),
			('HALO',   "Internal", "Use Halo's internal 1.0 scale (small)."),
			('CUSTOM', "Custom",   "Set your own scaling."),
		)
	)
	scale_float: FloatProperty(
		name="Custom Scale",
		description="Set your own scale.",
		default=1.0,
	)

	def execute(self, context):
		print("Use nodes: " + str(self.use_nodes))
		print("Use armatures: " + str(self.use_armatures))
		print("Scale Enum: " + str(self.scale_enum))
		print("Scale Float: " + str(self.scale_float))
		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout

		# Node settings elements:

		box = layout.box()
		row = box.row()
		row.label(text="Nodes:")
		row.prop(self, "use_nodes")
		if self.use_nodes:
			box.prop(self, "use_armatures")

		# Scale settings elements:

		box = layout.box()
		box.label(text="Scale:")
		row = box.row()
		row.prop(self, "scale_enum", expand=True)

		if self.scale_enum == 'CUSTOM':
			row = box.row()
			row.prop(self, "scale_float")


# Enumerate all classes for easy register/unregister.
classes = (
	MT_krieg_ImportHalo1Model,
)

def register():
	for cls in classes:
		register_class(cls)


def unregister():
	for cls in reversed(classes): #Reversed because: first in, last out.
		unregister_class(cls)


if __name__ == "__main__":
	register()
