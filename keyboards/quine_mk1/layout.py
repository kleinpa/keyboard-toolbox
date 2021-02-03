import sys

import shapely.geometry
from absl import app, flags

from toolbox.keyboard import save_keyboard
from toolbox.keyboard_pb2 import Keyboard, Position
from toolbox.layout import holes_between_keys, mirror_keys, rotate_keys, grid

FLAGS = flags.FLAGS
flags.DEFINE_string('output', None, 'Output path.')
flags.DEFINE_enum('format', 'bin', ['bin', 'text'], 'Protobuf output format.')


def quine_1_keyboard():
    kb = Keyboard(
        name="quine-mk1",
        controller=Keyboard.CONTROLLER_PROMICRO,
        footprint=Keyboard.FOOTPRINT_CHERRY_MX,
        outline=Keyboard.OUTLINE_TIGHT,

        # Plate outline parameters
        outline_concave=90,
        outline_convex=1.5,
        hole_diameter=2.6,
    )

    pitch = 19.05
    column_offsets = [0, 2, 4, 2, -1, -2]
    keys = [
        *(grid(x, 3, y_offset=column_offsets[x]) for x in range(6)),
        *(grid(x, 2, y_offset=column_offsets[x]) for x in range(6)),
        *(grid(x, 1, y_offset=column_offsets[x]) for x in range(6)),
        *(grid(x,
               0,
               arc_radius=90,
               x_offset=-1 / 3 * pitch,
               y_offset=column_offsets[1]) for x in range(3)),
    ]

    for key in mirror_keys(rotate_keys(keys, angle=35), middle_space=0):
        kb.keys.append(key)

    for hole in holes_between_keys(kb.keys, [(0, 13), (11, 22), (13, 24),
                                             (23, 34), (4, 7), (29, 38),
                                             (30, 39)]):
        kb.hole_positions.append(hole)

    kb.controller_pose.CopyFrom(kb.keys[8].pose)

    # TODO: un-hardcode
    row_nets = [0, 7, 8, 9]
    col_nets = [17, 16, 15, 14, 13, 12, 11, 10, 6, 5, 4, 3]
    for i, key in enumerate(kb.keys):
        key.controller_pin_low = row_nets[i // 12]
        key.controller_pin_high = col_nets[(i % 12) +
                                           (3 if i // 12 == 3 else 0)]

    return kb


def main(argv):
    kb = quine_1_keyboard()
    save_keyboard(kb, FLAGS.output, FLAGS.format)


if __name__ == "__main__":
    app.run(main)
