import json
import sys

import shapely.geometry
from absl import app, flags

from kbtb.keyboard import save_keyboard
from kbtb.keyboard_pb2 import Keyboard, Position
from kbtb.kle import kle_to_keyboard
from kbtb.layout import (between_pose, grid, holes_between_keys, mirror_keys,
                         pose_closest_point, project_to_outline, rotate_keys)
from kbtb.matrix import fill_matrix_rows
from kbtb.outline import generate_outline_rectangle, generate_outline_tight

FLAGS = flags.FLAGS
flags.DEFINE_string('output', None, 'Output path.')
flags.DEFINE_enum('format', 'bin', ['bin', 'text'], 'Protobuf output format.')

flags.DEFINE_string('description', None, 'Variant label.')
flags.DEFINE_enum('mcu', 'atmega32u4',
                  ['atmega32u4', 'stm32f072', 'atmega328p', 'promicro'],
                  'Board variant')
flags.DEFINE_enum('switch', 'mx', ['mx', 'alps'], 'Board variant')


def layout():
    kle = json.loads("""[
            {"name": "numpad17"},
            ["", "", "", ""],
            ["", "", "", {"h": 2.0}, ""],
            ["", "", ""],
            ["", "", "", {"h": 2.0}, ""],
            [{"w": 2.0}, "", ""]
        ]""")

    if FLAGS.mcu == 'atmega32u4':
        controller = Keyboard.CONTROLLER_ATMEGA32U4
    elif FLAGS.mcu == 'stm32f072':
        controller = Keyboard.CONTROLLER_STM32F072
    elif FLAGS.mcu == 'promicro':
        controller = Keyboard.CONTROLLER_PROMICRO
    elif FLAGS.mcu == 'atmega328':
        controller = Keyboard.CONTROLLER_ATMEGA328
    else:
        raise RuntimeError(f"unknown controller {FLAGS.mcu}")

    if FLAGS.switch == 'mx':
        switch = Keyboard.SWITCH_CHERRY_MX
    else:
        raise RuntimeError(f"unknown switch {FLAGS.switch}")

    kb = kle_to_keyboard(
        kle,
        controller=controller,
        switch=switch,
        info_text=FLAGS.description + "\npeterklein.dev",
    )

    kb.name = FLAGS.description

    def pitch_offset(pose, x, y, pitch=19.01):
        return Position(x=pose.x + (x * pitch), y=pose.y + (y * pitch))

    kb.hole_positions.extend([
        # pitch_offset(kb.keys[0].pose, 0.5, -0.5),
        # pitch_offset(kb.keys[2].pose, 0.5, -0.5),
        # pitch_offset(kb.keys[8].pose, 0.5, -0.5),
        # pitch_offset(kb.keys[12].pose, 0.5, -0.5),
        # pitch_offset(kb.keys[10].pose, 0.5, -0.5),
    ])

    # Read the outline that kle_to_keyboard generated
    outline = shapely.geometry.polygon.LinearRing(
        (o.x, o.y) for o in kb.outline_polygon)

    if FLAGS.mcu == 'atmega32u4' or FLAGS.mcu == 'stm32f072' or FLAGS.mcu == 'atmega328':
        kb.connector_pose.CopyFrom(
            pose_closest_point(outline,
                               between_pose(kb.keys[1].pose, kb.keys[2].pose)))
        kb.connector_pose.x -= .7
        kb.controller_pose.CopyFrom(
            between_pose(kb.keys[5].pose, kb.keys[10].pose))
        kb.controller_pose.y += 2
    elif FLAGS.mcu == 'promicro':
        kb.controller_pose.CopyFrom(kb.keys[2].pose)
    else:
        raise RuntimeError(f"unknown controller {FLAGS.mcu}")

    kb.info_pose.CopyFrom(
        project_to_outline(
            outline,
            between_pose(kb.keys[16].pose, kb.keys[14].pose),
            offset=-2))

    kb.qmk.layout = "numpad_5x4"
    kb.qmk.layout_sequence[:] = [
        0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 7, 11, 12, 13, 15, 16, 14
    ]

    fill_matrix_rows(kb)

    return kb


def main(argv):
    save_keyboard(layout(), FLAGS.output, FLAGS.format)


if __name__ == "__main__":
    app.run(main)
