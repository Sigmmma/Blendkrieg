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
		assert_that(my_obj, not_none())
		assert_that(my_obj.name, equal_to('MyObject'))

#	@it('Objects can have children')
#	@it('Child objects have parent set')
#	@it('Collections created by name')
#	@it('All children added to collection')
#	@it('Object can belong to multiple collections')
