from __future__ import annotations

import numba
import numpy as np
from numpy.typing import ArrayLike, NDArray


@numba.njit(cache=True)
def convert_coords(coords: ArrayLike) -> NDArray:
    """Converts (x,y,z) coordinates into (r,z)

    Parameters
    ----------
    coords
        numpy array of coordinates where the second index corresponds to (x,y,z) respectively

    Returns
    -------
        numpy array of (r,z) coordinates for each point

    """
    r = np.sqrt(coords[:, 0] ** 2 + coords[:, 1] ** 2)
    return np.column_stack((r, coords[:, 2]))


def shortest_distance_to_plane(
    a_vec: NDArray,
    d: float,
    points: NDArray,
    rmax: float | None = None,
    zrange: tuple[float, float] | None = None,
) -> NDArray:
    """Get the shortest distance from a plane (constrained in r and z) to each point.

    The equation of the plane is given by :math:`a_1x+a_2y+a_3z=d`. Where
    :math:`\\vec{a}=(a_1,a_2,a_3)`.
    The closest point on the plane to the point (:math:`y`) is then given by:

    .. math::
        x =y-(y*a-d)*a/||a||^2

    The distance is then given by the length of the vector :math:`x-y`. This
    function also checks if the intersection point is above `rmax` or inside the
    `zrange`, if not, ``numpy.nan`` is returned for that point.

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
    """

    def _dot(a, b):
        return np.sum(a * b, axis=1)

    def _norm(a):
        ax = 1 if a.ndim == 2 else 0
        return np.sqrt(np.sum(a**2, axis=ax))

    a_norm = np.sum(a_vec * a_vec)

    proj_points = points - ((_dot(points, a_vec) - d)[:, np.newaxis]) * a_vec / a_norm

    dist_vec = _norm((_dot(points, a_vec) - d)[:, np.newaxis] * a_vec / a_norm)

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


def get_line_segments(
    r: ArrayLike, z: ArrayLike, surface_indices: ArrayLike = None
) -> tuple[NDArray, NDArray]:
    """Extracts the line segments from a shape.

    Parameters
    ---------
    r
        array or list of radial positions defining the polycone.
    z
        array or list of vertical positions defining the polycone.
    surface_indices
        list of integer indices of surfaces to consider. If ``None`` (the
        default) all surfaces used.

    Returns
    -------
        tuple of (s1,s2) arrays describing the line segments, both `s1` and
        `s2` have shape `(n_segments,2)` where the first axis represents thhe
        segment and the second `(r,z)`.
    """
    # build lists of pairs of coordinates
    s1 = np.array([np.array([r1, z1]) for r1, z1 in zip(r[:-1], z[:-1])])
    s2 = np.array([np.array([r2, z2]) for r2, z2 in zip(r[1:], z[1:])])

    if surface_indices is not None:
        s1 = s1[surface_indices]
        s2 = s2[surface_indices]

    return s1, s2


# @numba.njit(cache=True)
def shortest_distance(
    s1_list: NDArray,
    s2_list: NDArray,
    points: NDArray,
    tol: float = 1e-11,
    signed: bool = True,
) -> tuple[NDArray, NDArray]:
    """Get the shortest distance between each point and a line segment.

    Based on vector algebra where the distance vector is given by:

    .. math::
        d = s_1 - p - ( (n · (s_1- p)) * n )

    where:

    - :math:`s_1` is a vector from which the distance is measured,
    - `p` is a point vector,
    - `n` is a unit direction vector from :math:`s_1` to :math:`s_2`,
    - `a` is another point vector.

    If the projection point lies inside the segment s1-s2. Else the closest
    point is either :math:`s_1` or :math:`s_2`.  The distance is the modulus of
    this vector and this calculation is performed for each point.  A sign is
    attached based on the cross product of the line vector and the distance
    vector.  To avoid numerical issues any point within the tolerance is
    considered inside.

    Parameters
    ----------
    s1_list
        `(n_segments,2)` np.array of the first points in the line segment, for
        the second axis indices `0,1` correspond to `r,z`.
    s2_list
        second points, same format as `s1_list`.
    points
        `(n_points,2)` array of points to compare, first axis corresponds to
        the point index and the second to `(r,z)`.
    tol
        tolerance when computing sign, points within this distance to the
        surface are pushed inside.
    signed
        boolean flag to attach a sign to the distance (positive if inside).

    Returns
    -------
        ``(n_points,n_segments)`` numpy array of the shortest distances for each segment.
    """

    # helper functions
    def _dot(a, b):
        return np.sum(a * b, axis=1)

    def _norm(a):
        ax = 1 if a.ndim == 2 else 0
        return np.sqrt(np.sum(a**2, axis=ax))

    n_segments = len(s1_list)
    dists = np.full((len(points), len(s1_list)), np.nan)

    for segment in range(n_segments):
        s1 = s1_list[segment]
        s2 = s2_list[segment]
        # check if vertical or horizontal
        # Ensure s2's coordinate is always >= s1's coordinate for simpler logic
        if (s1[0] > s2[0]) or (s1[1] > s2[1]):
            s1, s2 = s2, s1
            sign_factor = -1
        else:
            sign_factor = 1

        if abs(s1[0] - s2[0]) < tol:
            # Compute distances for a vertical segment
            x_level = s1[0]  # x-coordinate of the vertical line
            y_min, y_max = s1[1], s2[1]

            # Points that project onto the segment (y between y_min and y_max)
            mask_on_segment = (points[:, 1] >= y_min) & (points[:, 1] <= y_max)

            # Initialize distance vector
            dist_vec = np.zeros_like(points)

            # For points that project onto the segment (y within bounds)
            x_diff = points[:, 0] - x_level
            dist_vec[mask_on_segment, 0] = x_diff[mask_on_segment]
            dist_vec[mask_on_segment, 1] = 0

            # For points below the segment
            mask_below = points[:, 1] < y_min
            dist_vec[mask_below] = points[mask_below] - s1

            # For points above the segment
            mask_above = points[:, 1] > y_max
            dist_vec[mask_above] = points[mask_above] - s2

            # Compute sign for vertical segment (positive to the right if s2>s1)
            if signed:
                sign_vec_norm = np.ones(len(points))
                # If points are to the left of the line, sign is negative
                sign_vec_norm[x_diff > 0 if sign_factor == 1 else x_diff < 0] = -1
            else:
                sign_vec_norm = np.ones(len(points))

            normed_dist = np.abs(
                np.where(
                    dist_vec[:, 1] == 0,
                    dist_vec[:, 0],
                    _norm(dist_vec),
                )
            )

        # check if horizontal segment
        elif abs(s1[1] - s2[1]) < tol:
            # Compute distances for a horizontal segment
            y_level = s1[1]  # y-coordinate of the horizontal line
            x_min, x_max = s1[0], s2[0]

            # Points that project onto the segment (x between x_min and x_max)
            mask_on_segment = (points[:, 0] >= x_min) & (points[:, 0] <= x_max)

            # Initialize distance vector
            dist_vec = np.zeros_like(points)

            # For points that project onto the segment (x within bounds)
            y_diff = points[:, 1] - y_level
            dist_vec[mask_on_segment, 0] = 0
            dist_vec[mask_on_segment, 1] = y_diff[mask_on_segment]

            # For points to the left of the segment
            mask_left = points[:, 0] < x_min
            dist_vec[mask_left] = points[mask_left] - s1

            # For points to the right of the segment
            mask_right = points[:, 0] > x_max
            dist_vec[mask_right] = points[mask_right] - s2
            # Compute sign for horizontal segment (positive above if s2>s1)
            if signed:
                sign_vec_norm = np.ones(len(points))
                # If points are below the line, sign is negative
                sign_vec_norm[y_diff < 0 if sign_factor == 1 else y_diff > 0] = -1
            else:
                sign_vec_norm = np.ones(len(points))

            normed_dist = np.abs(
                np.where(
                    dist_vec[:, 0] == 0,
                    dist_vec[:, 1],
                    _norm(dist_vec),
                )
            )

        else:
            n = (s2 - s1) / _norm(s2 - s1)

            proj_dist = -_dot(n, (n * _dot(s1 - points, n)[:, np.newaxis]))

            dist_vec = np.empty_like(s1 - points)

            condition1 = proj_dist < 0
            condition2 = proj_dist > _norm(s2 - s1)
            condition3 = (~condition1) & (~condition2)

            diff_s1 = s1 - points
            dist_vec[condition1] = diff_s1[condition1]
            dist_vec[condition2] = s2 - points[condition2]
            dist_vec[condition3] = (
                diff_s1[condition3] - n * _dot(diff_s1, n)[condition3, np.newaxis]
            )

            # make this signed so inside is positive and outside negative
            if signed:
                sign_vec = n[0] * dist_vec[:, 1] - n[1] * dist_vec[:, 0]

                # push points on surface inside
                sign_vec = (
                    np.where(np.abs(sign_vec) < tol, -tol, sign_vec) * sign_factor
                )
                sign_vec_norm = -sign_vec / np.abs(sign_vec)

            else:
                sign_vec_norm = np.ones(len(dist_vec))
            normed_dist = np.abs(_norm(dist_vec))

        dists[:, segment] = np.where(
            normed_dist < tol,
            tol,
            normed_dist * sign_vec_norm,
        )
    return dists
