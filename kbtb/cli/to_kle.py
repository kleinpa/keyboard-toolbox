"""Generate various artifacts from a keyboard definition."""

from absl import app, flags

from kbtb.keyboard import load_keyboard
from kbtb.kle import keyboard_to_kle_file

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum('format', 'kle', ['kle'], 'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'kle':
        with open(FLAGS.output, 'w') as output:
            output.write(keyboard_to_kle_file(kb))

    else:
        raise ValueError("unknown --format value")

if __name__ == "__main__":
    app.run(main)
