"""Generate various artifacts from a keyboard definition."""

from absl import app, flags

from kbtb.keyboard import load_keyboard
from kbtb.kicad import polygon_to_kicad_file
from kbtb.pcb import generate_kicad_pcb_file
from kbtb.plate import generate_plate

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum('format', 'main_pcb',
                  ['main_pcb', 'plate_top_pcb', 'plate_bottom_pcb'],
                  'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'main_pcb':
        with open(FLAGS.output, 'wb') as output:
            output.write(generate_kicad_pcb_file(kb))

    elif FLAGS.format == 'plate_top_pcb':
        with open(FLAGS.output, 'wb') as output:
            plate = generate_plate(kb, mounting_holes=False, cutouts=True)
            output.write(polygon_to_kicad_file(plate))

    elif FLAGS.format == 'plate_bottom_pcb':
        with open(FLAGS.output, 'wb') as output:
            plate = generate_plate(kb, mounting_holes=True, cutouts=False)
            output.write(polygon_to_kicad_file(plate))

    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
