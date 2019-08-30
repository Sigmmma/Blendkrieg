import bpy

import os

# TODO: Figure out why I can't import these without ..lib.
from ..lib.reclaimer.hek.defs.mode import mode_def
from ..lib.reclaimer.hek.defs.mod2 import mod2_def
from ..lib.reclaimer.model.jms import read_jms
from ..lib.reclaimer.model.model_decompilation import extract_model

from ..scene.shapes import create_sphere

def read_halo1model(filepath):
	'''Takes a halo1 model file and turns it into a jms class.'''

	# Workaround for reclaimer's brokenness on Linux
	filepath = os.path.realpath(filepath)

	if filepath.endswith('.gbxmodel'):
		# Load Gbxmodel
		mod2 = mod2_def.build(filepath=filepath)
		#TODO: Get all lod permutations.
		#Only getting the superhigh perms for now
		jms = extract_model(mod2.data.tagdata, write_jms=False)[0]
		return jms

	if filepath.endswith('.model'):
		# Load Xbox model
		mode = mode_def.build(filepath=filepath)
		# Convert the Xbox model to a Gbxmodel
		mod2 = mod2_def.build()
		convert_model(mod2, mode, True) #True means: convert to mod2
		#TODO: Get all lod permutations.
		#Only getting the superhigh perms for now
		jms = extract_model(mod2.data.tagdata, write_jms=False)[0]

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

def import_halo1_nodes(jms):
	'''
	Import all the nodes from a jms into the scene and returns a list of them.
	'''
	scene_nodes = []
	for node in jms.nodes:
		scene_node = create_sphere(name=node.name, size=0.02)

		# Assign parent if index is valid.
		if node.parent_index >= 0:
			scene_node.parent = scene_nodes[node.parent_index]

		# TODO: Get proper position and rotation using Keanu Reeves math
		# Set the translations
		scene_node.rotation_mode = 'QUATERNION'
		scene_node.rotation_quaternion = (
			node.rot_w, node.rot_i, node.rot_j, node.rot_k
		)
		# Undo 100x scaling from jms files.
		scene_node.location = (node.pos_x/100, node.pos_y/100, node.pos_z/100)



		scene_nodes.append(scene_node)

	return scene_nodes


# The next is copied from mozzarilla.windows.tag_converters.model_converter
# Too many references to libraries that aren't even used by the function
# that we're importing.
# It relied on threadsafe_tkinter, which relies on tkinter,
# which relies on who knows what.

# Just ignore this whole part for now

from reclaimer.hek.defs.mod2    import fast_mod2_def
from reclaimer.stubbs.defs.mode import fast_mode_def

def convert_model(src_tag, dst_tag, to_gbxmodel):
	src_tag_data = src_tag.data.tagdata
	dst_tag_data = dst_tag.data.tagdata

	# move the first 14 header fields from src tag into dst tag
	# (except for the flags since usually ZONER shouldnt be copied)
	dst_tag_data[1: 14] = src_tag_data[1: 14]
	for flag_name in src_tag_data.flags.NAME_MAP:
		if hasattr(dst_tag_data.flags, flag_name):
			dst_tag_data.flags[flag_name] = src_tag_data.flags[flag_name]

	# fix the fact the mode and mod2 store stuff related to lods
	# in reverse on most platforms(pc stubbs is an exception)
	if dst_tag_data.superhigh_lod_cutoff < dst_tag_data.superlow_lod_cutoff:
		tmp0 = dst_tag_data.superhigh_lod_cutoff
		tmp1 = dst_tag_data.high_lod_cutoff
		dst_tag_data.superhigh_lod_cutoff = dst_tag_data.superlow_lod_cutoff
		dst_tag_data.high_lod_cutoff      = dst_tag_data.low_lod_cutoff
		dst_tag_data.low_lod_cutoff       = tmp1
		dst_tag_data.superlow_lod_cutoff  = tmp0

		tmp0 = dst_tag_data.superhigh_lod_nodes
		tmp1 = dst_tag_data.high_lod_nodes
		dst_tag_data.superhigh_lod_nodes = dst_tag_data.superlow_lod_nodes
		dst_tag_data.high_lod_nodes      = dst_tag_data.low_lod_nodes
		dst_tag_data.low_lod_nodes       = tmp1
		dst_tag_data.superlow_lod_nodes  = tmp0

	# make all markers global ones
	if hasattr(src_tag, "globalize_local_markers"):
		src_tag.globalize_local_markers()

	# move the markers, nodes, regions, and shaders, from mode into mod2
	dst_tag_data.markers = src_tag_data.markers
	dst_tag_data.nodes = src_tag_data.nodes
	dst_tag_data.regions = src_tag_data.regions
	dst_tag_data.shaders = src_tag_data.shaders

	# give the mod2 as many geometries as the mode
	src_tag_geoms = src_tag_data.geometries.STEPTREE
	dst_tag_geoms = dst_tag_data.geometries.STEPTREE
	dst_tag_geoms.extend(len(src_tag_geoms))

	# copy the data from the src_tag_geoms into the dst_tag_geoms
	for i in range(len(dst_tag_geoms)):
		# give the dst_tag_geom as many parts as the src_tag_geom
		src_tag_parts = src_tag_geoms[i].parts.STEPTREE
		dst_tag_parts = dst_tag_geoms[i].parts.STEPTREE
		dst_tag_parts.extend(len(src_tag_parts))

		# copy the data from the src_tag_parts into the dst_tag_parts
		for j in range(len(dst_tag_parts)):
			src_tag_part = src_tag_parts[j]
			dst_tag_part = dst_tag_parts[j]

			# move the first 9 part fields from src_tag into dst_tag
			# (except for the flags since usually ZONER shouldnt be copied)
			dst_tag_part[1: 9] = src_tag_part[1: 9]

			src_local_nodes = getattr(src_tag_part, "local_nodes", None)
			dst_local_nodes = getattr(dst_tag_part, "local_nodes", None)
			if not getattr(src_tag_part.flags, "ZONER", False):
				src_local_nodes = None

			if dst_local_nodes and src_local_nodes:
				# converting from a gbxmodel with local nodes to a gbxmodel
				# with local nodes. copy the local nodes and node count
				dst_tag_part.flags.ZONER = True
				dst_tag_part.local_node_count = src_tag_part.local_node_count
				dst_tag_part.local_nodes[:] = src_local_nodes[:]
			elif src_local_nodes:
				# converting from a gbxmodel with local nodes to
				# something without them. make the nodes absolute.
				src_tag.delocalize_part_nodes(i, j)

			# move the vertices and triangles from the src_tag into the dst_tag
			dst_tag_part.triangles = src_tag_part.triangles
			dst_tag_part.uncompressed_vertices = src_tag_part.uncompressed_vertices
			dst_tag_part.compressed_vertices   = src_tag_part.compressed_vertices

			uncomp_verts = dst_tag_part.uncompressed_vertices
			comp_verts   = dst_tag_part.compressed_vertices

			if to_gbxmodel:
				# if the compressed vertices are valid or
				# the uncompressed are not then we don't have
				# any conversion to do(already uncompressed)
				if not uncomp_verts.size or comp_verts.size:
					dst_tag.decompress_part_verts(i, j)
			elif not comp_verts.size or uncomp_verts.size:
				# the uncompressed vertices are valid or
				# the compressed are not, so we don't have
				# any conversion to do(already compressed)
				dst_tag.compress_part_verts(i, j)

	dst_tag.calc_internal_data()
