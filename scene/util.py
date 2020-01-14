def apply_halo_rotation(scene_object, ijkw):
    '''
    Helper to apply a rotation from Halo to an object in the scene.
    '''
    # Store original rotation mode.
    rot_mode = scene_object.rotation_mode
    # Set rotation mode to quaternion and apply the rotation.
    scene_object.rotation_mode = 'QUATERNION'
    scene_object.rotation_quaternion = (
        -ijkw[3], ijkw[0], ijkw[1], ijkw[2]
    )
    # Set rotation mode back.
    scene_object.rotation_mode = rot_mode
