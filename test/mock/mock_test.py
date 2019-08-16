from pocha import *
from hamcrest import *

import bpy
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
			assert_that(child.parent, not_none(), 'Child has parent set')
			assert_that(child.parent, equal_to(parent), 'Child has correct parent')

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
		assert_that(coll.objects, has_entry('obj1', obj1), 'Collection has obj1')
		assert_that(coll.objects, has_entry('obj2', obj2), 'Collection has obj2')

		assert_that(obj1.users_collection, has_item(coll), 'obj1 has the collection')
		assert_that(obj2.users_collection, has_item(coll), 'obj2 has the collection')

	@it('All children added to parent\'s collection')
	def childrenAddedToParentsCollection():
		bpy.set_scene_data({
			'Parent': {
				'collections': ['coll1'],
				'children': {
					'child1': {
						'collections': ['coll2']
					},
					'child2': {}
				}
			}
		})

		parent = bpy.data.objects.get('Parent')
		child1 = bpy.data.objects.get('child1')
		child2 = bpy.data.objects.get('child2')
		coll1 = bpy.data.collections.get('coll1')
		coll2 = bpy.data.collections.get('coll2')

		assert_that(coll1.objects, has_entries('child1', child1, 'child2', child2),
			'Both children added to parent\'s collection')

		assert_that(coll2, not_none(), 'Child1\'s collection was created')
		assert_that(coll2.name, equal_to('coll2'),
			'Child1\'s collection has correct name')
		assert_that(coll2.objects, has_entry('child1', child1),
			'Child1 belongs to its collection')
		assert_that(coll2.objects, not_(has_entry('child2', child2)),
			'Child2 not in Child1\'s collection')

		assert_that(child1.users_collection, has_items(coll1, coll2),
			'Child1 has its and its parent\'s collections')
		assert_that(child2.users_collection, has_item(coll1),
			'Child2 has its parent\'s collection')
		assert_that(child2.users_collection, not_(has_item(coll2)),
			'Child2 does not have Child1\'s collection')

#	@it('Collections can have nested sub-collections')

