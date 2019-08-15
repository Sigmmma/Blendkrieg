from pocha import *
from hamcrest import *

import bpy
assert_that(bpy.is_mock, equal_to(True))

@describe('Blender mock tests')
def blenderMockTests():

	@afterEach
	def cleanup():
		bpy.clear_mock()

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

#	@it('Collections created by name')
#	@it('All children added to collection')
#	@it('Object can belong to multiple collections')
