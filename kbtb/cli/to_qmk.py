"""Generate various artifacts from a keyboard definition."""

from absl import app, flags

from kbtb.keyboard import load_keyboard
from kbtb.qmk import make_qmk_info_file

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum('format', 'qmk', ['qmk'], 'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'qmk':
        with open(FLAGS.output, 'w') as output:
            output.write(make_qmk_info_file(kb))

    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
