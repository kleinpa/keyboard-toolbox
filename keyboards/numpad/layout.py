import sys

import google.protobuf.text_format
import shapely
import shapely.geometry
from absl import app, flags

from toolbox.keyboard_pb2 import Keyboard, Position
from toolbox.layout import holes_between_keys, make_key, mirror_keys, rotate_keys, row
from toolbox.matrix import fill_matrix_random
from toolbox.utils import pose, pose_to_xyr

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')


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

    pitch = 19.05

    keys = [
        row(0, 4),
        row(1, 4),
        row(2, 4),
        row(3, 4),
        row(0, 3),
        row(1, 3),
        row(2, 3),
        row(3, 2.5),
        row(0, 2),
        row(1, 2),
        row(2, 2),
        row(0, 1),
        row(1, 1),
        row(2, 1),
        row(3, 0.5),
        row(0.5, 0),
        row(2, 0),
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
