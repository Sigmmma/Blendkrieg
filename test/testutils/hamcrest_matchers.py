from math import fabs

from bpy_types import Mesh
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.library.number.iscloseto import isnumeric
from mathutils import Vector # From Blender's API

# Blender Vectors seem to only care about precision out to 8 digits
DEFAULT_VECTOR_DELTA = 1e-8

class VectorCloseTo(BaseMatcher):
	'''Lets us match Blender Vectors without caring about full precision.'''

	def __init__(self, vector, delta):
		if not isinstance(vector, Vector):
			raise TypeError('VectorCloseTo vector must be a ' + str(Vector))
		if not isnumeric(delta):
			raise TypeError('VectorCloseTo delta must be a number')

		self.vector = vector
		self.delta = delta

	def _calc_diffs(self, item):
		diffs = []
		for i, value in enumerate(item):
			diff = fabs(value - self.vector[i])
			if diff >= self.delta:
				diffs.append([i, diff])
		return diffs

	def _matches(self, item):
		if not isinstance(item, Vector):
			return False

		return not self._calc_diffs(item)

	def describe_to(self, description):
		description \
			.append_text(Vector)                          \
			.append_text(' with all components within <') \
			.append_text(self.delta)                      \
			.append_text('> of ')                         \
			.append_text(repr(self.vector))

	def describe_mismatch(self, item, description):
		if not isinstance(item, Vector):
			super(VectorCloseTo, self).describe_mismatch(item, description)
		else:
			diffs = self._calc_diffs(item)
			description.append_text(repr(item)).append_text('\n')
			for index, diff in diffs:
				description \
					.append_text('\t<')             \
					.append_text(index)             \
					.append_text('> differed by <') \
					.append_text(diff)              \
					.append_text('>\n')


class MeshEquals(BaseMatcher):
	'''Lets us match Blender meshes.

	Currently this just matches the position and count of vertices.
	This could fairly easily be extended to match other things too, like UVs.
	'''
	def __init__(self, mesh):
		if not isinstance(mesh, Mesh):
			raise TypeError('MeshEquals mesh must be a ' + str(Mesh))

		self.mesh = mesh

	def _matches(self, item):
		if not isinstance(item, Mesh):
			return False

		if len(self.mesh.vertices) != len(item.vertices):
			return False

		# "co" compares vertex locations as Vectors
		for v1, v2 in zip(self.mesh.vertices, item.vertices):
			if v1.co != v2.co:
				return False

		return True

	def describe_to(self, description):
		description.append_text(self.mesh)

	def describe_mismatch(self, item, description):
		if not isinstance(item, Mesh):
			super(MeshEquals, self).describe_mismatch(item, description)
		else:
			# TODO Diffing two meshes in text is too big a problem to solve for
			# something this minor. If you're feeling really brave, go ahead.
			description.append_text('Mesh vertices did not match up')


def vector_close_to(vector, delta=DEFAULT_VECTOR_DELTA):
	return VectorCloseTo(vector, delta)

def mesh_equal_to(mesh):
	return MeshEquals(mesh)
