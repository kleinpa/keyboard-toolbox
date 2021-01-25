import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import google.protobuf.text_format
import keyboard_pb2
import shapely
import shapely.geometry
from absl import app, flags

from layout import holes_between_keys, make_key, mirror_keys, rotate_keys
from utils import pose, pose_to_xyr

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

    x, y, r = pose_to_xyr(geom)
    return keyboard_pb2.Keyboard.Key(pose={"x": x, "y": y, "r": r})


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
        *(make_key(x * pitch, 3 * pitch + column_offsets[x])
          for x in range(6)),
        *(make_key(x * pitch, 2 * pitch + column_offsets[x])
          for x in range(6)),
        *(make_key(x * pitch, 1 * pitch + column_offsets[x])
          for x in range(6)),
        *(arc(2 - x, 90, (5 / 3) * pitch, column_offsets[1])
          for x in range(3)),
    ]

    keys = list(mirror_keys(rotate_keys(keys, angle=35), middle_space=0))
    holes = holes_between_keys(keys, ((0, 13), (11, 22), (13, 24), (23, 34),
                                      (4, 7), (29, 38), (30, 39)))

    for key in keys:
        kb.keys.append(key)
    for hole in holes:
        x, y = hole.x, hole.y
        kb.hole_positions.append(keyboard_pb2.Position(x=x, y=y))

    kb.controller_pose.CopyFrom(keys[8].pose)

    # TODO: un-hardcode
    row_nets = (0, 7, 8, 9)
    col_nets = (17, 16, 15, 14, 13, 12, 11, 10, 6, 5, 4, 3)
    for i, key in enumerate(kb.keys):
        key.controller_pin_low = row_nets[i // 12]
        key.controller_pin_high = col_nets[(i % 12) +
                                           (3 if i // 12 == 3 else 0)]

    return kb


def main(argv):
    kb = quine_1_keyboard()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
