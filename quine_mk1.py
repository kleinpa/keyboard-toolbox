from absl import app, flags

FLAGS = flags.FLAGS
flags.DEFINE_enum(
    'format', 'pb',
    ['pb', 'plate_dxf', 'main_kicad_pcb', 'plate_kicad_pcb', 'svg'],
    'Format to emit')
flags.DEFINE_string('output', '', 'Output path')

import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import shapely
import shapely.geometry
from absl import app, flags

from layout import mirror_keys, rotate_keys, holes_between_keys
from utils import pose, pose_to_xyr
from make_plate import generate_plate, generate_svg, generate_dxf, generate_kicad
from make_pcb import generate_kicad_pcb
import make_qmk_header

import keyboard_pb2

FLAGS = flags.FLAGS

# Height to add to each columng of keys for the right hand keys
column_offsets = [0, 2, 4, 2, -1, -2]

# helpful design reference https://matt3o.com/anatomy-of-a-keyboard/
pitch = 19.05


def arc(n, r, x_offset=0, y_offset=0):
    geom = pose(x_offset, y_offset)
    about = shapely.affinity.translate(geom[0], yoff=-pitch / 2 - r)
    geom = shapely.affinity.rotate(geom,
                                   n * 2 * atan(pitch / 2 / r),
                                   use_radians=True,
                                   origin=about)
    return geom


def quine_1_keyboard():
    keys = [
        *(pose(x * pitch, 3 * pitch + column_offsets[x]) for x in range(6)),
        *(pose(x * pitch, 2 * pitch + column_offsets[x]) for x in range(6)),
        *(pose(x * pitch, 1 * pitch + column_offsets[x]) for x in range(6)),
        *(arc(2 - x, 90, (5 / 3) * pitch, column_offsets[1])
          for x in range(3)),
    ]
    keys = list(mirror_keys(rotate_keys(keys, angle=35), middle_space=0))
    holes = holes_between_keys(keys, ((0, 13), (11, 22), (13, 24), (23, 34),
                                      (4, 7), (29, 38), (30, 39)))
    kb = keyboard_pb2.Keyboard()

    for key in keys:
        x, y, r = pose_to_xyr(key)
        kb.key_poses.append(keyboard_pb2.Pose(x=x, y=y, r=r))
    for hole in holes:
        x, y = hole.x, hole.y
        kb.hole_positions.append(keyboard_pb2.Position(x=x, y=y))

    kb.footprint = keyboard_pb2.Keyboard.FOOTPRINT_CHERRY_MX
    kb.outline = keyboard_pb2.Keyboard.OUTLINE_TIGHT
    kb.controller = keyboard_pb2.Keyboard.CONTROLLER_PROMICRO

    x, y, r = pose_to_xyr(keys[8])
    kb.controller_pose.CopyFrom(keyboard_pb2.Pose(x=x, y=y, r=r))

    # Parameters for processing the plate outline
    kb.outline_concave = 90
    kb.outline_convex = 1.5
    kb.hole_diameter = 2.6

    return kb


def main(argv):
    kb = quine_1_keyboard()

    if FLAGS.format == 'pb':
        import google.protobuf.text_format
        with open(FLAGS.output, 'w') as fn:
            google.protobuf.text_format.PrintMessage(kb, fn)

    elif FLAGS.format == 'svg':
        with open(FLAGS.output, 'w') as fn:
            generate_svg(fn, kb)

    elif FLAGS.format == 'plate_dxf':
        with open(FLAGS.output, 'w') as fn:
            plate = generate_plate(kb)
            generate_dxf(fn, plate)
    elif FLAGS.format == 'plate_kicad_pcb':
        plate = generate_plate(kb)
        generate_kicad(FLAGS.output, plate)

    elif FLAGS.format == 'main_kicad_pcb':
        print(FLAGS.output)
        generate_kicad_pcb(FLAGS.output, kb)
    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
