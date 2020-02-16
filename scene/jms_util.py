'''
Functions for interfacing Jms stuff with the Blender scene.
'''
from mathutils import Quaternion, Vector
from .util import set_rotation, set_translation

def set_rotation_from_jms(scene_object, jms_piece):
	'''
	Set a Blender object rotation to that of a JmsNode or JmsMarker.
	'''
	set_rotation(scene_object,
		i=jms_piece.rot_i, j=jms_piece.rot_j,
		k=jms_piece.rot_k, w=jms_piece.rot_w)

def set_translation_from_jms(scene_object, jms_piece, scale=1.0):
	'''
	Set a Blender object position to that of a JmsNode or JmsMarker.
	'''
	set_translation(scene_object, scale,
		x=jms_piece.pos_x,
		y=jms_piece.pos_y,
		z=jms_piece.pos_z)

def get_absolute_node_transforms_from_jms(node_list):
	'''
	Takes a JmsNodes list and returns the absolute transformations in a dict.
	'''
	node_transforms = {}

	for i, node in enumerate(node_list):
		translation = Vector((node.pos_x, node.pos_y, node.pos_z))
		rotation = Quaternion((-node.rot_w, node.rot_i, node.rot_j, node.rot_k))

		if node.parent_index >= 0:
			parent = node_transforms[node.parent_index]

			abs_rotation    = parent['rotation'] @ rotation
			# Rotating this way has the result end up in the instance
			# we're calling this method from.
			translation.rotate(parent['rotation'])
			abs_translation = parent['translation'] + translation
		else:
			abs_translation = translation
			abs_rotation    = rotation

		node_transforms[i] = {
			'translation': abs_translation,
			'rotation': abs_rotation,
		}

	return node_transforms
