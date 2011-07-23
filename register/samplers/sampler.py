""" A collection of samplers"""

import numpy as np
import scipy.ndimage as nd

from numpy.ctypeslib import load_library
from numpyctypes import c_ndarray

libsampler = load_library('libsampler', __file__)

class Sampler(object):
    """
    Abstract sampler.

    @param METHOD: the method implemented by the sampler.
    @param DESCRIPTION: a meaningful description of the technique used, with
                        references where appropriate.
    """

    METHOD=None
    DESCRIPTION=None

    def __init__(self, coordinates):

        self.coordinates = coordinates

    def f(self, array, warp):
        """
        A sampling function, responsible for returning a sampled set of values
        from the given array.

        @param array: an n-dimensional array (representing an image or volume).
        @param coords: array coordinates in cartesian form (n by p).
        """

        if self.coordinates is None:
            raise ValueError('Appropriately defined coordinates not provided.')

        i = self.coordinates.tensor[0] + warp[0]
        j = self.coordinates.tensor[1] + warp[1]

        packedCoords = (i.reshape(1,i.size),
                        j.reshape(1,j.size))

        return self.sample(array, np.vstack(packedCoords))

    def sample(self, array, coords):
        """
        The sampling function - provided by the specialized samplers.
        """
        return None

    def __str__(self):
        return 'Method: {0} \n {1}'.format(
            self.METHOD,
            self.DESCRIPTION
            )


class Nearest(Sampler):

    METHOD='Nearest Neighbour (NN)'

    DESCRIPTION="""
        Given coordinate in the array nearest neighbour sampling simply rounds
        coordinates points:
            f(I; i,j) = I( round(i), round(j))
                """

    def __init__(self, coordinates):
        Sampler.__init__(self, coordinates)


    def f(self, array, warp):
        """
        A sampling function, responsible for returning a sampled set of values
        from the given array.

        @param array: an n-dimensional array (representing an image or volume).
        @param coords: array coordinates in cartesian form (n by p).
        """

        if self.coordinates is None:
            raise ValueError('Appropriately defined coordinates not provided.')

        result = np.zeros_like(array)

        arg0 = c_ndarray(warp, dtype=np.double, ndim=3)
        arg1 = c_ndarray(array, dtype=np.double, ndim=2)
        arg2 = c_ndarray(result, dtype=np.double, ndim=2)

        libsampler.nearest(arg0, arg1, arg2)

        return result.flatten()


class Spline(Sampler):

    METHOD='nd-image spline sampler (SR)'

    DESCRIPTION="""
        Refer to the documentation for the ndimage map_coordinates function.

        http://docs.scipy.org/doc/scipy/reference/generated/
            scipy.ndimage.interpolation.map_coordinates.html

                """

    def __init__(self, coordinates):
        Sampler.__init__(self, coordinates)

    def f(self, array, warp):
        """
        A sampling function, responsible for returning a sampled set of values
        from the given array.

        @param array: an n-dimensional array (representing an image or volume).
        @param coords: array coordinates in cartesian form (n by p).
        """

        if self.coordinates is None:
            raise ValueError('Appropriately defined coordinates not provided.')

        return nd.map_coordinates(
            array,
            warp,
            order=2,
            cval=0.0
            ).flatten()
