"""A basic example keyboard layout used for testing."""

from math import atan2, cos, degrees, radians, sin
from absl import app, flags
import json

import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard, Position
from kbtb.layout import between, between_pose, pose_closest_point, mirror_keys, rotate_keys, grid
from kbtb.matrix import fill_matrix_rows
from kbtb.kle import kle_to_keyboard
from kbtb.outline import generate_outline_convex_hull

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')


def main(argv):
    kb = kle_to_keyboard(
        json.loads('[["","",""],["","",""],["","",""]]'),
        controller=Keyboard.CONTROLLER_STM32F072,
        switch=Keyboard.SWITCH_CHERRY_MX,
        outline_type="rectangle",
    )

    # Read the outline that kle_to_keyboard generated
    outline = shapely.geometry.polygon.LinearRing(
        (o.x, o.y) for o in kb.outline_polygon)

    kb.connector_pose.CopyFrom(
        pose_closest_point(outline,
                           between_pose(kb.keys[0].pose, kb.keys[1].pose)))
    kb.connector_pose.x -= .7

    kb.controller_pose.CopyFrom(between_pose(kb.keys[1].pose, kb.keys[5].pose))

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
