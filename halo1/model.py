import bpy

from reclaimer.hek.defs.mode import mode_def
from reclaimer.hek.defs.mod2 import mod2_def
from reclaimer.model.jms import read_jms
from reclaimer.model.model_decompilation import extract_model
from mozzarilla.windows.tag_converters.model_converter import convert_model

def read_halo1model(filepath):
	'''Takes a halo1 model file and turns it into a jms class.'''

	if filepath.endswith('.gbxmodel'):
		# Load Gbxmodel
		mod2 = mod2_def.build(filepath=filepath)
		#TODO: Get all lod permutations.
		jms = extract_model(mod2)[0] #Only getting the superhigh perms for now

		return jms

	if filepath.endswith('.model'):
		# Load Xbox model
		mode = mode_def.build(filepath=filepath)
		# Convert the Xbox model to a Gbxmodel
		mod2 = mod2_def.build()
		convert_model(mod2, mode, True) #True means: convert to mod2
		#TODO: Get all lod permutations.
		jms = extract_model(mod2)[0] #Only getting the superhigh perms for now

		return jms

	if filepath.endswith('.jms'):
		# Read jms file into string.
		jms_string = ""
		with open(filepath, 'r') as jms_file:
			jms_string = jms_file.read()
		# Read Jms data from string.
		jms = read_jms(jms_string)
		# Make sure it's a Halo 1 jms
		assert(jms.version == "8200")

		return jms
