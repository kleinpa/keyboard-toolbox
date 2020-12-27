import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import google.protobuf.text_format
import keyboard_pb2
import shapely
import shapely.geometry
from absl import app, flags

from layout import holes_between_keys, make_key, mirror_keys, rotate_keys
from matrix import fill_matrix_random
from utils import pose, pose_to_xyr

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')

# helpful design reference https://matt3o.com/anatomy-of-a-keyboard/
pitch = 19.05


def arc(n, r, x_offset=0, y_offset=0):
    geom = pose(x_offset, y_offset)
    about = shapely.affinity.translate(geom[0], yoff=-pitch / 2 - r)
    geom = shapely.affinity.rotate(geom,
                                   n * 2 * atan(pitch / 2 / r),
                                   use_radians=True,
                                   origin=about)
    return geom


def planckish_keyboard():
    kb = keyboard_pb2.Keyboard(
        controller=keyboard_pb2.Keyboard.CONTROLLER_PROMICRO,
        footprint=keyboard_pb2.Keyboard.FOOTPRINT_CHERRY_MX,
        outline=keyboard_pb2.Keyboard.OUTLINE_TIGHT,

        # Plate outline parameters
        outline_concave=90,
        outline_convex=1.5,
        hole_diameter=2.6,
    )

    keys = [
        make_key(0 * pitch, 4 * pitch),
        make_key(1 * pitch, 4 * pitch),
        make_key(2 * pitch, 4 * pitch),
        make_key(3 * pitch, 4 * pitch),
        make_key(0 * pitch, 3 * pitch),
        make_key(1 * pitch, 3 * pitch),
        make_key(2 * pitch, 3 * pitch),
        make_key(3 * pitch, 2.5 * pitch),
        make_key(0 * pitch, 2 * pitch),
        make_key(1 * pitch, 2 * pitch),
        make_key(2 * pitch, 2 * pitch),
        make_key(0 * pitch, 1 * pitch),
        make_key(1 * pitch, 1 * pitch),
        make_key(2 * pitch, 1 * pitch),
        make_key(3 * pitch, 0.5 * pitch),
        make_key(0.5 * pitch, 0 * pitch),
        make_key(2 * pitch, 0 * pitch),
    ]

    holes = [shapely.geometry.Point((1, 1))]

    for key in keys:
        kb.keys.append(key)
    for hole in holes:
        x, y = hole.x, hole.y
        kb.hole_positions.append(keyboard_pb2.Position(x=x, y=y))

    kb.controller_pose.CopyFrom(keys[8].pose)

    fill_matrix_random(kb)
    return kb


def main(argv):
    kb = planckish_keyboard()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
