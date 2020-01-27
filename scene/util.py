'''
Functions for interfacing Halo stuff with the Blender scene.
'''
import itertools

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
	Takes a set of preprocessed vertices and triangles and deletes and unused
	or double vertices.
	'''

	### Remove unused vertices

	# Get a set of all vertex indices used by the tris

	used_indices = set(itertools.chain(*tris))

	translation_dict = {}
	unique_verts = []

	for i in used_indices:
		count = len(unique_verts)

		vert = verts[i]

		new_id = translation_dict.setdefault(vert, count)

		if not new_id < count:
			unique_verts.append(vert)

	new_tris = tuple(
		map(lambda t : (
			translation_dict[verts[t[0]]],
			translation_dict[verts[t[1]]],
			translation_dict[verts[t[2]]],
			), tris
		)
	)

	return unique_verts, new_tris
