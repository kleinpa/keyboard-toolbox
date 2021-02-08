"""Create physical outlines for keyboards."""

from kbtb.keyboard_pb2 import Keyboard
from kbtb.layout import generate_placeholders


def shapely_round(shape, radius_convex, radius_concave, resolution=64):
    shape = shape.buffer(radius_concave, resolution=resolution)
    shape = shape.buffer(-radius_concave - radius_convex,
                         resolution=resolution)
    shape = shape.buffer(radius_convex, resolution=resolution)
    return shape


def generate_outline_tight(kb, resolution=64):
    placeholders = generate_placeholders(kb.keys)
    return shapely_round(placeholders,
                         kb.outline_convex,
                         kb.outline_concave,
                         resolution=resolution).exterior


def generate_outline_convex_hull(kb, resolution=64, corner_radius=1.5):
    placeholders = generate_placeholders(kb.keys)
    return shapely_round(placeholders.convex_hull,
                         corner_radius,
                         corner_radius,
                         resolution=resolution).exterior


def generate_outline_rectangle(kb, resolution=64, corner_radius=1.5):
    placeholders = generate_placeholders(kb.keys)
    return shapely_round(placeholders.envelope,
                         corner_radius,
                         corner_radius,
                         resolution=resolution).exterior


def generate_outline(kb):
    if kb.outline == Keyboard.OUTLINE_TIGHT:
        return generate_outline_tight(kb)
    elif kb.outline == Keyboard.OUTLINE_CONVEX_HULL:
        return generate_outline_convex_hull(kb)
    elif kb.outline == Keyboard.OUTLINE_RECTANGLE:
        return generate_outline_rectangle(kb)
    else:
        raise RuntimeError(f"unknown outline type")
