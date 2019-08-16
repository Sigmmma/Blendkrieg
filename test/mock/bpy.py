# A note on data types:
# Blender refers to most things in the scene as Objects. This includes meshes,
# cameras, lights, etc...
# This does NOT include collecions, which are their own thing.

# This module attempts to replicate Blender's API functionality, albeit with
# basic lists and dictionaries instead of whatever Blender is using.
# This should, in theory, be a drop-in replacement for testing.

class Data:
	def __init__(self):
		self.collections = dict() # All the collections in the scene
		self.meshes = dict()      # All the mesh objects in the scene
		self.objects = dict()     # All the objects in the scene

class Collection:
	def __init__(self):
		self.children = dict() # All sub-collections in this collection
		self.name = None       # Name as it appears in Outliner
		self.objects = dict()  # All objects in this collection

class Object:
	def __init__(self):
		self.children = list()         # Objects parented to this object
		self.name = None               # Name as it appears in Outliner
		self.parent = None             # The object this object is parented to
		self.users_collection = set()  # All the collections this object belongs to


is_mock = True # Allows tests to verify they're using the mocks
data = Data()


def clear_mock():
	data.collections.clear()
	data.meshes.clear()
	data.objects.clear()

def set_scene_data(nested):
	'''Uses a nested dictionary to create all of the objects in the scene.
	Collections are created by name. Parents are inferred from dict structure.
	'''
	_add_objects(nested)

# Yeah, we're using recursion. Sue me
def _add_objects(nested, parent=None):
	for name in nested:
		obj = Object()
		obj.name = name

		if parent:
			obj.parent = parent
			parent.children.append(obj)

		for coll_name in nested[name].get('collections', {}):
			coll_obj = data.collections.get(coll_name, Collection())
			coll_obj.name = coll_name
			coll_obj.objects[name] = obj
			data.collections[coll_name] = coll_obj
			obj.users_collection.append(coll_obj)

		children = nested[name].get('children')
		if children:
			_add_objects(children, parent=obj)

		data.objects[name] = obj

