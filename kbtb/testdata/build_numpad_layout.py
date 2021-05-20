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
    ]"""),
        controller=Keyboard.CONTROLLER_ATMEGA32U4,
        switch=Keyboard.SWITCH_CHERRY_MX,
        outline_type="rectangle")

    def bottom_left_of(pose, pitch=19):
        return Position(x=pose.x + pitch / 2, y=pose.y - pitch / 2)

    kb.hole_positions.extend([
        bottom_left_of(kb.keys[0].pose),
        bottom_left_of(kb.keys[2].pose),
        bottom_left_of(kb.keys[11].pose),
        bottom_left_of(kb.keys[13].pose),
    ])

    # Read the outline that kle_to_keyboard generated
    outline = shapely.geometry.polygon.LinearRing(
        (o.x, o.y) for o in kb.outline_polygon)

    kb.connector_pose.CopyFrom(
        pose_closest_point(outline,
                           between_pose(kb.keys[1].pose, kb.keys[2].pose)))
    kb.connector_pose.x -= .7

    kb.controller_pose.CopyFrom(
        between_pose(kb.keys[5].pose, kb.keys[10].pose))
    kb.controller_pose.y += 2

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
