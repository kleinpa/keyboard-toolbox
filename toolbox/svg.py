"""Create svg images from a keyboard definition."""

import xml.etree.ElementTree as ET
import io
from math import sin, cos, atan2, degrees, radians

from toolbox.make_plate import generate_plate


def shape_to_svg_element(shape, props={}, x_scale=1, y_scale=-1):
    return ET.Element(
        "path", {
            "d":
            " M " + " ".join(f"{x_scale*x},{y_scale*y}"
                             for x, y in shape.exterior.coords) + " Z " +
            " ".join((" M " + " ".join(f"{x_scale*x},{y_scale*y}"
                                       for x, y in i.coords) + " Z ")
                     for i in shape.interiors),
            **props,
        })


def shape_to_svg(shape, props={}, x_scale=1, y_scale=-1):
    # Calculate viewbox from shape bounds
    x_min, y_min, x_max, y_max = shape.bounds
    left = min(x_min * x_scale, x_max * x_scale)
    top = min(y_min * y_scale, y_max * y_scale)
    width = abs(x_scale * x_min - x_scale * x_max)
    height = abs(y_scale * y_min - y_scale * y_max)

    # Create the empty svg tree
    root = ET.Element(
        'svg', {
            "viewBox": f"{left} {top} {width} {height}",
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            **props,
        })

    root.append(shape_to_svg_element(shape, x_scale=x_scale, y_scale=y_scale))

    return ET.ElementTree(root)


def keyboard_to_layout_svg_file(kb, add_numbers=True):
    plate = generate_plate(kb)

    x_scale = 1
    y_scale = -1

    # Calculate viewbox from plate bounds
    x_min, y_min, x_max, y_max = plate.bounds
    left = min(x_min * x_scale, x_max * x_scale)
    top = min(y_min * y_scale, y_max * y_scale)
    width = abs(x_scale * x_min - x_scale * x_max)
    height = abs(y_scale * y_min - y_scale * y_max)

    # Create the empty svg tree
    root = ET.Element(
        'svg', {
            "viewBox": f"{left} {top} {width} {height}",
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
        })
    root.append(ET.Comment(f'physical-dimensions: {width} mm by {height} mm'))

    # Add groups for document structure
    g_plate = ET.SubElement(root, "g", {
        "id": "plate",
        "style": "fill: black; fill-rule: evenodd;",
    })
    g_plate = ET.SubElement(g_plate, "g", {"id": "plate"})
    g_keycaps = ET.SubElement(root, "g", {
        "id": "keycaps",
        "style": "fill: white;"
    })

    # Add plate
    ET.SubElement(
        g_plate, "path", {
            "d":
            " M " + " ".join(f"{x_scale*x},{y_scale*y}"
                             for x, y in plate.exterior.coords) + " Z " +
            " ".join((" M " + " ".join(f"{x_scale*x},{y_scale*y}"
                                       for x, y in i.coords) + " Z ")
                     for i in plate.interiors)
        })

    g_plate.append(
        shape_to_svg_element(plate, {"style": "fill: black;"}, x_scale,
                             y_scale))

    for i, key in enumerate(kb.keys):
        x, y = x_scale * key.pose.x, y_scale * key.pose.y
        r = degrees(
            atan2(y_scale * sin(radians(key.pose.r - 90)),
                  x_scale * cos(radians(key.pose.r - 90)))) + 90

        keyboard_unit = 19.05
        margin = keyboard_unit - 18.42
        ET.SubElement(
            g_keycaps, "rect", {
                "width": str(keyboard_unit * key.unit_width - margin),
                "height": str(keyboard_unit * key.unit_height - margin),
                "x": str((keyboard_unit * key.unit_width - margin) / -2),
                "y": str((keyboard_unit * key.unit_height - margin) / -2),
                "rx": "1",
                "transform": f"translate({x} {y}) rotate({r})"
            })
        if add_numbers:
            ET.SubElement(
                g_keycaps, "text", {
                    "style":
                    "fill: black; font-family: sans-serif; font-size: 5;",
                    "transform": f"translate({x} {y}) rotate({180+r}) ",
                    "alignment-baseline": "middle",
                    "text-anchor": "middle",
                }).text = f"{i}"

    f = io.BytesIO()
    ET.ElementTree(root).write(f)
    f.seek(0)
    return f
