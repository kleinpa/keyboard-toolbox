"""Create physical outlines for keyboards."""

from kbtb.keyboard_pb2 import Keyboard
from kbtb.layout import generate_placeholders, shapely_round


def generate_outline_tight(kb,
                           outline_convex=1.5,
                           outline_concave=80,
                           resolution=64):
    placeholders = generate_placeholders(kb.keys)
    return shapely_round(placeholders,
                         outline_convex,
                         outline_concave,
                         resolution=resolution).exterior


def generate_outline_convex_hull(kb, resolution=64, corner_radius=1.5):
    placeholders = generate_placeholders(kb.keys)
    return shapely_round(placeholders.convex_hull,
                         corner_radius,
                         corner_radius,
                         resolution=resolution).exterior


def generate_outline_rectangle(kb, resolution=64, corner_radius=1.5):
    placeholders = generate_placeholders(kb.keys)
    if corner_radius == 0:
        return placeholders.envelope.exterior
    else:
        return shapely_round(placeholders.envelope,
                             corner_radius,
                             corner_radius,
                             resolution=resolution).exterior
