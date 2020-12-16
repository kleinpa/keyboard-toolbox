from math import atan, atan2, cos, degrees, radians, sin, sqrt
import sys
import shapely
import typing


# Use the first point for origin and second to show orientation
def pose(x, y, r=0):
    return shapely.geometry.multipoint.MultiPoint([(x, y),
                                                   (x + cos(radians(r + 90)),
                                                    y + sin(radians(r + 90)))])


def pose_to_xyr(pose):
    return (pose[0].x, pose[0].y,
            degrees(atan2(pose[1].y - pose[0].y, pose[1].x - pose[0].x)) - 90)


# Polygon describing the required plate area under each key
key_placeholder = shapely.geometry.polygon.Polygon([
    (9.525, 9.525),
    (9.525, -9.525),
    (-9.525, -9.525),
    (-9.525, 9.525),
])


def generate_placeholders(kb):
    keys = [pose(k.x, k.y, k.r) for k in kb.key_poses]

    def placeholder(key):
        x, y, r = pose_to_xyr(key)
        p = key_placeholder
        p = shapely.affinity.rotate(p, r)
        p = shapely.affinity.translate(p, x, y)
        return p

    return shapely.geometry.multipolygon.MultiPolygon(
        placeholder(key) for key in keys)


def generate_outline(kb):
    placeholders = generate_placeholders(kb)
    return placeholders.buffer(kb.outline_concave,
                               join_style=1).buffer(
                                   -kb.outline_concave - kb.outline_convex,
                                   join_style=1).buffer(kb.outline_convex,
                                                        join_style=1)


def generate_hole_shape(hole, diameter):
    return hole.buffer(diameter / 2)


def controller():
    pass
