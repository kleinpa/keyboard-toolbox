"""A basic example keyboard layout used for testing."""

from math import atan2, cos, degrees, radians, sin
from absl import app, flags
import json

import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard, Position
from kbtb.layout import between_pose, pose_closest_point, project_to_outline
from kbtb.kle import kle_to_keyboard

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')


def main(argv):
    kb = kle_to_keyboard(
        json.loads('[["","",""],["","",""],["","",""]]'),
        controller=Keyboard.CONTROLLER_STM32F072,
        switch=Keyboard.SWITCH_CHERRY_MX,
        outline_type="rectangle",
        info_text="kbtb/stm32f072@{git}")

    # Read the outline that kle_to_keyboard generated
    outline = shapely.geometry.polygon.LinearRing(
        (o.x, o.y) for o in kb.outline_polygon)

    kb.connector_pose.CopyFrom(
        pose_closest_point(outline,
                           between_pose(kb.keys[0].pose, kb.keys[1].pose)))
    kb.connector_pose.x -= .7

    kb.controller_pose.CopyFrom(between_pose(kb.keys[1].pose, kb.keys[5].pose))

    kb.info_pose.CopyFrom(
        project_to_outline(outline, kb.keys[-2].pose, offset=-2))

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
