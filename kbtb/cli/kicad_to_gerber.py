"""Convert a .kicad_pcb file into a gerber archive ready for manufacturing."""

import shutil

from absl import app, flags

from kbtb.kicad import kicad_file_to_gerber_archive_file

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Path to .kicad_pcb file')
flags.DEFINE_string('output', '', 'Path to write .zip file containing gerbers')


def main(argv):
    with open(FLAGS.input, "rb") as fp:
        output = kicad_file_to_gerber_archive_file(fp)
    with open(FLAGS.output, "wb") as fp:
        shutil.copyfileobj(output, fp)


if __name__ == "__main__":
    app.run(main)
