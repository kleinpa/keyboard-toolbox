"""Generate various artifacts from a keyboard definition."""

import shutil

from absl import app, flags

from kbtb.keyboard import load_keyboard
from kbtb.kicad import polygon_to_kicad_file
from kbtb.pcb import generate_kicad_pcb_file
from kbtb.plate import generate_plate
from kbtb.qmk import make_qmk_header_file

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum('format', 'main_kicad_pcb',
                  ['h', 'main_kicad_pcb', 'plate_kicad_pcb'],
                  'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'plate_kicad_pcb':
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
