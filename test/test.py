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
	blender = args.blender                \
		or os.environ.get('BLENDER_PATH') \
		or which('blender')

	if blender is None:
		raise Exception('Cannot find Blender executable')

	# Build a path to our test running script that Blender will run
	cur_dir = Path(__file__).resolve().parent
	run_pocha = cur_dir.joinpath('run-pocha.py')

	# Peel back directories until we find the project root
	while not cur_dir.samefile(cur_dir.root)   \
	  and not cur_dir.joinpath('.git').exists():
		cur_dir = cur_dir.parent

	# Run Blender with the project root as the working directory so this script
	# will work when run from anywhere.
	subprocess.run(
		[blender, '--background', '--python', str(run_pocha)],
		cwd=str(cur_dir)
	)
