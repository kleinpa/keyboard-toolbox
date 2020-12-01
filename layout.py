import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import shapely
import shapely.geometry
from absl import app, flags

from utils import *

FLAGS = flags.FLAGS

# Height to add to each columng of keys for the right hand keys
column_offsets = [0, 2, 4, 2, -1, -2]

# Polygon describing the shape of an individual key cutout
cutout_geom_square = shapely.geometry.polygon.Polygon([
    (7, 7),
    (7, -7),
    (-7, -7),
    (-7, 7),
])
cutout_geom_mx_alps = shapely.geometry.polygon.Polygon([
    # from https://github.com/swill/kad/blob/62948e9/key.go
    (7, -7),
    (7, -6.4),
    (7.8, -6.4),
    (7.8, 6.4),
    (7, 6.4),
    (7, 7),
    (-7, 7),
    (-7, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
    (-7, -6.4),
    (-7, -7),
])
cutout_geom_mx_wings = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    (7, -7),
    (7, -6),
    (7.8, -6),
    (7.8, -2.9),
    (7, -2.9),
    (7, 2.9),
    (7.8, 2.9),
    (7.8, 6),
    (7, 6),
    (7, 7),
    (-7, 7),
    (-7, 6),
    (-7.8, 6),
    (-7.8, 2.9),
    (-7, 2.9),
    (-7, -2.9),
    (-7.8, -2.9),
    (-7.8, -6),
    (-7, -6),
    (-7, -7),
])
cutout_geom_alps = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    (7.8, -6.4),
    (7.8, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
])
cutout_geom = cutout_geom_mx_wings

# Parameters for processing the plate outline
outline_fill = 90
outline_round = 1.5
outline_pad = 0

hole_diameter = 2.6

# helpful design reference https://matt3o.com/anatomy-of-a-keyboard/
pitch = 19.05
mcu_key_index = 8


def arc(n, r, x_offset=0, y_offset=0):
    geom = pose(x_offset, y_offset)
    about = shapely.affinity.translate(geom[0], yoff=-pitch / 2 - r)
    geom = shapely.affinity.rotate(geom,
                                   n * 2 * atan(pitch / 2 / r),
                                   use_radians=True,
                                   origin=about)
    return geom


def quine_1_keyboard():
    keys = [
        *(pose(x * pitch, 3 * pitch + column_offsets[x]) for x in range(6)),
        *(pose(x * pitch, 2 * pitch + column_offsets[x]) for x in range(6)),
        *(pose(x * pitch, 1 * pitch + column_offsets[x]) for x in range(6)),
        *(arc(2 - x, 90, (5 / 3) * pitch, column_offsets[1])
          for x in range(3)),
    ]
    keys = list(mirror_keys(rotate_keys(keys, angle=35), middle_space=0))
    holes = holes_between_keys(keys, ((0, 13), (11, 22), (13, 24), (23, 34),
                                      (4, 7), (29, 38), (30, 39)))
    return Keyboard(keys, list(holes))


def make_planck_layout():
    keys = [
        *(pose(x * pitch, 4 * pitch) for x in range(6)),
        *(pose(x * pitch, 3 * pitch) for x in range(6)),
        *(pose(x * pitch, 2 * pitch) for x in range(6)),
        *(pose(x * pitch, 1 * pitch) for x in range(6)),
    ]

    return mirror_keys(keys, middle_space=middle_space)


#make_layout = make_planck_layout
