"""Generate various artifacts from a keyboard definition."""

import shutil

from absl import app, flags

from kbtb.dxf import polygon_to_dxf_file
from kbtb.keyboard import load_keyboard
from kbtb.plate import generate_plate

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum('format', 'plate_dxf', ['plate_dxf'],
                  'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'plate_dxf':
        with open(FLAGS.output, 'wb') as output:
            plate = generate_plate(kb)
            shutil.copyfileobj(polygon_to_dxf_file(plate), output)

    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
