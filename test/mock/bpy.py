# A note on data types:
# Blender refers to most things in the scene as Objects. This includes meshes,
# cameras, lights, etc...
# This does NOT include collecions, which are their own thing.

# This module attempts to replicate Blender's API functionality, albeit with
# basic lists and dictionaries instead of whatever Blender is using.
# This should, in theory, be a drop-in replacement for testing.

from mathutils import Euler, Quaternion, Vector
import pymesh

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
		self.location = Vector()       # Coordinate location of this object
		self.name = None               # Name as it appears in Outliner
		self.parent = None             # The object this object is parented to
		self.rotation_euler = Euler()  # Rotation in Euler coordinates
		self.rotation_mode = 'XYZ'     # Rotation mode (or Euler coordinate order)
		self.rotation_quaternion = Quaternion() # Rotation in Quaternion coordinates
		self.scale = Vector()          # Scale of this object
		self.users_collection = set()  # All the collections this object belongs to
		self._mesh = None # The mesh associated with this object

	def to_mesh(self):
		return self._mesh

class Mesh:
	def __init__(self):
		# NOTE: Blender does not track a "triangles" field. Triangles can be
		# derived from polygons and vertices.
		self.name = None        # Name as it appears in Outliner
		self.vertices = list()  # All vertices in this mesh

class Vertex:
	def __init__(self):
		self.co = Vector() # The XYZ position of this vertex



is_mock = True # Allows tests to verify they're using the mocks
data = Data()
name_cache = {}


def clear_mock():
	data.collections.clear()
	data.meshes.clear()
	data.objects.clear()
	name_cache.clear()

def set_scene_data(nested):
	'''Uses a nested dictionary to create all of the objects in the scene.
	Collections are created by name. Parents are inferred from dict structure.
	'''
	_add_objects(nested)

# Yeah, we're using recursion. Sue me
def _add_objects(nested, parent=None, parent_colls=set()):
	for name in nested:
		obj = Object()
		obj.name = name

		loc = nested[name].get('location', Vector())
		obj.location = Vector((loc[0], loc[1], loc[2]))

		rot = nested[name].get('rotation', Euler())
		if isinstance(rot, Euler):
			# FIXME This is hard-coded as XYZ for now because mathutils 2.81.2
			# doesn't support other orders for Euler coordinates.
			# TODO is this how Blender handles setting rotation for other modes?
			obj.rotation_mode = 'XYZ'
			obj.rotation_euler = Euler((rot.x, rot.y, rot.z))
			obj.rotation_quaternion = rot.to_quaternion()
		elif isinstance(rot, Quaternion):
			obj.rotation_mode = 'QUATERNION'
			obj.rotation_quaternion = Quaternion((rot.w, rot.x, rot.y, rot.z))
			obj.rotation_euler = rot.to_euler()
		else:
			raise Exception('Invalid rotation type: ' + str(type(rot)))

		scale = nested[name].get('scale', Vector())
		obj.scale = Vector((scale[0], scale[1], scale[2]))

		mesh = _load_mesh(nested[name])
		obj._mesh = mesh

		if parent:
			obj.parent = parent
			parent.children.append(obj)

		# Create any new collections
		child_colls = set()
		for coll_name in nested[name].get('collections', set()):
			coll = data.collections.get(coll_name)
			if coll is None:
				coll = Collection()
				coll.name = coll_name
				data.collections[coll_name] = coll
			child_colls.add(coll)

		# Add all child collections as children of parent collections
		for p_coll in parent_colls:
			for c_coll in child_colls:
				p_coll.children[c_coll.name] = c_coll

		# Set up associations between object and all relevant collections
		all_colls = child_colls | parent_colls
		for coll in all_colls:
			obj.users_collection.add(coll)
			coll.objects[name] = obj

		children = nested[name].get('children')
		if children:
			_add_objects(children, parent=obj, parent_colls=all_colls)

		data.objects[name] = obj

def _load_mesh(testobj):
	meshfile = testobj.get('mesh')
	if meshfile:
		obj = pymesh.load_mesh(meshfile)

		mesh = Mesh()
		meshname = testobj.get('meshname', _unique_name('mesh'))
		mesh.name = meshname

		for v in obj.vertices:
			vert = Vertex()
			vert.co = Vector((v[0], v[1], v[2]))
			mesh.vertices.append(vert)

		data.meshes[meshname] = mesh
		return mesh

def _unique_name(name):
	global name_cache
	new_name = name
	try:
		count = name_cache[name]
		new_name += '.' + str(count)
		name_cache[name] = count + 1
	except KeyError:
		name_cache[name] = 1
	return new_name

