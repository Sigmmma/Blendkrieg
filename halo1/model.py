import bpy
import itertools
import math

from mathutils import Euler

from reclaimer.hek.defs.mode import mode_def
from reclaimer.hek.defs.mod2 import mod2_def
from reclaimer.model.jms import read_jms
from reclaimer.model.model_decompilation import extract_model
from reclaimer.util.geometry import point_distance_to_line

from ..constants import (JMS_VERSION_HALO_1, NODE_NAME_PREFIX,
	MARKER_NAME_PREFIX)
from ..scene.shapes import create_sphere
from ..scene.util import (set_uniform_scale, reduce_vertices, trace_into_direction)
from ..scene.jms_util import (set_rotation_from_jms,
	set_translation_from_jms, get_absolute_node_transforms_from_jms)

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


from mathutils import Vector

def import_halo1_nodes_from_jms(jms, *,
		scale=1.0,
		node_size=0.02,
		max_attachment_distance=0.00001,
		attach_bones=('bip01',)):
	'''
	Import all the nodes from a jms into the scene as an armature and returns
	a dict of them.

	node_size is currently unused and may be depricated.

	max_attachment_distance is the max distance a bone may deviate from
	the line that signifies the direction of the parent.

	attach_bones is a tuple of name prefixes that this function should attempt
	to connect.

	Returns the armature object and a dict of index - bone pairs.
	'''
	view_layer = bpy.context.view_layer

	scene_nodes = {}

	absolute_transforms = get_absolute_node_transforms_from_jms(jms.nodes)

	armature = bpy.data.armatures.new('imported')
	armature_obj = bpy.data.objects.new('imported', armature)

	# We need to specifically link the object to this so we can use mode_set
	# to set Blender to edit mode.

	view_layer.active_layer_collection.collection.objects.link(armature_obj)
	view_layer.objects.active = armature_obj

	# We need to be in edit mode in order to be able to edit armatures at all.

	edit_bones = armature.edit_bones
	bpy.ops.object.mode_set(mode='EDIT')

	# "directions" of where each node is pointing for the attachment progress.
	# These really are just points that are offset 1000 units in the direction
	# the node is pointing from the point of the node's in scene head.
	# These are used so we can check if two bones should be attached.
	directions = {}

	for i, node in enumerate(jms.nodes):
		scene_node = edit_bones.new(name=NODE_NAME_PREFIX+node.name)

		# Assign parent if index is valid.
		scene_node.parent = scene_nodes.get(node.parent_index, None)

		# If a node has multiple children we cannot connect its tail end
		# to the children.

		pos = absolute_transforms[i]['translation']
		rot = absolute_transforms[i]['rotation']

		# Bones when created start at 0 0 0 for their tail and head.
		# We set the X of the tail, so it's not 0 length.
		# X also is the forward direction for Halo bones.

		scene_node.tail.x = 0.2

		# We then rotate the bone by the absolute rotation that it should have.

		scene_node.transform(rot.to_matrix(), scale=False)

		# Then we add the absolute location to both the head and the tail.

		scene_node.head += Vector(
			(pos[0] * scale, pos[1] * scale, pos[2] * scale))
		scene_node.tail += Vector(
			(pos[0] * scale, pos[1] * scale, pos[2] * scale))

		# Store the info we gathered this cycle.
		scene_nodes[i] = scene_node

		# Store a "direction" for this node
		directions[scene_node.name] = trace_into_direction(rot)

	if len(attach_bones) > 0:
		print('Checking if any bones with the prefixes %s can be connected.\n' %
				(attach_bones,))

	# Add the node prefix to in-tag prefixes that we should attempt to connect.
	attach_bones = tuple(map(lambda p : NODE_NAME_PREFIX + p, attach_bones))

	# Attach all the bones that we should attach if we can safely do so.
	for bone in armature.edit_bones:
		children = bone.children

		if (len(children) == 1 # Can't connect to multiple children, so don't.
		and bone.name.startswith(attach_bones)
		and children[0].name.startswith(attach_bones)):
			child = children[0]

			distance = point_distance_to_line(
				child.head,
				(bone.head, directions[bone.name]),
				use_double_rounding=False)

			if distance < max_attachment_distance:
				print("Connecting %r to %r with distance %.12f" %
						(child.name, bone.name, distance))
				# If the child bone's head is on a line with the parent's tail
				# direction we can set the parent tail to the location of the
				# child head.
				bone.tail = child.head
				# Connect the bone so it stays attached when editing.
				child.use_connect = True

	# Change back to object mode so the rest of the script can execute properly.

	bpy.ops.object.mode_set(mode='OBJECT')

	return armature_obj, scene_nodes

def import_halo1_markers_from_jms(jms, *, armature=None, scale=1.0, node_size=0.01,
		scene_nodes={}, import_radius=False,
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

		scene_marker = create_sphere(
			name=MARKER_NAME_PREFIX+marker.name,
			size=(scale if import_radius else node_size))

		# Make the marker invisible in renders.
		scene_marker.hide_render = True

		# Set scale to be the size for easy changing of the marker size.
		if import_radius:
			set_uniform_scale(scene_marker, marker.radius)

		set_rotation_from_jms(scene_marker, marker)

		set_translation_from_jms(scene_marker, marker, scale)

		# Assign parent if index is valid.
		parent = scene_nodes.get(marker.parent, None)
		if armature and parent:
			scene_marker.parent = armature
			scene_marker.parent_type = 'BONE'
			scene_marker.parent_bone = parent.name

			# The rotation is offset by 0, 0, -90 euler, so we rotate it to
			# fix that.

			scene_marker.location.rotate(Euler((0.0, 0.0, math.radians(90.0))))

			# Then we subtract the length of the parent bone from the y axis,
			# the y axis being the axis that is offset.

			# In Halo, marker positions are relative to the start of their
			# parent bone. In blender they are relative to the end of the bone.
			# So, we subtract the length of the bone from the y axis to
	        # make the final positions match up.
			scene_marker.location.y -= parent.length

	#TODO: Should this return something?

def import_halo1_region_from_jms(jms, *,
		name="unnamed",
		scale=1.0,
		region_filter=(),
		parent_rig=None,
		skin_vertices=True):
	'''
	Imports all the geometry into a Halo 1 JMS into the scene.

	Only imports the regions in the region filter.

	mesh object gets linked to parent_rig and skinned to the bones if
	skin_vertices is True and the parent is an ARMATURE object.
	'''

	if not region_filter:
		region_filter = range(len(jms.regions))

	### Geometry preprocessing.

	# Ready the vertices.
	vertices = tuple(map(
			lambda v : (v.pos_x * scale, v.pos_y * scale, v.pos_z * scale),
			jms.verts
		)
	)

	# Ready the triangles.

	# Filter the triangles so only the wished regions are retrieved.
	triangles = filter(lambda t : t.region in region_filter, jms.tris)

	# Reduce the triangles to just their key components.
	triangles = tuple(map(lambda t : (t.v0, t.v1, t.v2), triangles))

	# Unpack the vertex normals.
	vertex_normals = tuple(
		map(lambda v : (v.norm_i, v.norm_j, v.norm_k), jms.verts)
	)

	# Convert the vertex normals to triangle normals.
	tri_normals = map(
		lambda t : (
			vertex_normals[t[0]],
			vertex_normals[t[1]],
			vertex_normals[t[2]]),
		triangles
	)

	# Collect UVs

	vert_uvs = tuple(map(lambda v : (v.tex_u, v.tex_v), jms.verts))

	tri_uvs = tuple(map(
		lambda t : (
			vert_uvs[t[0]],
			vert_uvs[t[1]],
			vert_uvs[t[2]]),
		triangles
	))

	# Remove unused vertices
	vertices, triangles, translation_dict = reduce_vertices(vertices, triangles)

	# Chain all of the triangle normals together into loop normals.
	# ((x, y, z), (x, y, z), (x, y, z)), ((x, y, z), (x, y, z), (x, y, z)),
	#    |    |    |
	#    V    V    V
	# ((x, y, z), (x, y, z), (x, y, z), (x, y, z), (x, y, z), (x, y, z)),
	# Loops are the points of triangles so to speak.

	loop_normals = tuple(itertools.chain(*tri_normals))

	loop_uvs = tuple(itertools.chain(*tri_uvs))

	### Importing the data into a mesh

	# Make a mesh to hold all relevant data.
	mesh = bpy.data.meshes.new(name)

	# Import the verts and tris into the mesh.
	# verts, edges, tris. If () is given for edges Blender will infer them.
	mesh.from_pydata(vertices, (), triangles)

	# Import loop normals into the mesh.
	mesh.normals_split_custom_set(loop_normals)

	# Setting this to true makes Blender display the custom normals.
	# It feels really wrong. But it is right.
	mesh.use_auto_smooth = True

	# Apply the UVs

	for loop, uvs in zip(mesh.uv_layers.new().data, loop_uvs):
		loop.uv = uvs

	# Validate the mesh and make sure it doesn't have any invalid indices.
	mesh.validate()

	# Create the object, and link it to the scene.
	region_obj = bpy.data.objects.new(name, mesh)
	scene = bpy.context.collection
	scene.objects.link(region_obj)

	# If the function was supplied with a parent object attempt to skin to it
	# if it is an ARMATURE.

	region_obj.parent = parent_rig

	if skin_vertices and region_obj.parent.type == 'ARMATURE':
		mod = region_obj.modifiers.new('armature', 'ARMATURE')
		mod.object = parent_rig

		# Create a vertex group for each bone.

		for node in jms.nodes:
			region_obj.vertex_groups.new(name=NODE_NAME_PREFIX+node.name)

		# Add the vertices to all the correct vertex groups.

		for jms_i in translation_dict:
			v = jms.verts[jms_i]
			mesh_i = translation_dict[jms_i]

			if v.node_0 != -1:
				# The first node has no skinning data in JMS files (oof)
				if v.node_1 != -1:
					region_obj.vertex_groups[v.node_0].add(
						[mesh_i], 1.0 - v.node_1_weight, 'ADD')
				else:
					region_obj.vertex_groups[v.node_0].add(
						[mesh_i], 1.0, 'ADD')

			if v.node_1 != -1:
				region_obj.vertex_groups[v.node_1].add(
					[mesh_i], v.node_1_weight, 'ADD')

	return region_obj

def import_halo1_all_regions_from_jms(jms, *, name="", scale=1.0, parent_rig=None):
	'''
	Import all regions from a given jms.
	'''
	for i in range(len(jms.regions)):
		import_halo1_region_from_jms(
			jms,
			name=name+":"+jms.regions[i],
			scale=scale,
			region_filter=(i,),
			parent_rig=parent_rig
		)
