from absl import app, flags

import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import shapely
import shapely.geometry
from absl import app, flags
import google.protobuf.text_format

from layout import mirror_keys, rotate_keys, holes_between_keys
from utils import pose, pose_to_xyr

import keyboard_pb2

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')

# Height to add to each columng of keys for the right hand keys
column_offsets = [0, 2, 4, 2, -1, -2]

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


def quine_1_keyboard():
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
        *(pose(x * pitch, 3 * pitch + column_offsets[x]) for x in range(6)),
        *(pose(x * pitch, 2 * pitch + column_offsets[x]) for x in range(6)),
        *(pose(x * pitch, 1 * pitch + column_offsets[x]) for x in range(6)),
        *(arc(2 - x, 90, (5 / 3) * pitch, column_offsets[1])
          for x in range(3)),
    ]
    keys = list(mirror_keys(rotate_keys(keys, angle=35), middle_space=0))
    holes = holes_between_keys(keys, ((0, 13), (11, 22), (13, 24), (23, 34),
                                      (4, 7), (29, 38), (30, 39)))

    for key in keys:
        x, y, r = pose_to_xyr(key)
        kb.key_poses.append(keyboard_pb2.Pose(x=x, y=y, r=r))
    for hole in holes:
        x, y = hole.x, hole.y
        kb.hole_positions.append(keyboard_pb2.Position(x=x, y=y))

    x, y, r = pose_to_xyr(keys[8])
    kb.controller_pose.CopyFrom(keyboard_pb2.Pose(x=x, y=y, r=r))

    return kb


def main(argv):
    kb = quine_1_keyboard()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
