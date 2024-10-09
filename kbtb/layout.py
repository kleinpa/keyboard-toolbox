"""Helpers to create and modify key arrangments."""

from math import atan, atan2, cos, degrees, radians, sin

import shapely
import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard, Position, Pose


# Use the first point for origin and second to show orientation
def pose(x, y, r=0):
    return shapely.geometry.multipoint.MultiPoint([(x, y),
                                                   (x + cos(radians(r + 90)),
                                                    y + sin(radians(r + 90)))])


def pose_to_xyr(p):
    return (
        p.geoms[0].x, p.geoms[0].y,
        degrees(atan2(p.geoms[1].y - p.geoms[0].y,
                      p.geoms[1].x - p.geoms[0].x)) - 90)


def make_key(x, y, r=0, w=1, h=1):
    k = Keyboard.Key(pose={
        "x": x,
        "y": y,
        "r": r
    },
                     unit_width=w,
                     unit_height=h)
    return k


def rotate_keys(keys, angle):
    for key in keys:
        p = pose(key.pose.x, key.pose.y, key.pose.r)
        p = shapely.affinity.rotate(p, angle / 2, origin=(0, 0))
        x, y, r = pose_to_xyr(p)
        yield make_key(x, y, r)


def between(k1, k2):
    return Position(x=(k1.x + k2.x) / 2, y=(k1.y + k2.y) / 2)


def between_pose(k1, k2):
    return Pose(x=(k1.x + k2.x) / 2, y=(k1.y + k2.y) / 2, r=(k1.r + k2.r) / 2)


def holes_between_keys(keys, hole_map):
    for k1, k2 in hole_map:
        yield between(keys[k1].pose, keys[k2].pose)


def pose_closest_point(outline, point):
    ps = [
        outline.interpolate(
            x + outline.project(shapely.geometry.Point(point.x, point.y)))
        for x in [-.1, 0, .1]
    ]
    return Pose(x=ps[1].x,
                y=ps[1].y,
                r=degrees(atan2(ps[2].y - ps[0].y, ps[2].x - ps[0].x)))


# use project_to_outline
def pose_closest_point(outline, point):
    ps = [
        outline.interpolate(
            x + outline.project(shapely.geometry.Point(point.x, point.y)))
        for x in [-.1, 0, .1]
    ]
    return Pose(x=ps[1].x,
                y=ps[1].y,
                r=degrees(atan2(ps[2].y - ps[0].y, ps[2].x - ps[0].x)))


def project_to_outline(outline, point, offset=0, flip=False):
    outline = shapely.geometry.Polygon(outline).buffer(offset).exterior
    ps = [
        outline.interpolate(
            x + outline.project(shapely.geometry.Point(point.x, point.y)))
        for x in [-.1, 0, .1]
    ]
    return Pose(x=ps[1].x,
                y=ps[1].y,
                r=180 + degrees(atan2(ps[2].y - ps[0].y, ps[2].x - ps[0].x)))


def group_by_row(keys):  # duplicated to matrix.py
    """Split the keys into monotonically increasing sublists of x-position."""
    row = []
    last_x = None
    for key in keys:
        if last_x and key.pose.x < last_x:
            yield row
            row = []
        last_x = key.pose.x
        row.append(key)
    if len(row) > 0: yield row


def generate_placeholders(keys, keyboard_unit=19.05):

    def placeholder(key):
        width = keyboard_unit * key.unit_width
        height = keyboard_unit * key.unit_height
        p = shapely.geometry.polygon.Polygon([
            (width / 2, height / 2),
            (width / 2, -height / 2),
            (-width / 2, -height / 2),
            (-width / 2, height / 2),
        ])
        x, y, r = key.pose.x, key.pose.y, key.pose.r
        return shapely.affinity.translate(shapely.affinity.rotate(p, r), x, y)

    return shapely.geometry.multipolygon.MultiPolygon(
        placeholder(key) for key in keys)


def mirror_keys(keys, middle_space=0, only_flip=False):
    keys = list(keys)
    x_min, y_min, _, _ = generate_placeholders(keys).bounds

    row = []
    for row in group_by_row(keys):
        full_row = []
        for key in row:
            p = pose(key.pose.x, key.pose.y, key.pose.r)
            p = shapely.affinity.translate(p,
                                           xoff=-x_min + middle_space / 2,
                                           yoff=-y_min)
            p2 = shapely.affinity.scale(p, -1, origin=(0, 0))
            full_row.insert(0, make_key(*pose_to_xyr(p2)))
            if not only_flip: full_row.append(make_key(*pose_to_xyr(p)))

        yield from full_row


def grid(col,
         row=0,
         arc_radius=0,
         x_offset=0,
         y_offset=0,
         pitch=19.05,
         arc_base_row=0,
         arc_base_col=2):
    if arc_radius == 0:
        return make_key(col * pitch + x_offset, row * pitch + y_offset)
    else:
        n = arc_base_col - col
        geom = pose(arc_base_col * pitch + x_offset, row * pitch + y_offset)
        about = shapely.affinity.translate(geom.geoms[0],
                                           yoff=-pitch / 2 - arc_radius -
                                           (row - arc_base_row) * pitch)
        geom = shapely.affinity.rotate(geom,
                                       n * 2 * atan(pitch / 2 / arc_radius),
                                       use_radians=True,
                                       origin=about)

        x, y, r = pose_to_xyr(geom)
        return make_key(x, y, r)


def shapely_round(shape, radius_convex, radius_concave, resolution=64):
    shape = shape.buffer(radius_concave, resolution=resolution)
    shape = shape.buffer(-radius_concave - radius_convex,
                         resolution=resolution)
    shape = shape.buffer(radius_convex, resolution=resolution)
    return shape
