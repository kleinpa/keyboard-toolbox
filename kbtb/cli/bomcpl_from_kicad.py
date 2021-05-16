"""Convert a .kicad_pcb file into a gerber archive ready for manufacturing."""

import shutil

from absl import app, flags

from kbtb.kicad import bomcpl_from_kicad

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Path to .kicad_pcb file')
flags.DEFINE_string('output', '', 'Path to write .zip file containing gerbers')


def main(argv):
    with open(FLAGS.input, "rb") as fp:
        kicad_file = fp.read()
        gerber_archive = bomcpl_from_kicad(kicad_file)
    with open(FLAGS.output, "wb") as fp:
        fp.write(gerber_archive)


if __name__ == "__main__":
    app.run(main)
