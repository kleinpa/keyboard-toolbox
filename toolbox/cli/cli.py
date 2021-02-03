"""Generate various artifacts from a keyboard definition."""

import shutil

from absl import app, flags

from toolbox.dxf_utils import polygon_to_dxf_file
from toolbox.keyboard import load_keyboard
from toolbox.kicad_utils import polygon_to_kicad_file
from toolbox.make_pcb import generate_kicad_pcb_file
from toolbox.make_plate import generate_plate
from toolbox.qmk_utils import make_qmk_header_file
from toolbox.svg import keyboard_to_layout_svg_file

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum(
    'format', 'svg',
    ['h', 'plate_dxf', 'main_kicad_pcb', 'plate_kicad_pcb', 'svg'],
    'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'svg':
        with open(FLAGS.output, 'wb') as output:
            shutil.copyfileobj(keyboard_to_layout_svg_file(kb), output)

    elif FLAGS.format == 'plate_dxf':
        with open(FLAGS.output, 'wb') as output:
            plate = generate_plate(kb)
            shutil.copyfileobj(polygon_to_dxf_file(plate), output)

    elif FLAGS.format == 'plate_kicad_pcb':
        with open(FLAGS.output, 'wb') as output:
            plate = generate_plate(kb)
            shutil.copyfileobj(polygon_to_kicad_file(plate), output)

    elif FLAGS.format == 'h':
        with open(FLAGS.output, 'wb') as output:
            shutil.copyfileobj(make_qmk_header_file(kb), output)

    elif FLAGS.format == 'main_kicad_pcb':
        with open(FLAGS.output, 'wb') as output:
            shutil.copyfileobj(generate_kicad_pcb_file(kb), output)

    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
