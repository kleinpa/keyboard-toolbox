"""Generate C++ headers for use in QMK firmware."""

import io
import json

from kbtb.keyboard_pb2 import Keyboard


def make_qmk_info_file(kb):
    data = {}

    if kb.name: data['keyboard_name'] = kb.name
    if kb.url: data['url'] = kb.url

    data['usb'] = {'pid': '0x23B0', 'device_ver': '0x0001'}

    # TODO: generalize...

    if kb.controller == Keyboard.CONTROLLER_PROMICRO:
        data['processor'] = 'atmega32u4'
        data['bootloader'] = 'atmel-dfu'
        data['diode_direction'] = 'COL2ROW'
        pin_names = [
            'D3', 'D2', 'D1', 'D0', 'D4', 'C6', 'D7', 'E6', 'B4', 'B5', 'B6',
            'B2', 'B3', 'B1', 'F7', 'F6', 'F5', 'F4'
        ]
    elif kb.controller == Keyboard.CONTROLLER_ATMEGA32U4:
        data['processor'] = 'atmega32u4'
        data['bootloader'] = 'atmel-dfu'
        data['diode_direction'] = 'COL2ROW'
        pin_names = [
            'B0',
            'B7',
            'D0',
            'D1',
            'D2',
            'D3',
            'D5',
            'D4',
            'D6',
            'D7',
            'B4',
            'B5',
            'B6',
            'C6',
            'C7',
            'F7',
            'F6',
            'F5',
            'F4',
            'F1',
            'F0',
            'E6',
        ]
    elif kb.controller == Keyboard.CONTROLLER_ATMEGA328:
        data['processor'] = 'atmega328p'
        data['bootloader'] = 'USBasp'
        data['diode_direction'] = 'COL2ROW'
        pin_names = [
            "D0",
            "D1",
            "D4",
            "D6",
            "D7",
            "B0",
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "C0",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
        ]
    else:
        raise RuntimeError(f'unknown controller: {kb.controller}')

    data['features'] = {
        "backlight": False,
        "command": False,
        "console": False,
        "extrakey": False,
        "midi": False,
        "mousekey": False,
        "nkro": False,
        "rgblight": False,
        "unicode": False
    }

    # Build sets of row and column controller pin indices
    rows = sorted(set(k.controller_pin_low for k in kb.keys))
    cols = sorted(set(k.controller_pin_high for k in kb.keys))

    # Sanity check the controller pins
    if set(rows) & set(cols):
        raise RuntimeError(
            f'pin in both row and column list rows={rows} cols={cols}')
    if not set(rows).issubset(range(len(pin_names))):
        raise RuntimeError(f'rows contains out-of-range pin rows={rows}')
    if not set(cols).issubset(range(len(pin_names))):
        raise RuntimeError(f'Rows contains out-of-range pin cols={cols}')
    if len(
            set((k.controller_pin_low, k.controller_pin_high)
                for k in kb.keys)) != len(kb.keys):
        raise RuntimeError(f'controller pin index assignments not unique')

    data['width'] = len(cols)
    data['height'] = len(rows)
    data['key_count'] = len(kb.keys)
    data['matrix_pins'] = {
        'cols': list(pin_names[x] for x in cols),
        'rows': list(pin_names[x] for x in rows)
    }

    ku = 19.05
    min_x = min(k.pose.x for k in kb.keys)
    min_y = min(k.pose.y for k in kb.keys)

    def make_layout(key):
        data = {}
        data['matrix'] = [
            rows.index(key.controller_pin_low),
            cols.index(key.controller_pin_high)
        ]
        if key.unit_width != 1: data['w'] = key.unit_width
        if key.unit_height != 1: data['h'] = key.unit_height
        if key.pose.r != 0: data['r'] = key.pose.r
        data['x'] = (key.pose.x - min_x) / ku
        data['y'] = (key.pose.y - min_y) / ku

        return data

    if kb.qmk.layout and kb.qmk.layout_sequence:
        data["community_layouts"] = [kb.qmk.layout]
        data['layouts'] = {
            f'LAYOUT_{kb.qmk.layout}': {
                'key_count': len(kb.qmk.layout_sequence),
                'layout':
                [make_layout(kb.keys[i]) for i in kb.qmk.layout_sequence]
            }
        }
    elif kb.qmk.layout and not kb.qmk.layout_sequence:
        data["community_layouts"] = [kb.qmk.layout]
        data['layouts'] = {
            f'LAYOUT_{kb.qmk.layout}': {
                'key_count': len(kb.keys),
                'layout': [make_layout(k) for k in kb.keys]
            }
        }
    return json.dumps(data, indent=2)
