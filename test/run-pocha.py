'''This is a hack so we can run Pocha through Blender Python.'''
import pocha
import sys

# Remove the arguments from argv. If we don't then Pocha will get upset at
# the args we've just given Blender.
sys.argv = sys.argv[ :1]

# Run the entrypoint of pocha!
pocha.cli.cli()
