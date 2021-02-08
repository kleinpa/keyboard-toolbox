"""Generate keyboard artifacts as-needed from a web server."""

import glob
import json
import os

from absl import app, flags
from flask import Flask, make_response, redirect, render_template, send_file

from google.protobuf import text_format
from kbtb.dxf import polygon_to_dxf_file
from kbtb.keyboard import load_keyboard
from kbtb.kicad import polygon_to_kicad_file
from kbtb.kle import keyboard_to_kle, keyboard_to_kle_file
from kbtb.pcb import generate_kicad_pcb_file
from kbtb.plate import generate_plate
from kbtb.qmk import make_qmk_header_file
from kbtb.svg import keyboard_to_layout_svg, svg_to_file


def find_keyboards():
    keyboard_files = glob.glob("kbtb/testdata/*.pb")
    for f in keyboard_files:
        kb = load_keyboard(f)
        yield (kb.name, kb)


keyboards = dict(find_keyboards())

flask_app = Flask(__name__,
                  template_folder=os.path.join(os.getcwd(), "kbtb", "service",
                                               "templates"))


@flask_app.route('/')
def index():
    return render_template('index.html', keyboards=keyboards.values())


@flask_app.route('/kb/<name>/svg')
def render_layout_svg_file(name=None):
    return send_file(svg_to_file(keyboard_to_layout_svg(keyboards[name])),
                     mimetype='image/svg+xml',
                     as_attachment=False,
                     attachment_filename=f'{name}.svg')


@flask_app.route('/kb/<name>/textproto')
def render_proto_text(name=None):
    x = text_format.MessageToString(keyboards[name])
    r = make_response(x)
    r.mimetype = 'text/plain'
    r.attachment_filename = f'{name}.textproto'
    return r


@flask_app.route('/kb/<name>/qmk')
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
    return send_file(polygon_to_kicad_file(plate),
                     mimetype='application/x-kicad-pcb',
                     as_attachment=True,
                     attachment_filename=f'{name}-plate.kicad_pcb')


@flask_app.route('/kb/<name>/plate_gerber')
def render_plate_gerber_file(name=None):
    plate = generate_plate(keyboards[name])
    plate_kicad_file = polygon_to_kicad_file(plate)
    return send_file(polygon_to_kicad_file(plate),
                     mimetype='application/x-kicad-pcb',
                     as_attachment=True,
                     attachment_filename=f'{name}-plate.kicad_pcb')


@flask_app.route('/kb/<name>/plate-dxf')
def render_dxf_file(name=None):
    plate = generate_plate(keyboards[name])
    return send_file(polygon_to_dxf_file(plate),
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
