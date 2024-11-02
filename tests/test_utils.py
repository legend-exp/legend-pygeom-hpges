from __future__ import annotations

import numpy as np

from legendhpges import utils


def test_distances():
    # test conversion of coordinates

    coords = np.array([[1, 1, 1], [0, 0, 0]])
    coords_rz = utils.convert_coords(coords)

    assert coords_rz.ndim == 2
    assert np.shape(coords_rz) == (2, 2)
    assert np.allclose(coords_rz[1], np.array([0, 0]))

    # test distances

    a = np.array([[1, 0], [1, 0]])
    b = np.array([[0, 0], [1, 0]])

    assert np.allclose(utils.distance(a, b), np.array([1, 0]))

    # test norm

    a = np.array([1, 0, 0])
    b = np.array([[1, 0], [3, 4]])
    assert utils.norm(a) == 1
    assert np.allclose(utils.norm(b), np.array([1, 5]))

    # test dot
    a = np.array([[1, 0], [1, 0]])
    b = np.array([[0, 0], [1, 0]])

    assert np.allclose(utils.dot(a, b), np.array([0, 1]))

    # test shortest distance
    # in all these
    s1 = np.array([0, 0])
    s2 = np.array([1, 0])

    # first point on segment (distance is 0)
    # second directly above start (distance is 5)
    # third above the segment (distance is 7)
    # fourth outside the segment by 3 units in x and 4 in y (distance is 5)
    # last the same but for the first point

    points = np.array([[0.5, 0], [0, 5], [0.3, 7], [4, 4], [-3, 4]])
    res = np.array([0.0, 5.0, 7.0, 5.0, 5.0])
    assert np.allclose(utils.shortest_distance(s1, s2, points), res)

    # all distances shouldn't be affected by a global offset and rotation
    offset = np.array([107, -203])
    rot = np.array(
        [
            [np.cos(np.rad2deg(37)), -np.sin(np.rad2deg(37))],
            [np.sin(np.rad2deg(37)), np.cos(np.rad2deg(37))],
        ]
    )

    points_new = [rot @ (p_tmp + offset) for p_tmp in points]

    assert np.allclose(
        utils.shortest_distance(rot @ (s1 + offset), rot @ (s2 + offset), points_new),
        res,
    )
