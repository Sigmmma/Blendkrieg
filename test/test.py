#!env python3
'''
Runs all (or a subset of) the tests inside Blender.

Blendkrieg depends on Blender's internal bpy module, and thus the tests do too.
This script makes it a little easier to do that. We assume this script and
run-pocha.py are co-located in the test directory.
'''

from pathlib import Path
from shutil import which
import subprocess
import sys

if __name__ == '__main__':
	run_pocha = Path(__file__).resolve().parent.joinpath('run-pocha.py')

	# We could be more robust here and support providing Blender's path as an
	# argument, but FU.
	blender = which('blender')
	if blender is None:
		raise Exception('Cannot find blender')

	subprocess.run([blender, '--background', '--python', str(run_pocha)])
