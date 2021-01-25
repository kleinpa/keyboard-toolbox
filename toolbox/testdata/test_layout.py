import sys

import google.protobuf.text_format
from absl import app, flags

from toolbox.keyboard_pb2 import Keyboard
from toolbox.layout import between, mirror_keys, rotate_keys, grid
from toolbox.matrix import fill_matrix
from toolbox.utils import pose

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')


def test_layout():
    kb = Keyboard(
        name="test-layout",
        controller=Keyboard.CONTROLLER_PROMICRO,
        footprint=Keyboard.FOOTPRINT_CHERRY_MX,
        outline=Keyboard.OUTLINE_TIGHT,

        # Plate outline parameters
        outline_concave=120,
        outline_convex=1.5,
        hole_diameter=2.6,
    )

    rows = 4

    pitch = 19.05
    column_offsets = [-1, 0, 1, 0, -1, -2]
    keys = [
        *(grid(x, row, y_offset=column_offsets[x])
          for row in range(rows - 1, 0, -1) for x in range(6)),
        *(grid(x,
               0,
               arc_radius=120,
               x_offset=-1 / 3 * pitch,
               y_offset=column_offsets[1]) for x in range(3)),
    ]

    for key in mirror_keys(rotate_keys(keys, angle=19), middle_space=0):
        kb.keys.append(key)
    kb.hole_positions.extend([
        between(kb.keys[0].pose, kb.keys[13].pose),
        between(kb.keys[11].pose, kb.keys[22].pose),
        between(kb.keys[4].pose, kb.keys[17].pose),
        between(kb.keys[7].pose, kb.keys[18].pose),
        between(kb.keys[25 + (rows - 5) * 12].pose,
                kb.keys[36 + (rows - 5) * 12].pose),
        between(kb.keys[35 + (rows - 5) * 12].pose,
                kb.keys[46 + (rows - 5) * 12].pose),
        between(kb.keys[41 + (rows - 5) * 12].pose,
                kb.keys[50 + (rows - 5) * 12].pose),
        between(kb.keys[42 + (rows - 5) * 12].pose,
                kb.keys[51 + (rows - 5) * 12].pose)
    ])

    kb.controller_pose.CopyFrom(kb.keys[8].pose)

    fill_matrix(kb)

    return kb


def main(argv):
    kb = test_layout()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
