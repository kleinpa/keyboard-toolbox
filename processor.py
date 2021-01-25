import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import keyboard_pb2
import shapely
import shapely.geometry
from absl import app, flags

import make_qmk_header
from layout import holes_between_keys, mirror_keys, rotate_keys
from make_plate import (generate_dxf, generate_plate,
                        generate_svg)
from utils import pose, pose_to_xyr

FLAGS = flags.FLAGS
flags.DEFINE_enum(
    'format', 'svg',
    ['h', 'plate_dxf', 'main_kicad_pcb', 'plate_kicad_pcb', 'svg'],
    'Format to emit')
flags.DEFINE_string('output', '', 'Output path')
flags.DEFINE_string('input', '', 'Input path')


def main(argv):
    with open(FLAGS.input, "rb") as fn:
        kb = keyboard_pb2.Keyboard()
        kb.ParseFromString(fn.read())

    if FLAGS.format == 'svg':
        with open(FLAGS.output, 'w') as fn:
            generate_svg(fn, kb)

    elif FLAGS.format == 'plate_dxf':
        with open(FLAGS.output, 'w') as fn:
            plate = generate_plate(kb)
            generate_dxf(fn, plate)

    elif FLAGS.format == 'plate_kicad_pcb':
        from make_plate import generate_kicad
        plate = generate_plate(kb)
        generate_kicad(FLAGS.output, plate)

    elif FLAGS.format == 'h':
        with open(FLAGS.output, 'w') as fn:
            fn.write(make_qmk_header.make_qmk_header(kb))

    elif FLAGS.format == 'main_kicad_pcb':
        from make_pcb import generate_kicad_pcb
        generate_kicad_pcb(FLAGS.output, kb)
    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
