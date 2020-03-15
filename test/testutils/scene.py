'''The code that translates our test data format into actual Blender objects.

This module shouldn't be imported directly. Use the public exports from
__init__.py like this instead:
from test import testdata
'''
import bpy
from mathutils import Euler, Quaternion, Vector

def clear_scene():
	'''Nuke everything in the scene.
	You should probably be calling this after each test.
	'''
	bpy.ops.wm.read_factory_settings(use_empty=True)


def set_scene_data(testdata):
	'''Initialize a scene with some known test data.'''
	process_obj_table(testdata)


def process_obj_table(table, parent=None, parent_colls=[]):
	'''Processes a map of {name: data} object pairs.

	data - A single object in our test format.
	parent - A Blender object to parent the new object to.
	parent_colls - Blender collections to add the new object to.
	'''
	for name, data in table.items():
		data['name'] = name
		read_in_obj(data, parent=parent, parent_colls=parent_colls)


def read_in_obj(data, parent=None, parent_colls=[]):
	'''Translate our test format into a Blender object.
	The object (and any collections) will be added to the scene.

	data - A single object in our test format.
	parent - A Blender object to parent the new object to.
	parent_colls - Blender collections to add the new object to. If empty, the
	               new object will be linked to the scene's collection.
	'''
	# TODO mesh here
	# TODO detect case where two meshes explicitly specify the same name
	obj = bpy.data.objects.new(data.get('name'), None)

	obj.location = Vector(data.get('location', (0, 0, 0)))
	obj.scale    = Vector(data.get('scale', (1, 1, 1)))
	obj.parent   = parent

	rot = data.get('rotation', Euler())
	if isinstance(rot, Euler):
		obj.rotation_mode  = rot.order
		obj.rotation_euler = rot
	elif isinstance(rot, Quaternion):
		obj.rotation_mode       = 'QUATERNION'
		obj.rotation_quaternion = rot
	else:
		raise Exception('Invalid rotation type: ' + str(type(rot)))

	# Associate the object with the appropriate collections
	obj_colls = add_new_collections(
		data.get('collections', []),
		parent_colls=parent_colls)
	obj_colls.extend(parent_colls)
	obj_colls = list(set(obj_colls))
	if obj_colls:
		for coll in obj_colls:
			coll.objects.link(obj)
	else:
		bpy.context.scene.collection.objects.link(obj)

	process_obj_table(data.get('children', {}),
		parent=obj,
		parent_colls=obj_colls)


def add_new_collections(new_coll_names, parent_colls=[]):
	'''Adds new collections by name if they don't exist, and associates them
	with any parent collections.

	new_coll_names - A list of names of new collections to make.
	parent_colls - A list of Blender collection objects to associate with every
	               new collection. If not provided, new collections are linked
	               to the scene itself.

	Returns the list of new collections.
	'''
	new_colls = []
	for name in new_coll_names:
		coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
		new_colls.append(coll)

		if parent_colls:
			for parent in parent_colls:
				maybe_link(parent.children, coll)
		else:
			maybe_link(bpy.context.scene.collection.children, coll)

	return new_colls

def maybe_link(parent, obj):
	'''Link the obj to the parent if it isn't already linked'''
	if not parent.get(obj.name):
		parent.link(obj)

# TODO remove this stuff. It's just here for reference.
#me = bpy.data.meshes.new('blah')
#ob = bpy.data.objects.new('blah', me)
#bpy.context.scene.collection.objects.link(ob)
