'''
Functions for interfacing Halo stuff with the Blender scene.
'''
import itertools

from mathutils import Vector

def set_rotation(scene_object, *, i=0.0, j=0.0, k=0.0, w=-1.0):
	'''
	Helper to apply a rotation from Halo to an object in the scene.
	'''
	# Store original rotation mode.
	rot_mode = scene_object.rotation_mode
	# Set rotation mode to quaternion and apply the rotation.
	scene_object.rotation_mode = 'QUATERNION'
	scene_object.rotation_quaternion = (-w, i, j, k)
	# Set rotation mode back.
	scene_object.rotation_mode = rot_mode

def get_rotation(scene_object):
	'''
	Takes a Blender object and returns a dict with the Halo rotation values.
	'''
	# Store original rotation mode.
	rot_mode = scene_object.rotation_mode
	# Set rotation mode to quaternion.
	scene_object.rotation_mode = 'QUATERNION'
	# Get the rotation values.
	rotation = scene_object.rotation_quaternion
	# Set rotation mode back.
	scene_object.rotation_mode = rot_mode
	# Return them.
	return {
		'i': rotation[1],
		'j': rotation[2],
		'k': rotation[3],
		'w': -rotation[0],
	}

def set_translation(scene_object, scale=1.0, *, x=0.0, y=0.0, z=0.0):
	'''
	Helper for applying a Halo position to Blender objects.
	'''
	scene_object.location = (x * scale, y * scale, z * scale)

def get_translation(scene_object, scale=1.0):
	'''
	Helper for retrieving a Halo position from a Blender object.
	'''
	pos = scene_object.location
	return {
		'x': pos[0] / scale,
		'y': pos[1] / scale,
		'z': pos[2] / scale,
	}

def set_uniform_scale(scene_object, scale=1.0):
	'''Takes a blender object and sets all of its axis to the same scale.'''
	scene_object.scale = (scale, scale, scale)

def reduce_vertices(verts, tris):
	'''
	Takes a set of preprocessed vertices and triangles and deletes unused
	vertices.
	'''

	# Get a tuple of all unique vertex indices used by the tris
	used_indices = tuple(set(itertools.chain(*tris)))

	# Translation dict that will contain the used_indices as keys,
	# and their new indices as values.
	translation_dict = {}
	# List of unique vertices.
	new_verts = []

	for old_i in used_indices:
		# Get the next index in the new_verts list
		next_i = len(new_verts)
		# Get the translated id for this vertex. Use the next id if not.
		new_i = translation_dict.setdefault(old_i, next_i)

		# This shouldn't be possible. But better to be paranoid than sorry.
		assert new_i <= next_i, "Reached an invalid id."

		# If the new index is actually new we append its corresponding vertex
		# to our new vertex list.
		if not new_i < next_i:
			new_verts.append(verts[old_i])

	# Convert the vertex ids in the triangles to ids that properly reference
	# the new list.
	new_tris = map(
		lambda t : (
			translation_dict[t[0]],
			translation_dict[t[1]],
			translation_dict[t[2]],
		), tris
	)

	# Return as tuples because they are nice and fast.
	return tuple(new_verts), tuple(new_tris), translation_dict

def trace_into_direction(direction, distance=10000.0):
	'''
	Creates a point at (default) 10000 units into the given direction.
	Supports Euler, Quaternion, Matrix.
	'''
	# First we create the point at the distance we want it.
	point = Vector((distance, 0.0, 0.0))
	# Then we rotate it from the 0 0 0 point so it's in the direction given
	# as a function input.
	point.rotate(direction)

	return point
