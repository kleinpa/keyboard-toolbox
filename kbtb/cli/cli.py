"""Generate various artifacts from a keyboard definition."""

from absl import app, flags

from kbtb.keyboard import load_keyboard, save_keyboard
from kbtb.kicad import polygon_to_kicad_file
from kbtb.pcb import generate_kicad_pcb_file
from kbtb.plate import generate_plate
from kbtb.qmk import make_qmk_header_file
from kbtb.kle import keyboard_to_kle_file

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum(
    'format', 'main_kicad_pcb',
    ['h', 'main_kicad_pcb', 'plate_kicad_pcb', 'kle', 'proto_text'],
    'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'plate_kicad_pcb':
        with open(FLAGS.output, 'wb') as output:
            plate = generate_plate(kb)
            output.write(polygon_to_kicad_file(plate))

    elif FLAGS.format == 'h':
        with open(FLAGS.output, 'wb') as output:
            output.write(make_qmk_header_file(kb))

    elif FLAGS.format == 'main_kicad_pcb':
        with open(FLAGS.output, 'wb') as output:
            output.write(generate_kicad_pcb_file(kb))

    elif FLAGS.format == 'kle':
        with open(FLAGS.output, 'wb') as output:
            output.write(keyboard_to_kle_file(kb))

    elif FLAGS.format == 'proto_text':
        save_keyboard(kb, output_path=FLAGS.output, format='text')

    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
