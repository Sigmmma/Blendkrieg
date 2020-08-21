bl_info = {
	"name": "Blendkrieg",
	"author": "gbMichelle & Mimickal",
	"version": (0, 0, 1),
	"blender": (2, 80, 0),
	"location": "Top-Bar > Krieg",
	"description": "Adds Halo importers, exporters, and Helper tools.",
	"warning": "",
	"wiki_url": "https://github.com/gbMichelle/Blendkrieg/wiki",
	"category": "Import-Export"
}

# Initialize the libraries module.
from . import lib

# Import all submodules.
from .menu import topbar_dropdown
from .menu.import_export import halo1_model
from .menu.import_export import halo1_anim

modules = [
	halo1_model,
	halo1_anim,
	topbar_dropdown,
]

def register():
	'''
	Registers classes on load by calling the
	register functions in their respective modules.
	'''
	for module in modules:
		module.register()

def unregister():
	'''
	Unregisters classes on unload by calling the
	unregister functions in their respective modules.
	'''
	#Unregister classes in reverse order to avoid any dependency problems.
	for module in reverse(modules):
		module.unregister()

if __name__ == "__main__":
	register()
