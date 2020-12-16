import sys
import xml.etree.ElementTree as ET
from math import cos, radians, sin, sqrt

import shapely
import shapely.geometry

from kicad_utils import kicad_polygon
from layout import cutout_geom
from utils import generate_hole_shape, generate_outline, pose, pose_to_xyr


def generate_cutouts(keys):
    def cutout(key):
        x, y, r = pose_to_xyr(key)
        p = cutout_geom
        p = shapely.affinity.rotate(p, r)
        p = shapely.affinity.translate(p, x, y)
        return p

    return shapely.geometry.multipolygon.MultiPolygon(
        cutout(key) for key in keys)


def generate_plate(kb):
    keys = [pose(k.x, k.y, k.r) for k in kb.key_poses]
    holes = [shapely.geometry.Point(h.x, h.y) for h in kb.hole_positions]
    outline = generate_outline(kb)
    return shapely.geometry.polygon.Polygon(
        outline.exterior,
        holes=[
            *(x.exterior for x in generate_cutouts(keys)),
            *(generate_hole_shape(x, kb.hole_diameter).exterior for x in holes)
        ])


def generate_svg(f, kb):
    keys = [pose(k.x, k.y, k.r) for k in kb.key_poses]

    # Transform geometry into svg coordinate system (top-left origin)
    def page_transform(geom):
        return shapely.affinity.scale(geom, yfact=-1, origin=(0, 0))

    # Generate the outline first to properly set the svg viewbox
    outline = page_transform(generate_outline(kb))
    x_min, y_min, x_max, y_max = outline.bounds

    # Create the empty svg tree
    root = ET.Element(
        'svg', {
            "viewBox":
            f"{x_min-1} {y_min-1} {x_max - x_min + 2} {y_max - y_min + 2}",
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink"
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
    g_holes = ET.SubElement(g_plate, "g", {"id": "holes"})
    g_keycaps = ET.SubElement(root, "g", {
        "id": "keycaps",
        "style": "fill: #73b3d1;"
    })

    # Add outline
    ET.SubElement(
        g_outline, "path", {
            "d":
            " M " + " ".join(f"{x},{y}" for x, y in outline.exterior.coords) +
            " Z " + " ".join((" M " + " ".join(f"{x},{y}"
                                               for x, y in i.coords) + " Z ")
                             for i in outline.interiors)
        })

    # TODO: consider drawing subtle nut over holes
    # # Add holes
    # for hole in generate_hole_shape(kb.holes, hole_diameter):
    #     ET.SubElement(
    #         g_holes, "polygon", {
    #             "points":
    #             " ".join(f"{x},{y}"
    #                      for x, y in page_transform(hole).exterior.coords)
    #         })

    # Add keycap for proofing
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

    for i, key in enumerate(keys):
        x, y, r = pose_to_xyr(page_transform(key))
        ET.SubElement(
            g_keycaps, "use", {
                "xlink:href": "#keycap",
                "transform": f"translate({x} {y}) rotate({r}) "
            })
        ET.SubElement(
            g_keycaps, "text", {
                "style": "fill: black; font-family: sans-serif; font-size: 5;",
                "transform": f"translate({x} {y}) rotate({180+r}) ",
                "alignment-baseline": "middle",
                "text-anchor": "middle",
            }).text = f"{i}"

    tree = ET.ElementTree(root)
    tree.write(f, encoding='unicode')


def generate_dxf(fn, geom):
    import ezdxf
    doc = ezdxf.new()
    doc.header['$INSUNITS'] = 4  # Milimeters
    doc.header['$AUNITS'] = 0  # Degrees
    doc.header['$MEASUREMENT'] = 1  # Measurement Metric
    msp = doc.modelspace()

    msp.add_lwpolyline(geom.exterior.coords)

    for interior in geom.interiors:
        msp.add_lwpolyline(interior.coords)

    doc.write(fn)


def generate_kicad(output_path, geom):
    import pcbnew

    # Transform geometry into kicad coordinate system (top-left origin)
    x_min, y_min, x_max, y_max = shapely.affinity.scale(geom).bounds
    margin = 16

    # block_margin = 48 # TODO: use bounds to set page size

    def page_transform(geom):
        geom = shapely.affinity.scale(geom, yfact=-1, origin=(0, 0))
        geom = shapely.affinity.translate(geom,
                                          xoff=-x_min + margin,
                                          yoff=-y_min + margin)
        return geom

    board = pcbnew.BOARD()

    for x in kicad_polygon(page_transform(geom)):
        board.Add(x)

    board.Save(output_path)
