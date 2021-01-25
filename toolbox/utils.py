from math import atan, atan2, cos, degrees, radians, sin, sqrt
import sys
import shapely
import typing


# Use the first point for origin and second to show orientation
def pose(x, y, r=0):
    return shapely.geometry.multipoint.MultiPoint([(x, y),
                                                   (x + cos(radians(r + 90)),
                                                    y + sin(radians(r + 90)))])


def pose_to_xyr(p):
    return (p[0].x, p[0].y,
            degrees(atan2(p[1].y - p[0].y, p[1].x - p[0].x)) - 90)


def generate_placeholders(kb, keyboard_unit=19.05):
    """Returns a multi-polygon containing the minimum plate to support each key."""
    def placeholder(key):
        x, y, r = key.pose.x, key.pose.y, key.pose.r
        p = shapely.geometry.polygon.Polygon([
            (keyboard_unit / 2, keyboard_unit / 2),
            (keyboard_unit / 2, -keyboard_unit / 2),
            (-keyboard_unit / 2, -keyboard_unit / 2),
            (-keyboard_unit / 2, keyboard_unit / 2),
        ])
        p = shapely.affinity.rotate(p, r)
        p = shapely.affinity.translate(p, x, y)
        return p

    return shapely.geometry.multipolygon.MultiPolygon(
        placeholder(key) for key in kb.keys)


def generate_outline(kb):
    placeholders = generate_placeholders(kb)
    resolution = 64
    return placeholders.buffer(kb.outline_concave,
                               join_style=1,
                               resolution=resolution).buffer(
                                   -kb.outline_concave - kb.outline_convex,
                                   join_style=1,
                                   resolution=resolution).buffer(
                                       kb.outline_convex,
                                       join_style=1,
                                       resolution=resolution)


def controller():
    pass
