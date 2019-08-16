class HBase:
    '''
    The base of all the translation classes that
    handle conversion between Halo and Blender.
    '''
    id_keys = {
        "long": 'halo_object',
        "short": 'h',
    }


class HRegion(HBase):
    '''
    A section of a model that can be different
    depending on what permutation is selected.
    '''
    id_keys = {
        "long": 'region',
        "short": 'r',
    }


class HPermutation(HRegion):
    '''
    One version of a region.
    '''
    id_keys = {
        "long": 'permutation',
        "short": 'p',
    }


class HNode(HBase):
    '''
    An object that allows a mesh to be deformed,
    and markers to be moved around.
    '''
    id_keys = {
        "long": 'node',
        "short": 'n',
    }


class HMarker(HNode):
    '''
    A point that can be the origin of an effect
    or the point of interaction.
    '''
    id_keys = {
        "long": 'marker',
        "short": 'm',
    }


class HMesh(HBase):
    '''
    A set of surfaces that dictates how
    its part of the model looks.
    '''
    id_keys = {
        "long": 'mesh',
        "short": '',
    }
