"""Helpers to create and modify key arrangments."""
import shapely
import shapely.geometry

from math import atan, atan2, cos, degrees, radians, sin, sqrt

from toolbox.keyboard import make_key
from toolbox.keyboard_pb2 import Keyboard, Position
from toolbox.utils import pose, pose_to_xyr, generate_placeholders


def rotate_keys(keys, angle):
    for key in keys:
        p = pose(key.pose.x, key.pose.y, key.pose.r)
        p = shapely.affinity.rotate(p, angle / 2, origin=(0, 0))
        x, y, r = pose_to_xyr(p)
        yield make_key(x, y, r)


def holes_between_keys(keys, hole_map):
    for k1, k2 in hole_map:
        yield shapely.geometry.Point((keys[k1].pose.x + keys[k2].pose.x) / 2,
                                     (keys[k1].pose.y + keys[k2].pose.y) / 2)


def between(k1, k2):
    return Position(x=(k1.x + k2.x) / 2, y=(k1.y + k2.y) / 2)


def rows(keys):
    """Split the keys into monotonically increasing sublists of x-position"""
    row = []
    last_x = None
    for key in keys:
        if last_x and key.pose.x < last_x:
            yield row
            row = []
        last_x = key.pose.x
        row.append(key)
    if len(row) > 0: yield row


def generate_key_placeholders(keys, keyboard_unit=19.05):
    def placeholder(key):
        p = shapely.geometry.polygon.Polygon([
            (keyboard_unit / 2, keyboard_unit / 2),
            (keyboard_unit / 2, -keyboard_unit / 2),
            (-keyboard_unit / 2, -keyboard_unit / 2),
            (-keyboard_unit / 2, keyboard_unit / 2),
        ])
        x, y, r = key.pose.x, key.pose.y, key.pose.r
        return shapely.affinity.translate(shapely.affinity.rotate(p, r), x, y)

    return shapely.geometry.multipolygon.MultiPolygon(
        placeholder(key) for key in keys)


def mirror_keys(keys, middle_space=0, only_flip=False):
    keys = list(keys)
    x_min, y_min, _, _ = generate_key_placeholders(keys).bounds

    row = []
    for row in rows(keys):
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
        about = shapely.affinity.translate(geom[0],
                                           yoff=-pitch / 2 - arc_radius -
                                           (row - arc_base_row) * pitch)
        geom = shapely.affinity.rotate(geom,
                                       n * 2 * atan(pitch / 2 / arc_radius),
                                       use_radians=True,
                                       origin=about)

        x, y, r = pose_to_xyr(geom)
        return make_key(x, y, r)
