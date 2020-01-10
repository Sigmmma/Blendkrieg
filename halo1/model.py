import bpy

from reclaimer.hek.defs.mode import mode_def
from reclaimer.hek.defs.mod2 import mod2_def
from reclaimer.model.jms import read_jms
from reclaimer.model.model_decompilation import extract_model

from ..scene.shapes import create_sphere

def read_halo1model(filepath):
	'''Takes a halo1 model file and turns it into a jms object.'''

	# TODO: Use a tag handler to see if these files actually are what they
	# say they are. We can get really nasty parsing problems if they aren't.

	# These two model types can be imported the same way because of their
	# nearly matching structures when built into a python object.
	if (filepath.lower().endswith('.gbxmodel')
	or filepath.lower().endswith('.model')):
		# Load model
		tag = None
		if filepath.lower().endswith('.gbxmodel'):
			tag = mod2_def.build(filepath=filepath)
		else:
			tag = mode_def.build(filepath=filepath)
		#TODO: Get all lod permutations.
		#Only getting the superhigh perms for now
		jms = extract_model(tag.data.tagdata, write_jms=False)[0]
		return jms

	if filepath.lower().endswith('.jms'):
		# Read jms file into string.
		jms_string = ""
		with open(filepath, 'r') as jms_file:
			jms_string = jms_file.read()
		# Read Jms data from string.
		jms = read_jms(jms_string)
		# Make sure it's a Halo 1 jms
		if jms.version != "8200":
			raise ValueError('Not a Halo 1 jms!')

		return jms

def import_halo1_nodes(jms, scale=1.0, node_size=0.02):
	'''
	Import all the nodes from a jms into the scene and returns a list of them.
	'''
	scene_nodes = dict()
	for i, node in enumerate(jms.nodes):
		scene_node = create_sphere(name="@"+node.name, size=node_size)

		# Assign parent if index is valid.
		if node.parent_index in range(len(scene_nodes)):
			scene_node.parent = scene_nodes[node.parent_index]

		# Store original rotation mode.
		rot_mode = scene_node.rotation_mode
		# Set rotation mode to quaternion and apply the rotation.
		scene_node.rotation_mode = 'QUATERNION'
		scene_node.rotation_quaternion = (
			-node.rot_w, node.rot_i, node.rot_j, node.rot_k
		)
		# Set rotation mode back.
		scene_node.rotation_mode = rot_mode

		# Undo 100x scaling from jms files.
		scene_node.location = (
			node.pos_x*scale, node.pos_y*scale, node.pos_z*scale
		)

		scene_nodes[i] = scene_node

	return scene_nodes
