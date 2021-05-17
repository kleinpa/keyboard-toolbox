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
    kb = kle_to_keyboard(json.loads('[["",""],["",""],["",""]]'))

    kb.controller = Keyboard.CONTROLLER_ATMEGA32U4
    kb.footprint = Keyboard.FOOTPRINT_CHERRY_MX
    kb.hole_diameter = 2.4

    fill_matrix_rows(kb)

    outline = generate_outline_convex_hull(kb)

    kb.connector_pose.CopyFrom(
        pose_closest_point(outline,
                           between_pose(kb.keys[0].pose, kb.keys[1].pose)))
    kb.connector_pose.x -= .7

    kb.controller_pose.CopyFrom(between_pose(kb.keys[3].pose, kb.keys[4].pose))

    # kle_to_keyboard adds a default outline so remove it
    kb.ClearField("outline_polygon")

    for x, y in outline.coords:
        kb.outline_polygon.add(x=x, y=y)

    for sw1, sw2 in [(1, 3), (3, 5), (4, 2), (2, 0)]:
        pose = pose_closest_point(
            shapely.geometry.Polygon(outline).buffer(-4).exterior,
            between_pose(kb.keys[sw1].pose, kb.keys[sw2].pose))
        kb.hole_positions.extend([Position(x=pose.x, y=pose.y)])

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
