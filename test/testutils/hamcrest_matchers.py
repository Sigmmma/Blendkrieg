from math import fabs

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.library.number.iscloseto import isnumeric
from mathutils import Vector # From Blender's API

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


def vector_close_to(vector, delta):
	return VectorCloseTo(vector, delta)
