from __future__ import annotations

import numpy as np


def convert_coords(coords: np.ndarray) -> np.ndarray:
    """Converts (x,y,zx) coordinates into (r,z)

    Parameters
    ----------
    coords
        numpy array of coordinates where the second index corresponds to (x,y,z) respectively

    Returns
    -------
        numpy array of (r,z) coordinates for each point

    """
    r = np.sqrt(np.power(coords[:, 0], 2) + np.power(coords[:, 1], 2))
    return np.column_stack((r, coords[:, 2]))


def distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Computes the distance between a set of vectors a and b

    Parameters
    ----------
    a
        First list of vectors, where the second index corresponds to the dimension.
    b
        Second list in the same format.

    Returns
    -------
        the distance for each vector
    """
    return np.sqrt(np.sum(np.power(a - b, 2), axis=1))


def norm(a: np.ndarray) -> np.ndarray:
    """Computes the norm of a set of vectors or a single vector

    Parameters
    ----------
    a
        First list of vectors, or a single vector.

    Returns
    -------
        the length for each vector.
    """
    ax = 1 if a.ndim == 2 else 0

    return np.sqrt(np.sum(np.power(a, 2), axis=ax))


def dot(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Computes the dot product of a set of vectors

    Parameters
    ----------
    a
        First list of vectors, where the second index corresponds to the dimension.

    b
        Second list in the same format.


    Returns
    -------
        the dot product for each vector.
    """

    return np.sum(a * b, axis=1)


def shortest_distance_to_plane(
    a_vec: np.array,
    d: float,
    points: np.ndarray,
    rmax: float | None = None,
    zrange: tuple[float, float] | None = None,
) -> np.ndarray:
    """Get the shortest distance from a plane (constrained in r and z) to each point.

    The equation of the plane is given by :math:`a_1x+a_2y+a_3z=d`. Where :math:`\\vec{a}=(a_1,a_2,a_3)` The closest point on the plane to the point
    (:math:`y`) is then given by:

    .. math::
        x =y-(y*a-d)*a/||a||^2

    The distance is then given by the length of the vector :math:`x-y`. This function also checks if the
    intersection point is above rmax or inside the zrange,  if not nan is returned for that point.

    Parameters
    ----------
    a_vec
        3 coordinate array defining the plane.
    d
        scalar in the plane definition.
    points
        set of points to compute distance.
    rmax
        maximum radius for the plane.
    zrange
        range in z for the plane.

    Returns
    -------
    np.array of distance for each point.
    """

    a_norm = np.sum(a_vec * a_vec)
    proj_points = points - ((dot(points, a_vec) - d)[:, np.newaxis]) * a_vec / a_norm

    dist_vec = norm((dot(points, a_vec) - d)[:, np.newaxis] * a_vec / a_norm)

    # check on r and z

    proj_points_rz = convert_coords(proj_points)

    if rmax is not None:
        condition_r = proj_points_rz[:, 0] <= rmax
    else:
        condition_r = np.full(len(points), True)

    if zrange is not None:
        condition_z = (proj_points_rz[:, 1] > zrange[0]) & (
            proj_points_rz[:, 1] < zrange[1]
        )
    else:
        condition_z = np.full(len(points), True)

    condition = condition_r * condition_z
    return np.where(condition, dist_vec, np.full(len(points), np.nan))


def shortest_distance(s1: np.ndarray, s2: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Get the shortest distance between each point and the line segment defined by s1-s2.

    Based on vector algebra where the distance vector is given by:

    .. math::
        d = s_1 - p - ( (n · (s_1- p)) * n )

    where:
        - :math:`s_1` is a vector from which the distance is measured,
        - `p` is a point vector,
        - `n` is a unit direction vector from :math:`s_1` to :math:`s_2`,
        - `a` is another point vector.

    If the projection point lies inside the segment s1-s2. Else the closest point is either :math:`s_1` or :math:`s_2`.
    The distance is the modulus of this vector and this calculation is performed for each point.

    Parameters
    ----------
    s1
        first point in the line segment, 1D array where index 0 correspond to r and 1 to z.
    s2
        second point, same format as s1.
    points
        array of points to compare, first index corresponds to the point and the second to r,z.

    Returns
    -------
        numpy array of the shortest distances
    """

    n = (s2 - s1) / norm(s2 - s1)
    proj_dist = -dot(n, (n * dot(s1 - points, n)[:, np.newaxis]))
    dist_vec = np.empty_like(s1 - points)
    condition1 = proj_dist < 0
    condition2 = proj_dist > norm(s2 - s1)
    condition3 = (~condition1) & (~condition2)

    dist_vec[condition1] = (s1 - points)[condition1]
    dist_vec[condition2] = (points - s2)[condition2]
    dist_vec[condition3] = ((s1 - points) - n * dot(s1 - points, n)[:, np.newaxis])[
        condition3
    ]

    # TODO make this signed so inside is positive and outside negative
    return norm(dist_vec)
