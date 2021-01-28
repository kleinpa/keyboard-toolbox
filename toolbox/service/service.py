import glob
import io
import json
import os
import tempfile

from absl import app, flags
from flask import Flask, redirect, render_template, send_file
from toolbox.dxf_utils import shape_to_dxf_file
from toolbox.keyboard import load_keyboard
from toolbox.keyboard_pb2 import Keyboard
from toolbox.kicad_utils import shape_to_kicad_file
from toolbox.kle_utils import keyboard_to_kle, keyboard_to_kle_file
from toolbox.make_pcb import generate_kicad_pcb_file
from toolbox.make_plate import generate_plate
from toolbox.qmk_utils import make_qmk_header_file
from toolbox.svg import keyboard_to_layout_svg_file


def find_keyboards():
    keyboard_files = glob.glob("keyboards/*/*.pb") + glob.glob(
        "toolbox/testdata/*.pb")
    for f in keyboard_files:
        with open(f, "rb") as fn:
            kb = Keyboard()
            kb.ParseFromString(fn.read())
            yield (kb.name, kb)


keyboards = dict(find_keyboards())

flask_app = Flask(__name__,
                  template_folder=os.path.join(os.getcwd(), "toolbox",
                                               "service", "templates"))


@flask_app.route('/')
def index():
    return render_template('index.html', keyboards=keyboards.values())


@flask_app.route('/kb/<name>/svg')
def render_layout_svg_file(name=None):
    return send_file(keyboard_to_layout_svg_file(keyboards[name]),
                     mimetype='image/svg+xml',
                     as_attachment=False,
                     attachment_filename=f'{name}.svg')


@flask_app.route('/kb/<name>/qmk_header')
def render_qmk_header_file(name=None):
    return send_file(make_qmk_header_file(keyboards[name]),
                     mimetype='text/plain',
                     as_attachment=False,
                     attachment_filename=f'{name}-config.h')


@flask_app.route('/kb/<name>/kicad_pcb')
def render_kicad_pcb_file(name=None):
    return send_file(generate_kicad_pcb_file(keyboards[name]),
                     mimetype='application/x-kicad-pcb',
                     as_attachment=True,
                     attachment_filename=f'{name}.kicad_pcb')


@flask_app.route('/kb/<name>/plate_kicad_pcb')
def render_plate_kicad_pcb_file(name=None):
    plate = generate_plate(keyboards[name])
    return send_file(shape_to_kicad_file(plate),
                     mimetype='application/x-kicad-pcb',
                     as_attachment=True,
                     attachment_filename=f'{name}-plate.kicad_pcb')


@flask_app.route('/kb/<name>/plate-dxf')
def render_dxf_file(name=None):
    plate = generate_plate(keyboards[name])
    return send_file(shape_to_dxf_file(plate),
                     mimetype='application/dxf',
                     as_attachment=True,
                     attachment_filename=f'{name}-plate.dxf')


@flask_app.route('/kb/<name>/kle')
def render_kle_file(name=None):
    return send_file(keyboard_to_kle_file(keyboards[name]),
                     mimetype='application/json',
                     as_attachment=True,
                     attachment_filename=f'{name}-kle.json')


@flask_app.route('/kb/<name>/kle_redirect')
def render_kle_redirect(name=None):
    kle_data = keyboard_to_kle(keyboards[name])
    kle_json = json.dumps(kle_data, separators=(',', ':'))
    return redirect("http://www.keyboard-layout-editor.com/##" + kle_json,
                    code=302)


def main(argv):
    flask_app.run(port=80, debug=True)


if __name__ == "__main__":
    app.run(main)
