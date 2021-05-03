"""A basic example keyboard layout used for testing."""

from math import atan2, cos, degrees, radians, sin
from absl import app, flags
import json

import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard, Position
from kbtb.layout import between, between_pose, pose_closest_point, mirror_keys, rotate_keys, grid
from kbtb.matrix import fill_matrix_rows
from kbtb.kle import kle_to_keyboard
from kbtb.outline import generate_outline_rectangle

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')


def main(argv):
    kb = kle_to_keyboard(
        json.loads("""[
        ["", "", "", ""],
        ["", "", "", {"h": 2.0}, ""],
        ["", "", ""],
        ["", "", "", {"h": 2.0}, ""],
        [{"w": 2.0}, "", ""]
    ]"""))

    kb.controller = Keyboard.CONTROLLER_STM32F072
    kb.footprint = Keyboard.FOOTPRINT_CHERRY_MX
    kb.hole_diameter = 2.4

    pitch = 19
    kb.hole_positions.extend([
        Position(x=kb.keys[0].pose.x + pitch / 2,
                 y=kb.keys[0].pose.y - pitch / 2),
        Position(x=kb.keys[2].pose.x + pitch / 2,
                 y=kb.keys[2].pose.y - pitch / 2),
        Position(x=kb.keys[11].pose.x + pitch / 2,
                 y=kb.keys[11].pose.y - pitch / 2),
        Position(x=kb.keys[13].pose.x + pitch / 2,
                 y=kb.keys[13].pose.y - pitch / 2),
    ])

    fill_matrix_rows(kb)

    outline = generate_outline_rectangle(kb)

    kb.controller_pose.CopyFrom(
        pose_closest_point(outline,
                           between_pose(kb.keys[1].pose, kb.keys[2].pose)))
    kb.controller_pose.x -= .7

    # kle_to_keyboard adds a default outline so remove it
    kb.ClearField("outline_polygon")

    for x, y in outline.coords:
        kb.outline_polygon.add(x=x, y=y)

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
