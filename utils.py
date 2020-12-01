from math import atan, atan2, cos, degrees, radians, sin, sqrt
import sys
import shapely
import typing


class Keyboard(typing.NamedTuple):
    keys: str
    holes: int


# Polygon describing the required plate area under each key
placeholder_geom = shapely.geometry.polygon.Polygon([
    (9.525, 9.525),
    (9.525, -9.525),
    (-9.525, -9.525),
    (-9.525, 9.525),
])


def generate_placeholders(keys):
    def placeholder(key):
        x, y, r = pose_to_xyr(key)
        p = placeholder_geom
        p = shapely.affinity.rotate(p, r)
        p = shapely.affinity.translate(p, x, y)
        return p

    return shapely.geometry.multipolygon.MultiPolygon(
        placeholder(key) for key in keys)


# Use the first point for origin and second to show orientation
def pose(x, y, r=0):
    return shapely.geometry.multipoint.MultiPoint([(x, y),
                                                   (x + cos(radians(r + 90)),
                                                    y + sin(radians(r + 90)))])


def pose_to_xyr(pose):
    return (pose[0].x, pose[0].y,
            degrees(atan2(pose[1].y - pose[0].y, pose[1].x - pose[0].x)) - 90)


def rotate_keys(keys, angle):
    for key in keys:
        yield shapely.affinity.rotate(key, angle / 2, origin=(0, 0))


# Split the keys by x-value into monotonically increasing sublists
def rows(keys):
    row = []
    last_x = None
    for key in keys:
        x, y, r = pose_to_xyr(key)
        if last_x and x < last_x:
            yield row
            row = []
        last_x = x
        row.append(key)

    if len(row) > 0: yield row


def mirror_keys(keys, middle_space):
    keys = list(keys)
    x_min, y_min, _, _ = generate_placeholders(keys).bounds

    row = []
    last_x = None
    for row in rows(keys):
        full_row = []
        for key in row:
            key = shapely.affinity.translate(key,
                                             xoff=-x_min + middle_space / 2,
                                             yoff=-y_min)
            mirror_key = shapely.affinity.scale(key, -1, origin=(0, 0))
            full_row.insert(0, mirror_key)
            full_row.append(key)

        yield from full_row


def generate_outline(keys, fill, round, pad):
    placeholders = generate_placeholders(keys)
    return placeholders.buffer(fill, join_style=1).buffer(-fill - round,
                                                          join_style=1).buffer(
                                                              round + pad,
                                                              join_style=1)


def holes_between_keys(keys, hole_map):
    for k1, k2 in hole_map:
        x1, y1, _ = pose_to_xyr(keys[k1])
        x2, y2, _ = pose_to_xyr(keys[k2])
        yield shapely.geometry.Point((x1 + x2) / 2, (y1 + y2) / 2)


def generate_hole_shape(hole, diameter):
    return hole.buffer(diameter / 2)
