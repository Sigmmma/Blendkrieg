#!/usr/bin/env python3
from argparse import ArgumentParser
import os
from pathlib import Path
from shutil import which
import subprocess
import sys

DESC = '''
	Runs all (or a subset of) the tests inside Blender.

	Blendkrieg depends on Blender's internal bpy module, and thus the tests do
	too. This script makes it a little easier to run our tests inside Blender.
	We assume this script and run-pocha.py are co-located in the test directory.
	'''

if __name__ == '__main__':
	parser = ArgumentParser(description=DESC)
	parser.add_argument('-b', '--blender', type=str, default=None, help='''
		Path to Blender executable. This can also be specified by setting the
		environment variable BLENDER_PATH. If not specified, this script will
		search for a blender executable on the system.
	''')
	args = parser.parse_args()

	# Support reading Blender location in multiple ways
	if args.blender:
		blender = args.blender
	elif os.environ.get('BLENDER_PATH'):
		blender = os.environ.get('BLENDER_PATH')
	else:
		blender = which('blender')

	if blender is None:
		raise Exception('Cannot find Blender executable')

	run_pocha = Path(__file__).resolve().parent.joinpath('run-pocha.py')

	subprocess.run([blender, '--background', '--python', str(run_pocha)],
		cwd=str(run_pocha.parent.parent))
