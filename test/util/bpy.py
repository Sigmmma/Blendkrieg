# A note on data types:
# Blender refers to most things in the scene as Objects. This includes meshes,
# cameras, lights, etc...
# This does NOT include collecions, which are their own thing.

# This module attempts to replicate Blender's API functionality, albeit with
# basic lists and dictionaries instead of whatever Blender is using.
# This should, in theory, be a drop-in replacement for testing.

class Data:
	collections = dict() # All the collections in the scene
	meshes = dict()      # All the mesh objects in the scene
	objects = dict()     # All the objects in the scene

class Collection:
	children = dict() # All sub-collections in this collection
	objects = dict()  # All objects in this collection

class Object:
	children = list()         # Objects parented to this object
	name = None               # Name as it appears in Outliner
	parent = None             # The object this object is parented to
	users_collection = list() # All the collections this object belongs to

	def __init__(self, name, collection=None):
		pass

data = Data()

