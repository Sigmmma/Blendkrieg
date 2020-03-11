# A note on data types:
# Blender refers to most things in the scene as Objects. This includes meshes,
# cameras, lights, etc...
# This does NOT include collecions, which are their own thing.

# This module attempts to replicate Blender's API functionality, albeit with
# basic lists and dictionaries instead of whatever Blender is using.
# This should, in theory, be a drop-in replacement for testing.

from mathutils import Euler, Quaternion, Vector
from collada import Collada

class Data:
	def __init__(self):
		self.collections = dict() # All the collections in the scene
		self.materials = dict()   # All the materials in the scene
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
		self.type = None  # TODO do we need this?
		self.users_collection = set()  # All the collections this object belongs to
		self._mesh = None # The mesh associated with this object

	def to_mesh(self):
		return self._mesh

class Mesh:
	def __init__(self):
		# NOTE: Blender does not track a "triangles" field. Triangles can be
		# derived from polygons and vertices.
		self.edges = list()     # All edges in this mesh
		self.materials = dict() # All materials applied to this mesh
		self.name = None        # Name as it appears in Outliner
		self.polygons = list()  # All polygons in this mesh
		self.uv_layers = dict() # This mesh's UVW map. NOTE: Blender can have
		                        # several of these, but we only support one.
		self.vertices = list()  # All vertices in this mesh

# FIXME MeshVertex (change name?)
class Vertex:
	def __init__(self):
		self.co = Vector()     # The XYZ position of this vertex
		self.normal = Vector() # The XYZ normal of this vertex

class MeshUVLoopLayer:
	def __init__(self):
		self.data = list() # The list of UVLoops in this UV layer
		self.name = None   # The name of this UV layer

class MeshUVLoop:
	def __init__(self):
		self.uv = Vector() # The UV coordinate for this UV Loop

class Edge:
	def __init__(self):
		self.use_sharp_edge = False
		self.vertices = list()

class Polygon:
	def __init__(self):
		self.normal = Vector()
		self.vertices = list()

class Material:
	def __init__(self):
		self.diffuse_color = (1, 1, 1, 1) # Color in RGBA
		self.name = None                  # Name as it appears in Outliner


is_mock = True # Allows tests to verify they're using the mocks
data = Data()

_name_cache = {}


def clear_mock():
	data.collections.clear()
	data.materials.clear()
	data.meshes.clear()
	data.objects.clear()

	_name_cache.clear()

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

def _load_mesh(testdata):
	meshfile = testdata.get('mesh')
	if meshfile:
		dae = Collada(meshfile)
		geom = dae.geometries[0] # Assuming there's only one for now

		mesh = Mesh()
		meshname = testdata.get('meshname', _unique_name(geom.name))
		mesh.name = meshname

		# Collada separates the faces for each material into their own
		# primatives. Pycollada duplicates vertices shared by each primative, so
		# we need to create a map of vertex indices to vertex values to find the
		# duplicates.
		vertex_map = {}
		prim = geom.primitives[0]

		# Collada vertex position order matches Blender
		for v in prim.vertex:
			vert = Vertex()
			vert.co = Vector((v[0], v[1], v[2]))
			mesh.vertices.append(vert)

		# Collada vertex normal order DOES NOT match Blender, however,
		# the vertex_index and normal_index lists both refer to the same
		# vertices in the same order. We can use that fact to figure out which
		# normals belong to which vertex.
		#
		# Example: normal 4 maps to vertex 2, 1->3, 2->1, etc...
		#   vertex_index: [2, 3, 1, 4, 0]
		#   normal_index: [4, 1, 2, 0, 3]
		normal_vertex_map = {}
		for x in range(len(prim.normal_index)):
			normal_vertex_map[prim.normal_index[x]] = prim.vertex_index[x]

		for idx, n in enumerate(prim.normal):
			vert = mesh.vertices[normal_vertex_map[idx]]
			vert.normal = Vector((n[0], n[1], n[2]))

		# Texture coordinate order fortunately does match Blender
		uvlayer = MeshUVLoopLayer()
		uvlayer.name = 'Test'
		uvlayer.data = []
		for t in prim.texcoordset[0]:
			tex = MeshUVLoop()
			tex.uv = Vector((t[0], t[1]))
			uvlayer.data.append(tex)

		# Blender supports multiple UV layers but we're only supporting one.
		mesh.uv_layers['Test'] = uvlayer

		# Load in materials
		for m in dae.materials:
			mat = Material()
			mat.name = m.name
			dif = m.effect.diffuse
			mat.diffuse_color = (dif[0], dif[1], dif[2], dif[3])

			data.materials[m.name] = mat
			# TODO we're assuming every material belongs to this mesh.
			# That's not right but it'll do for now.
			mesh.materials[m.name] = mat

		# TODO face material assignments

		data.meshes[meshname] = mesh
		return mesh

def _unique_name(name):
	'''Uses a global cache to create a unique version of the given name'''
	global _name_cache
	new_name = name
	try:
		count = _name_cache[name]
		new_name += '.' + str(count)
		_name_cache[name] = count + 1
	except KeyError:
		_name_cache[name] = 1
	return new_name
