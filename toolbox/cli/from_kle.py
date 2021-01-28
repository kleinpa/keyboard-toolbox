import sys
import json

from absl import app, flags

from toolbox.keyboard import save_keyboard
from toolbox.kle_utils import kle_to_keyboard

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', None, 'Output path.')
flags.DEFINE_enum('format', 'bin', ['bin', 'text'], 'Protobuf output format.')


def main(argv):
    with open(FLAGS.input, "rb") as fp:
        kle_json = json.load(fp)

    kb = kle_to_keyboard(kle_json)

    save_keyboard(kb, FLAGS.output, FLAGS.format)


if __name__ == "__main__":
    app.run(main)
