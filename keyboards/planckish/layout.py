import sys

from absl import app, flags

from toolbox.keyboard import save_keyboard
from toolbox.keyboard_pb2 import Keyboard, Position
from toolbox.layout import grid, holes_between_keys, mirror_keys, rotate_keys
from toolbox.matrix import fill_matrix

FLAGS = flags.FLAGS
flags.DEFINE_string('output', None, 'Output path.')
flags.DEFINE_enum('format', 'bin', ['bin', 'text'], 'Protobuf output format.')


def planckish_keyboard():
    kb = Keyboard(
        name="planckish",
        controller=Keyboard.CONTROLLER_PROMICRO,
        footprint=Keyboard.FOOTPRINT_CHERRY_MX,
        outline=Keyboard.OUTLINE_TIGHT,

        # Plate outline parameters
        outline_concave=1,
        outline_convex=1.5,
        hole_diameter=2.6,
    )

    keys = [
        *(grid(x, 3) for x in range(6)),
        *(grid(x, 2) for x in range(6)),
        *(grid(x, 1) for x in range(6)),
        *(grid(x, 0) for x in range(6)),
    ]

    for key in mirror_keys(keys, middle_space=0):
        kb.keys.append(key)

    for hole in holes_between_keys(kb.keys, ((2, 15), (12, 25), (26, 39),
                                             (8, 21), (22, 35), (32, 45))):
        kb.hole_positions.append(hole)

    kb.controller_pose.CopyFrom(kb.keys[4].pose)

    fill_matrix(kb)

    return kb


def main(argv):
    kb = planckish_keyboard()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
