"""Generate various artifacts from a keyboard definition."""

import shutil

from absl import app, flags

from kbtb.dxf import polygon_to_dxf_file
from kbtb.keyboard import load_keyboard
from kbtb.plate import generate_plate

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_string('plate_type', 'top', 'Plate type.')
flags.DEFINE_enum('format', 'plate_dxf', ['plate_dxf'],
                  'Type of output to generate.')


def generate_plate_by_type(kb):
    if FLAGS.plate_type == "top":
        return generate_plate(kb, mounting_holes=False, cutouts=True)
    if FLAGS.plate_type == "bottom":
        return generate_plate(kb, mounting_holes=True, cutouts=False)


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'plate_dxf':
        with open(FLAGS.output, 'wb') as output:
            plate = generate_plate_by_type(kb)
            shutil.copyfileobj(polygon_to_dxf_file(plate), output)

    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
