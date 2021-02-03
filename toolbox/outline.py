"""Create physical outlines for keyboards."""

from toolbox.keyboard_pb2 import Keyboard
from toolbox.layout import generate_placeholders


def generate_outline_tight(kb, resolution=64):
    placeholders = generate_placeholders(kb.keys)
    x = placeholders
    x = x.buffer(kb.outline_concave, resolution=resolution)
    x = x.buffer(-kb.outline_concave - kb.outline_convex,
                 resolution=resolution)
    x = x.buffer(kb.outline_convex, resolution=resolution)
    return x


def generate_outline_rectangle(kb, resolution=64, corner_radius=1.5):
    placeholders = generate_placeholders(kb.keys)
    x = placeholders.envelope
    x = x.buffer(-corner_radius, resolution=resolution)
    x = x.buffer(corner_radius, resolution=resolution)
    return x


def generate_outline(kb):
    if kb.outline == Keyboard.OUTLINE_TIGHT:
        return generate_outline_tight(kb)
    elif kb.outline == Keyboard.OUTLINE_RECTANGLE:
        return generate_outline_rectangle(kb)
    else:
        raise RuntimeError(f"unknown outline type")
