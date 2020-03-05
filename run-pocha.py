# This is a hack so we can run Pocha through Blender Python.

# Remove the arguments from argv. If we don't then Pocha will get upset at
# the args we've just given Blender.
import sys
sys.argv = sys.argv[ :1]
# Run the entrypoint of pocha!
import pocha
pocha.cli.cli()
