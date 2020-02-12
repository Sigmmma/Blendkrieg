from pocha import *
from hamcrest import *
from mathutils import Euler, Quaternion, Vector

import bpy
# Put this assert outside of the Pocha stuff so we exception out before we even
# try to run tests, unless we're using the mocks.
assert_that(bpy.is_mock, equal_to(True))

@describe('Blender mock tests')
def blenderMockTests():

	@beforeEach
	def verifyEmpty():
		bpy.clear_mock()
		assert_that(bpy.data.objects, empty())
		assert_that(bpy.data.collections, empty())

	@it('Setting and retrieving single object')
	def singleObjectSet():
		bpy.set_scene_data({
			'MyObject': {}
		})

		my_obj = bpy.data.objects.get('MyObject')
		assert_that(my_obj, not_none(), 'Object is added')
		assert_that(my_obj.name, equal_to('MyObject'), 'Object name is set')

	@it('Setting an object with children')
	def objectWithChildrenSet():
		bpy.set_scene_data({
			'Parent': {
				'children': {
					'child1': {},
					'child2': {}
				}
			}
		})

		parent = bpy.data.objects.get('Parent')

		for i in range(1, 3):
			name = 'child' + str(i)
			child = bpy.data.objects.get(name)

			assert_that(parent.children, has_item(child), 'Parent has child')
			assert_that(child, not_none(), 'Child is added')
			assert_that(child.name, equal_to(name), 'Child name is set')
			assert_that(child.parent, all_of(
					not_none(),
					equal_to(parent)
				),
				'Child has correct parent')

	@it('Collections created and populated by name')
	def collectionsCreatedByName():
		bpy.set_scene_data({
			'obj1': {
				'collections': ['coll1']
			},
			'obj2': {
				'collections': ['coll1']
			},
		})

		coll = bpy.data.collections.get('coll1')
		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		assert_that(coll, not_none(), 'Collection is added')
		assert_that(coll.name, equal_to('coll1'), 'Collection has correct name')
		assert_that(coll.objects, has_entries(
				'obj1', obj1,
				'obj2', obj2
			),
			'Collection contains both objects')

		assert_that(obj1.users_collection, has_item(coll), 'obj1 has the collection')
		assert_that(obj2.users_collection, has_item(coll), 'obj2 has the collection')

	@it('All children added to parent\'s collection')
	def childrenAddedToParentsCollection():
		bpy.set_scene_data({
			'Parent': {
				'collections': ['coll'],
				'children': {
					'child1': {},
					'child2': {}
				}
			}
		})

		parent = bpy.data.objects.get('Parent')
		child1 = bpy.data.objects.get('child1')
		child2 = bpy.data.objects.get('child2')
		coll = bpy.data.collections.get('coll')

		assert_that(coll.objects, has_entries(
				'child1', child1,
				'child2', child2
			),
			'Both children added to parent\'s collection')

		assert_that(child1.users_collection, has_items(coll), 'Child1 has collection')
		assert_that(child2.users_collection, has_item(coll), 'Child2 has collection')

	@it('Collections can have nested sub-collections')
	def nestedCollections():
		bpy.set_scene_data({
			'Parent': {
				'collections': ['coll1'],
				'children': {
					'child1': {
						'collections': ['coll2']
					},
					'child2': {
						'collections': ['coll3', 'coll4']
					}
				}
			}
		})

		parent = bpy.data.objects.get('Parent')
		child1 = bpy.data.objects.get('child1')
		child2 = bpy.data.objects.get('child2')
		coll1 = bpy.data.collections.get('coll1')
		coll2 = bpy.data.collections.get('coll2')
		coll3 = bpy.data.collections.get('coll3')
		coll4 = bpy.data.collections.get('coll4')

		assert_that(coll2, not_none(), 'Child collection coll2 created')
		assert_that(coll3, not_none(), 'Child collection coll3 created')
		assert_that(coll4, not_none(), 'Child collection coll4 created')

		assert_that(coll1.children, all_of(
			has_length(3),
			has_entries(
				'coll2', coll2,
				'coll3', coll3,
				'coll4', coll4)
			),
			'Parent collection contains nested child collections')

		assert_that(coll2.children, empty(), 'Child collection coll2 has no children')
		assert_that(coll2.objects, all_of(
				has_length(1),
				has_entry('child1', child1)
			),
			'coll2 contains only its child')

		assert_that(coll3.children, empty(), 'Child collection coll3 has no children')
		assert_that(coll3.objects, all_of(
				has_length(1),
				has_entry('child2', child2)
			),
			'Child collection coll3 has child object child2')

		assert_that(coll4.children, empty(), 'Child collection coll4 has no children')
		assert_that(coll4.objects, all_of(
				has_length(1),
				has_entry('child2', child2)
			),
			'Child collection coll4 has child object child2')

		assert_that(child1.users_collection, all_of(
				has_length(2),
				has_items(coll1, coll2),
			),
			'Child1 has its and its parent\'s collections')
		assert_that(child2.users_collection, all_of(
				has_length(3),
				has_items(coll1, coll3, coll4),
			),
			'Child2 has its parent\'s collection')

	@it('Getting object location')
	def objectLocationGet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {
				'location': (1, 2, 3)
			}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		assert_that(obj1.location,
			equal_to(Vector((0, 0, 0))),
			'Object location defaults to (0, 0, 0)')

		assert_that(obj2.location,
			equal_to(Vector((1, 2, 3))),
			'Object location Vector is set')

		assert_that(obj2.location.x, equal_to(1), 'X component addressable')
		assert_that(obj2.location.y, equal_to(2), 'Y component addressable')
		assert_that(obj2.location.z, equal_to(3), 'Z component addressable')

	@it('Setting object location')
	def objectLocationSet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		obj1.location = Vector((1, 2, 3))
		obj2.location.x = 4
		obj2.location.y = 5
		obj2.location.z = 6

		assert_that(obj1.location,
			equal_to(Vector((1, 2, 3))),
			'Object location set by Vector')

		assert_that(obj2.location,
			equal_to(Vector((4, 5, 6))),
			'Object location set by components')

	@it('Getting object rotation (euler)')
	def objectRotationEulerGet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {
				'rotation': Euler((1, 2, 3))
			}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		assert_that(obj1.rotation_euler,
			equal_to(Euler((0, 0, 0))),
			'Object rotation defaults to (0, 0, 0)')

		assert_that(obj1.rotation_mode,
			equal_to('XYZ'),
			'Object rotation defaults to XYZ')

		rot = obj2.rotation_euler
		assert_that(rot, equal_to(Euler((1, 2, 3))), 'Object rotation is set')
		assert_that(rot.x, equal_to(1), 'X component addressable')
		assert_that(rot.y, equal_to(2), 'Y component addressable')
		assert_that(rot.z, equal_to(3), 'Z component addressable')

	@it('Setting object rotation (euler)')
	def objectRotationEulerSet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		obj1.rotation_euler = Euler((1, 2, 3))
		obj2.rotation_euler.x = 1
		obj2.rotation_euler.y = 2
		obj2.rotation_euler.z = 3

		assert_that(obj1.rotation_euler,
			equal_to(Euler((1, 2, 3))),
			'Object rotation set by Euler')

		assert_that(obj2.rotation_euler,
			equal_to(Euler((1, 2, 3))),
			'Object rotation set by components')

	# TODO the standalone mathutils we're using (v2.81.2) doesn't support
	# setting the coordinate order for Euler rotation. When that support is
	# added, we'll want to add another test here for changing rotation mode to
	# 'ZYX' and making sure the coordinates are re-ordered.

	@it('Getting object rotation (quaternion')
	def objectRotationQuaternionGet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {
				'rotation': Quaternion((1, 2, 3, 4))
			}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		assert_that(obj1.rotation_quaternion,
			equal_to(Quaternion((1, 0, 0, 0))),
			'Object rotation defaults to (1, 0, 0, 0)')

		assert_that(obj1.rotation_mode,
			equal_to('XYZ'),
			'Rotation mode defaults to XYZ')

		assert_that(obj2.rotation_mode,
			equal_to('QUATERNION'),
			'Rotation mode changes to QUATERNION for Quaternions')

		rot = obj2.rotation_quaternion
		assert_that(rot, equal_to(Quaternion((1, 2, 3, 4))), 'Object rotation is set')
		assert_that(rot.w, equal_to(1), 'W component addressable')
		assert_that(rot.x, equal_to(2), 'X component addressable')
		assert_that(rot.y, equal_to(3), 'Y component addressable')
		assert_that(rot.z, equal_to(4), 'Z component addressable')

	@it('Setting object rotation (quaternion)')
	def objectRotationQuaterionSet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		obj1.rotation_quaternion = Quaternion((1, 2, 3, 4))
		obj2.rotation_quaternion.w = 1
		obj2.rotation_quaternion.x = 2
		obj2.rotation_quaternion.y = 3
		obj2.rotation_quaternion.z = 4

		assert_that(obj1.rotation_quaternion,
			equal_to(Quaternion((1, 2, 3, 4))),
			'Object rotation set by Quaternion')

		assert_that(obj2.rotation_quaternion,
			equal_to(Quaternion((1, 2, 3, 4))),
			'Object rotation set by components')

	@it('Getting object scale')
	def objectScaleGet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {
				'scale': (1, 2, 3)
			}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		assert_that(obj1.scale,
			equal_to(Vector()),
			'Object scale defaults to (1, 1, 1)')

		assert_that(obj2.scale.x, equal_to(1), 'X component addressable')
		assert_that(obj2.scale.y, equal_to(2), 'Y component addressable')
		assert_that(obj2.scale.z, equal_to(3), 'Z component addressable')

	@it('Setting object scale')
	def objectScaleSet():
		bpy.set_scene_data({
			'obj1': {},
			'obj2': {}
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')

		obj1.scale = Vector((1, 2, 3))
		obj2.scale.x = 1
		obj2.scale.y = 2
		obj2.scale.z = 3

		assert_that(obj1.scale,
			equal_to(Vector((1, 2, 3))),
			'Object scale set by Vector')

		assert_that(obj2.scale,
			equal_to(Vector((1, 2, 3))),
			'Object scale set by components')

	@it('Loading mesh from .obj file')
	def meshFromObj():
		bpy.set_scene_data({
			'obj': {
				'mesh': 'pyramid.obj',
				'meshname': 'testmesh'
			}
		})

		obj = bpy.data.objects.get('obj')
		mesh = bpy.data.meshes.get('testmesh')

		assert_that(obj.to_mesh(), equal_to(mesh), 'Mesh set on object')
		assert_that(mesh.name, equal_to('testmesh'), 'Mesh name is set')

	@it('Mesh names have unique defaults')
	def meshUniqueDefaultNames():
		bpy.set_scene_data({
			'obj1': { 'mesh': 'pyramid.obj' },
			'obj2': { 'mesh': 'pyramid.obj' },
			'obj3': { 'mesh': 'pyramid.obj' }
		})

		obj1 = bpy.data.objects.get('obj1')
		obj2 = bpy.data.objects.get('obj2')
		obj3 = bpy.data.objects.get('obj3')

		assert_that(obj1.to_mesh().name, equal_to('mesh'), 'Default name 1')
		assert_that(obj2.to_mesh().name, equal_to('mesh.1'), 'Default name 2')
		assert_that(obj3.to_mesh().name, equal_to('mesh.2'), 'Default name 3')

	@it('Loading vertices from .obj file')
	def meshVertices():
		bpy.set_scene_data({
			'obj': { 'mesh': 'pyramid.obj' }
		})

		mesh = bpy.data.objects.get('obj').to_mesh()
		verts = mesh.vertices

		assert_that(verts[0].co, equal_to(Vector((-1, 0,  1))), 'Vertex 0')
		assert_that(verts[1].co, equal_to(Vector(( 1, 0,  1))), 'Vertex 1')
		assert_that(verts[2].co, equal_to(Vector((-1, 0, -1))), 'Vertex 2')
		assert_that(verts[3].co, equal_to(Vector(( 1, 0, -1))), 'Vertex 3')
		assert_that(verts[4].co, equal_to(Vector(( 0, 1,  0))), 'Vertex 4')

