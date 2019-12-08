import bpy
from bpy.utils import register_class, unregister_class
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper, orientation_helper, path_reference_mode, axis_conversion

from ...halo1.model import read_halo1model, import_halo1_nodes

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
	node_size: FloatProperty(
		name="Node Scene Size",
		description="Set the size that nodes should have in the Blender scene if at 1.0 scale.",
		default=0.1,
		min=0.0,
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
		min=0.0,
	)

	def execute(self, context):
		# Set appropriate scaling
		# TODO: All of these need constants.
		scale = 1.0
		if self.scale_enum == 'METRIC':
			scale = 10.0/0.032808/100.0
		elif self.scale_enum == 'MAX':
			scale = 100
		elif self.scale_enum == 'HALO':
			scale = 1.0
		elif self.scale_enum == 'CUSTOM':
			scale = self.scale_float
		else:
			raise ValueError('Invalid scale_enum state.')

		# Test if jms import function doesn't crash.
		jms = read_halo1model(self.filepath)

		# Import nodes into the scene.
		nodes = import_halo1_nodes(jms, scale=scale, node_size=self.node_size)

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout

		# Node settings elements:

		box = layout.box()
		row = box.row()
		row.label(text="Nodes:")
		row.prop(self, "use_nodes")
		if self.use_nodes:
			box.prop(self, "node_size")
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
