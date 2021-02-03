"""Generate switch mounting plate designs."""

import shapely
import shapely.geometry

from toolbox.outline import generate_outline

# Polygon describing the shape of an individual key cutout
cutout_geom_square = shapely.geometry.polygon.Polygon([
    # untested
    (7, 7),
    (7, -7),
    (-7, -7),
    (-7, 7),
])
cutout_geom_mx_alps = shapely.geometry.polygon.Polygon([
    # from https://github.com/swill/kad/blob/62948e9/key.go
    # untested
    (7, -7),
    (7, -6.4),
    (7.8, -6.4),
    (7.8, 6.4),
    (7, 6.4),
    (7, 7),
    (-7, 7),
    (-7, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
    (-7, -6.4),
    (-7, -7),
])
cutout_geom_mx_wings = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    (7, -7),
    (7, -6),
    (7.8, -6),
    (7.8, -2.9),
    (7, -2.9),
    (7, 2.9),
    (7.8, 2.9),
    (7.8, 6),
    (7, 6),
    (7, 7),
    (-7, 7),
    (-7, 6),
    (-7.8, 6),
    (-7.8, 2.9),
    (-7, 2.9),
    (-7, -2.9),
    (-7.8, -2.9),
    (-7.8, -6),
    (-7, -6),
    (-7, -7),
])
cutout_geom_alps = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    # untested
    (7.8, -6.4),
    (7.8, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
])


def generate_hole_shape(center, diameter):
    return center.buffer(diameter / 2)


def generate_cutouts(kb):
    def cutout(key):
        x, y, r = key.pose.x, key.pose.y, key.pose.r
        p = cutout_geom_mx_wings
        p = shapely.affinity.rotate(p, r)
        p = shapely.affinity.translate(p, x, y)
        return p

    return shapely.geometry.multipolygon.MultiPolygon(
        cutout(key) for key in kb.keys)


def generate_plate(kb, mounting_holes=False):
    features = [*(x.exterior for x in generate_cutouts(kb))]
    if mounting_holes:
        features += [
            *(generate_hole_shape(shapely.geometry.Point(h.x, h.y),
                                  kb.hole_diameter).exterior
              for h in kb.hole_positions)
        ]
    outline = generate_outline(kb)
    return shapely.geometry.polygon.Polygon(outline.exterior, holes=features)
