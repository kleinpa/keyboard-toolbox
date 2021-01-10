import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import google.protobuf.text_format
import shapely
import shapely.geometry
from absl import app, flags

from toolbox.keyboard_pb2 import Keyboard, Position
from toolbox.layout import holes_between_keys, make_key, mirror_keys, rotate_keys
from toolbox.matrix import fill_matrix_random
from toolbox.utils import pose, pose_to_xyr

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')

# helpful design reference https://matt3o.com/anatomy-of-a-keyboard/
pitch = 19.05


def planckish_keyboard():
    kb = Keyboard(
        controller=Keyboard.CONTROLLER_PROMICRO,
        footprint=Keyboard.FOOTPRINT_CHERRY_MX,
        outline=Keyboard.OUTLINE_TIGHT,

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
        kb.hole_positions.append(Position(x=hole.x, y=hole.y))

    kb.controller_pose.CopyFrom(kb.keys[8].pose)

    fill_matrix_random(kb)
    return kb


def main(argv):
    kb = planckish_keyboard()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
