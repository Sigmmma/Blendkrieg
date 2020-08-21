import bpy
from mathutils import Vector, Quaternion, Matrix, Euler
from math import pi, radians

from reclaimer.hek.defs.antr import antr_def
from reclaimer.animation.animation_decompilation import extract_model_animations

def read_halo1anim(filepath):
    ''' Takes a halo1 model_animations file and turns them into blender actions'''
    tag = antr_def.build(filepath=filepath)

    data = extract_model_animations(tag.data.tagdata,"",write_jma=False)
    return data


def import_animations(animations,scale = 0.03048):
    scene = bpy.context.scene
    target = bpy.context.object
    # just random lazy inspection stuff
    bpy.debug_anim = animations
    if target.type != "ARMATURE":
        raise "Not an armature"
    
    if not target.animation_data:
        target.animation_data_create()
    bpy.ops.object.mode_set(mode="POSE")
    
    
    for anim in [animations[0]]:
        action = bpy.data.actions.new(anim.name)
        target.animation_data.action = action
        action.use_fake_user = True
        scene.frame_start = 0
        scene.frame_end = len(anim.frames) - 1
        
        # this is recursively called for each node
        def ApplyKeyframes(bone):
            n = anim.get_node_index(bone.name[1:])
            keys = [ frame[n] for frame in anim.frames ]
            bone_string = "pose.bones[\"{}\"].".format(bone.name)
            
            group = action.groups.new(name=bone.name)
            curvesLoc = []
            curvesRot = []
            for l in range(3):
                curve = action.fcurves.new(data_path= bone_string + "location", index=l)
                curve.group = group
                curvesLoc.append(curve)
            for r in range(4):
                curve = action.fcurves.new(data_path= bone_string + "rotation_quaternion", index=r)
                curve.group = group
                curvesRot.append(curve)
            
            for f,frame in enumerate(keys):
                print(f,frame)
                translation = Vector((
                    frame.pos_x, frame.pos_y, frame.pos_z
                )) * scale
                rotation = Quaternion((
                    frame.rot_w, frame.rot_i, frame.rot_j, frame.rot_k
                )).normalized().inverted()

                matrix = Matrix.Translation(translation) @ rotation.to_matrix().to_4x4()

                if not bone.parent:
                    bone.matrix = matrix
                else:
                    bone.matrix = bone.parent.matrix @ matrix
                for i in range(3):
                    curvesLoc[i].keyframe_points.add(1)
                    curvesLoc[i].keyframe_points[-1].co = [f,bone.location[i]]
                for i in range(4):
                    curvesRot[i].keyframe_points.add(1)
                    curvesRot[i].keyframe_points[-1].co = [f,bone.rotation_quaternion[i]]
            for child in bone.children:
                ApplyKeyframes(child)
        #Start keying
        for bone in target.pose.bones:
            if not bone.parent:
                ApplyKeyframes(bone)
        for fc in action.fcurves:
            fc.update()
    for bone in target.pose.bones:
        bone.location.zero()
        bone.rotation_quaternion.identity()
    scene.frame_set(0)
    bpy.ops.object.mode_set(mode="OBJECT")