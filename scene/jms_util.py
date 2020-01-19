'''
Functions for interfacing Jms stuff with the Blender scene.
'''

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
