import bpy
import bmesh

def create_sphere(name="new_sphere", size=1):
    '''
    Creates a sphere with the given size.
    '''
    scene = bpy.context.collection

    mesh = bpy.data.meshes.new(name)
    sphere = bpy.data.objects.new(name, mesh)

    scene.objects.link(sphere)

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm,
        u_segments=16, v_segments=16,
        diameter=size
    )
    bm.to_mesh(mesh)
    bm.free()

    return sphere

def create_cone(name="new_cone", base_size=1, height=3):
    '''
    Creates a cone with the given sizes.
    '''
    scene = bpy.context.collection

    mesh = bpy.data.meshes.new(name)
    cone = bpy.data.objects.new(name, mesh)

    scene.objects.link(cone)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm,
        segments=16,
        diameter1=base_size, diameter2=base_size,
        depth=height
    )
    bm.to_mesh(mesh)
    bm.free()

    return cone
