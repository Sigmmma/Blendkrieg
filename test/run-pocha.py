'''
This is a hack so we can run Pocha through Blender Python.

This script adds the project root to Python's path. This makes it so you can
import Blendkrieg using `import Blendkrieg` within Blender's Python environment
without installing it to the addons directory.
'''
from pathlib import Path
import pocha
import sys

# Peel back directories until we find the project root.
location = Path(__file__).resolve()
while not location.samefile(location.root)  \
  and not location.joinpath('.git').exists():
	location = location.parent

sys.path.insert(0, location.parent)

# Remove the arguments from argv. If we don't then Pocha will get upset at
# the args we've just given Blender.
sys.argv = sys.argv[ :1]

# Run the entrypoint of pocha!
pocha.cli.cli()
