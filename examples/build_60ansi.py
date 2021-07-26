"""A basic example keyboard layout used for testing."""

import os
import json
import sys

import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard, Position
from kbtb.layout import between_pose, pose_closest_point, project_to_outline
from kbtb.kle import kle_to_keyboard


def main():
    kb = kle_to_keyboard(
        json.loads("""[
            ["","","","","","","","","","","","","",{"w":2},""],
            [{"w":1.5},"","","","","","","","","","","","","",{"w":1.5},""],
            [{"w":1.75},"","","","","","","","","","","","",{"w":2.25},""],
            [{"w":2.25},"","","","","","","","","","","",{"w":2.75},""],
            [{"w":1.25},"",{"w":1.25},"",{"w":1.25},"",{"a":7,"w":6.25},"",{"a":4,"w":1.25},"",{"w":1.25},"",{"w":1.25},"",{"w":1.25},""]
        ]"""),
        controller=Keyboard.CONTROLLER_STM32F072,
        switch=Keyboard.SWITCH_CHERRY_MX,
        outline_type="rectangle",
        info_text="tkl")

    kb.url = "https://github.com/kleinpa/keyboard-toolbox"

    def bottom_left_of(pose, pitch=19):
        return Position(x=pose.x + pitch / 2, y=pose.y - pitch / 2)

    kb.hole_positions.extend([
        # TODO: fill some thing in here?
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

    kb.info_pose.CopyFrom(
        project_to_outline(
            outline,
            between_pose(kb.keys[16].pose, kb.keys[14].pose),
            offset=-2))

    kb.qmk.layout = "60_ansi"

    with open(sys.argv[1], 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    main()
