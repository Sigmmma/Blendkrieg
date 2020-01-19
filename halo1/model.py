import bpy

from reclaimer.hek.defs.mode import mode_def
from reclaimer.hek.defs.mod2 import mod2_def
from reclaimer.model.jms import read_jms
from reclaimer.model.model_decompilation import extract_model

from ..constants import ( JMS_VERSION_HALO_1, NODE_SYMBOL, MARKER_SYMBOL )
from ..scene.shapes import create_sphere
from ..scene.util import apply_halo_rotation

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
		if jms.version != JMS_VERSION_HALO_1:
			raise ValueError('Not a Halo 1 jms!')

		return jms

def import_halo1_nodes(jms, *, scale=1.0, node_size=0.02):
	'''
	Import all the nodes from a jms into the scene and returns a dict of them.
	'''
	scene_nodes = dict()
	for i, node in enumerate(jms.nodes):
		scene_node = create_sphere(name=NODE_SYMBOL+node.name, size=node_size)

		# Assign parent if index is valid.
		scene_node.parent = scene_nodes.get(node.parent_index, None)

		apply_halo_rotation(scene_node,
			(node.rot_i, node.rot_j, node.rot_k, node.rot_w))

		# Scale to desired size
		scene_node.location = (
			node.pos_x*scale, node.pos_y*scale, node.pos_z*scale
		)

		scene_nodes[i] = scene_node

	return scene_nodes

def import_halo1_markers(jms, *, scale=1.0, node_size=0.01,
		scene_nodes=dict(), import_radius=False,
		permutation_filter=(), region_filter=()
		):
	'''
	Import all the markers from a given jms into a scene.

	Will parent to the nodes from scene_nodes.

	Allows you to specify what permutations you would like to isolate using
	the permutation_filter. Same goes for regions.

	The option to import radius is off by default because this radius goes
	largely unused, and will just be a nuisance to people using the tool
	otherwise.
	'''
	# The number of regions in a jms model is always known,
	# so we can just create a default range.
	if not len(permutation_filter):
		# Do markers have a -1 no region state? Because this would not work if so.
		region_filter = range(len(jms.regions))

	for marker in jms.markers:
		# Permutations cannot be known without seeking through the whole model.
		# This is an easier way to deal with not being given a filter.
		if len(permutation_filter) and not (
				marker.permutation in permutation_filter):
			# Skip if not in one of the requested permutations.
			continue

		if not (marker.region in region_filter):
			# Skip if not in one of the requested regions.
			continue

		scene_marker = create_sphere(name=MARKER_SYMBOL+marker.name,
			size=(scale if import_radius else node_size))

		# Set scale to be the size for easy changing of the marker size.
		if import_radius:
			scene_marker.scale = (
				marker.radius*scale, marker.radius*scale, marker.radius*scale)

		# Assign parent if index is valid.
		scene_marker.parent = scene_nodes.get(marker.parent, None)

		apply_halo_rotation(scene_marker,
			(marker.rot_i, marker.rot_j, marker.rot_k, marker.rot_w))

		# Scale to desired size
		scene_marker.location = (
			marker.pos_x*scale, marker.pos_y*scale, marker.pos_z*scale
		)

	#TODO: Should this return something?
