import xml.etree.ElementTree as ET
import io
from math import sin, cos, atan2, degrees, radians

from toolbox.utils import generate_outline, pose, pose_to_xyr
from toolbox.make_plate import generate_plate


def keyboard_to_layout_svg_file(kb, add_numbers=False):

    # Generate the outline first to properly set the svg viewbox
    outline = generate_plate(kb)
    x_min, y_min, x_max, y_max = outline.bounds

    x_scale = 1
    y_scale = -1

    # Create the empty svg tree
    root = ET.Element(
        'svg', {
            "viewBox":
            f"{min(x_min*x_scale,x_max*x_scale)} {min(y_min*y_scale,y_max*y_scale)} {abs(x_scale*(x_max - x_min))} {abs(y_scale*(y_max - y_min))}",
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
        })
    root.append(
        ET.Comment(
            f'physical-dimensions: {x_max-x_min} mm by {y_max-y_min} mm'))
    defs = ET.SubElement(root, "defs")

    # Add groups for document structure
    g_plate = ET.SubElement(root, "g", {
        "id": "plate",
        "style": "fill: black; fill-rule: evenodd;",
    })
    g_outline = ET.SubElement(g_plate, "g", {"id": "outline"})
    g_keycaps = ET.SubElement(root, "g", {
        "id": "keycaps",
        "style": "fill: white;"
    })

    # Add outline
    ET.SubElement(
        g_outline, "path", {
            "d":
            " M " + " ".join(f"{x_scale*x},{y_scale*y}"
                             for x, y in outline.exterior.coords) + " Z " +
            " ".join((" M " + " ".join(f"{x_scale*x},{y_scale*y}"
                                       for x, y in i.coords) + " Z ")
                     for i in outline.interiors)
        })

    # Add keycap
    g_keycap = ET.SubElement(
        defs,
        "g",
        {
            "id": "keycap",
        },
    )
    ET.SubElement(
        g_keycap, "rect", {
            "width": "18.3",
            "height": "18.3",
            "x": "-9.15",
            "y": "-9.15",
            "rx": "1.5",
        })

    for i, key in enumerate(kb.keys):
        x, y = x_scale * key.pose.x, y_scale * key.pose.y
        r = degrees(
            atan2(y_scale * sin(radians(key.pose.r - 90)),
                  x_scale * cos(radians(key.pose.r - 90)))) + 90

        keyboard_unit = 19.05
        margin = keyboard_unit - 18.3
        ET.SubElement(
            g_keycaps, "use", {
                "xlink:href": "#keycap",
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
