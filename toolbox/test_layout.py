import sys

import google.protobuf.text_format
import shapely
import shapely.geometry
from absl import app, flags

from toolbox.keyboard_pb2 import Keyboard, Position
from toolbox.layout import holes_between_keys, make_key, mirror_keys, rotate_keys, row
from toolbox.matrix import fill_matrix
from toolbox.utils import pose, pose_to_xyr

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')


def keyboard():
    kb = Keyboard(
        controller=Keyboard.CONTROLLER_PROMICRO,
        footprint=Keyboard.FOOTPRINT_CHERRY_MX,
        outline=Keyboard.OUTLINE_TIGHT,

        # Plate outline parameters
        outline_concave=90,
        outline_convex=1.5,
        hole_diameter=2.6,
    )

    # Height to add to each columng of keys for the right hand keys
    column_offsets = [-1.5, 0, 5, 2.25, -4.8, -6.3]
    pitch = 19.05
    r = 900
    keys = [
        *(row(x, 4, y_offset=column_offsets[x], arc_radius=r)
          for x in range(6)),
        *(row(x, 3, y_offset=column_offsets[x], arc_radius=r)
          for x in range(6)),
        *(row(x, 2, y_offset=column_offsets[x], arc_radius=r)
          for x in range(6)),
        *(row(x, 1, y_offset=column_offsets[x], arc_radius=r)
          for x in range(6)),
        *(row(x,
              0,
              arc_radius=90,
              x_offset=(-1 / 3) * pitch,
              y_offset=column_offsets[1]) for x in range(3)),
    ]

    #keys = mirror_keys(keys, only_flip=True)

    for key in keys:
        kb.keys.append(key)

    holes = holes_between_keys(kb.keys, ((0, 7), (12, 19), (4, 11), (23, 26)))
    for hole in holes:
        x, y = hole.x, hole.y
        kb.hole_positions.append(Position(x=x, y=y))

    kb.controller_pose.CopyFrom(kb.keys[3].pose)

    # TODO: un-hardcode
    row_nets = (0, 6, 7, 8, 9)
    col_nets = (17, 16, 15, 14, 13, 12, 11, 10, 5, 4, 3)
    for i, key in enumerate(kb.keys):
        key.controller_pin_low = row_nets[i // 6]
        key.controller_pin_high = col_nets[(i % 6) + (3 if i // 6 == 4 else 0)]

    return kb


def main(argv):
    kb = keyboard()
    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
