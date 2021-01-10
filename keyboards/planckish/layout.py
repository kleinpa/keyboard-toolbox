import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import google.protobuf.text_format
import shapely
import shapely.geometry
from absl import app, flags

from toolbox.keyboard_pb2 import Keyboard, Position
from toolbox.layout import holes_between_keys, make_key, mirror_keys, rotate_keys
from toolbox.matrix import fill_matrix
from toolbox.utils import pose, pose_to_xyr

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
    kb = Keyboard(
        controller=Keyboard.CONTROLLER_PROMICRO,
        footprint=Keyboard.FOOTPRINT_CHERRY_MX,
        outline=Keyboard.OUTLINE_TIGHT,

        # Plate outline parameters
        outline_concave=1,
        outline_convex=1.5,
        hole_diameter=2.6,
    )

    keys = [
        *(make_key(x * pitch, 3 * pitch) for x in range(6)),
        *(make_key(x * pitch, 2 * pitch) for x in range(6)),
        *(make_key(x * pitch, 1 * pitch) for x in range(6)),
        *(make_key(x * pitch, 0 * pitch) for x in range(6)),
    ]

    for key in mirror_keys(keys, middle_space=0):
        kb.keys.append(key)

    for hole in holes_between_keys(kb.keys, ((2, 15), (12, 25), (26, 39),
                                             (8, 21), (22, 35), (32, 45))):
        kb.hole_positions.append(Position(x=hole.x, y=hole.y))

    kb.controller_pose.CopyFrom(kb.keys[4].pose)

    return kb


def main(argv):
    kb = planckish_keyboard()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
