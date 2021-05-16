"""Generate preview svg images from a keyboard definition."""

from absl import app, flags

from kbtb.keyboard import load_keyboard
from kbtb.svg import keyboard_to_layout_svg, svg_to_file

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Input path.')
flags.DEFINE_string('output', '', 'Output path.')
flags.DEFINE_enum('format', 'svg', ['svg'], 'Type of output to generate.')


def main(argv):
    kb = load_keyboard(FLAGS.input)

    if FLAGS.format == 'svg':
        with open(FLAGS.output, 'wb') as output:
            output.write(svg_to_file(keyboard_to_layout_svg(kb)))
    else:
        raise ValueError("unknown --format value")


if __name__ == "__main__":
    app.run(main)
