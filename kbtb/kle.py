"""Convert between keyboard.proto and the mildly-archaic kle syntax.

keyboard.proto uses math-inspired coordinates, with +x rightwards, +y
upwards, and +r counterclockwise, with all units in milimeters.

The kle format uses +x rightwards, +y downwards, +r clockwise and has all
dimensions in terms of keyboard units.

Additional nuances in the kle syntax:
- Rotation about top left of key
- Key origin for tall keys at top left of key
- All positions are based on the position of the last key. Rotation is
    persisted but not cumulative.

When in doubt read the code:
https://github.com/ijprest/kle-serial/blob/master/index.ts
"""

import io
import json
from math import sin, cos, radians, isclose

from kbtb.keyboard_pb2 import Keyboard
from kbtb.layout import group_by_row, generate_placeholders
from kbtb.outline import generate_outline_tight, generate_outline_convex_hull, generate_outline_rectangle
from kbtb.matrix import fill_matrix_rows


def kle_position(key, keyboard_unit=19.05, x0=0, y0=0):
    x, y, r = key.pose.x, key.pose.y, key.pose.r

    # switch to inverted coordinates and move origin to top
    x = (x - x0)
    y = -(y - y0)

    # find top-left of key
    height = key.unit_height * keyboard_unit
    x = x + sin(radians(r - 180)) * height / 2
    y = y + cos(radians(r - 180)) * height / 2
    width = key.unit_width * keyboard_unit
    x = x + sin(radians(r - 90)) * width / 2
    y = y + cos(radians(r - 90)) * width / 2

    # determine un-rotated position
    x2 = x * cos(radians(r)) - y * sin(radians(r))
    y2 = y * cos(radians(r)) + x * sin(radians(r))

    return (x2 / keyboard_unit, y2 / keyboard_unit, -r, key.unit_width,
            key.unit_height)


def keyboard_to_kle(kb, keyboard_unit=19.05):
    x_min, y_min, x_max, y_max = generate_placeholders(kb.keys).bounds

    kle_metadata = {
        "name": kb.name,
    }

    kle_data = [
        kle_metadata,
    ]

    # state for KLE's relative positioning
    current_x, current_y, current_r = 0, 0, 0

    for row in group_by_row(kb.keys):
        kle_row = []

        for key in row:
            props = {}

            x, y, r, w, h = kle_position(
                key, x0=x_min, y0=y_max, keyboard_unit=keyboard_unit)

            # break row if rotation has changed
            if not isclose(current_r, r, abs_tol=0.00001):
                if kle_row:
                    kle_data.append(kle_row)
                    kle_row = []
                    current_y += 1
                current_x = 0
                current_r = r
                props["r"] = r

            if not isclose(x, current_x, abs_tol=0.00001):
                props["x"] = x - current_x
                current_x = x
            if not isclose(y, current_y, abs_tol=0.00001):
                props["y"] = y - current_y
                current_y = y

            if not isclose(w, 1, abs_tol=0.00001):
                props["w"] = w
            if not isclose(h, 1, abs_tol=0.00001):
                props["h"] = h

            if props: kle_row.append(props)
            kle_row.append("")

            current_x += w

        if kle_row:
            kle_data.append(kle_row)
            kle_row = []
            current_y += 1
        current_x = 0
    return kle_data


def keyboard_to_kle_file(kb, keyboard_unit=19.05):
    kle_data = keyboard_to_kle(kb, keyboard_unit)
    return json.dumps(kle_data)


def kle_param_to_key(x, y, r, rx, ry, w, h, keyboard_unit=19.05):
    x = (x) * keyboard_unit
    y = -(y) * keyboard_unit
    r = -r

    x2 = x * cos(radians(r)) - y * sin(radians(r))
    y2 = y * cos(radians(r)) + x * sin(radians(r))

    x2 += rx * keyboard_unit
    y2 -= ry * keyboard_unit

    height = h * keyboard_unit
    x2 = x2 + sin(radians(-r - 180)) * height / 2
    y2 = y2 + cos(radians(-r - 180)) * height / 2
    width = w * keyboard_unit
    x2 = x2 - sin(radians(-r - 90)) * width / 2
    y2 = y2 - cos(radians(-r - 90)) * width / 2

    return Keyboard.Key(
        pose={
            "x": x2,
            "y": y2,
            "r": r
        }, unit_width=w, unit_height=h)


def add_standard_stabilizers(kb):
    allowed_sizes = [2, 6.25]

    def add(key, size, r, flip):
        if size < min(allowed_sizes):
            return

        key.stabilizer.size = max(x for x in allowed_sizes if x <= size)
        key.stabilizer.r = r
        key.switch_r = r

        if flip:
            key.stabilizer.r += 180

    rows = list(group_by_row(kb.keys))
    for i, row in enumerate(rows):
        last_row = i == len(rows) - 1

        for j, key in enumerate(row):
            last_col = j == len(row) - 1
            if key.unit_width > 1 and key.unit_height == 1:
                add(key, key.unit_width, 0, last_row)
            if key.unit_width == 1 and key.unit_height > 1:
                add(key, key.unit_height, 90, last_col)


def kle_to_keyboard(kle_json,
                    keyboard_unit=19.05,
                    switch=Keyboard.SWITCH_CHERRY_MX,
                    controller=Keyboard.CONTROLLER_STM32F072,
                    outline_type='convex-hull',
                    hole_diameter=2.4,
                    add_stabilizers=True,
                    add_matrix=True,
                    **kb_args):
    kb = Keyboard(
        name="kle-import",
        controller=controller,
        switch=switch,
        hole_diameter=hole_diameter,
        **kb_args)

    # state for KLE's relative positioning
    current_y, current_r, current_rx, current_ry = 0, 0, 0, 0
    props = {}

    for row_or_metadata in kle_json:
        # decal, stepped, x2, y2, w2, h2 are unsupported
        current_x = 0  #current_rx

        props.update({
            # r, rx, ry default unset
            "x": 0,
            "y": 0,
            "w": 1,
            "h": 1,
        })

        if isinstance(row_or_metadata, dict):
            if "name" in row_or_metadata:
                kb.name = row_or_metadata["name"]
            if "kb-toolkit-outline" in row_or_metadata:
                outline_type = row_or_metadata["kb-toolkit-outline"]
        else:
            for key_or_props in row_or_metadata:
                if isinstance(key_or_props, dict):
                    props.update(key_or_props)
                    if "r" in props:
                        current_r = props["r"]
                    if "rx" in key_or_props:
                        current_rx = props["rx"]
                        current_x = 0
                        current_y = 0
                    if "ry" in key_or_props:
                        current_ry = props["ry"]
                        current_y = 0
                else:
                    current_x += props["x"]
                    current_y += props["y"]
                    width = props["w"]
                    height = props["h"]

                    kb.keys.append(
                        kle_param_to_key(
                            x=current_x,
                            y=current_y,
                            r=current_r,
                            rx=current_rx,
                            ry=current_ry,
                            w=width,
                            h=height,
                            keyboard_unit=keyboard_unit))

                    current_x += width
                    props.update({
                        "x": 0,
                        "y": 0,
                        "w": 1,
                        "h": 1,
                    })

            current_y += 1

    # generate outline polygon
    if outline_type == 'tight':
        outline = generate_outline_tight(kb)
    elif outline_type == 'convex-hull':
        outline = generate_outline_convex_hull(kb)
    elif outline_type == 'rectangle':
        outline = generate_outline_rectangle(kb)
    else:
        raise RuntimeError(f"unknown outline type: {outline_type}")

    for x, y in outline.coords:
        kb.outline_polygon.add(x=x, y=y)

    if add_stabilizers:
        add_standard_stabilizers(kb)

    if add_matrix:
        fill_matrix_rows(kb)

    return kb
