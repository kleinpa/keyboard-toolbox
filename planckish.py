import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import google.protobuf.text_format
import keyboard_pb2
import shapely
import shapely.geometry
from absl import app, flags

from layout import holes_between_keys, make_key, mirror_keys, rotate_keys
from matrix import fill_matrix
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
    keys = list(mirror_keys(keys, middle_space=0))
    holes = holes_between_keys(keys, ((2, 15), (12, 25), (26, 39), (8, 21),
                                      (22, 35), (32, 45)))

    for key in keys:
        kb.keys.append(key)
    for hole in holes:
        x, y = hole.x, hole.y
        kb.hole_positions.append(keyboard_pb2.Position(x=x, y=y))

    kb.controller_pose.CopyFrom(keys[4].pose)

    return kb


def main(argv):
    kb = planckish_keyboard()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
