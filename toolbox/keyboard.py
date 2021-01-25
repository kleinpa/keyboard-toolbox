"""Utilities for keyboard.proto."""

import sys
from google.protobuf import text_format

from toolbox.keyboard_pb2 import Keyboard


def save_keyboard(kb, output_path=None, format='text'):
    if format == 'bin':
        if output_path:
            with open(output_path, 'wb') as fp:
                fp.write(kb.SerializeToString())
        else:
            raise RuntimeError("will not write binary proto to stdout")
    elif format == 'text':
        if output_path:
            with open(output_path, 'w') as fp:
                sys.stdout.write(text_format.MessageToString(kb))
        else:
            sys.stdout.write(text_format.MessageToString(kb))
    else:
        raise RuntimeError(f"unknown format: {format}")


def load_keyboard(input_path, format='text'):
    with open(input_path, "rb") as fn:
        kb = Keyboard()
        kb.ParseFromString(fn.read())
        return kb


def make_key(x, y, r=0, w=1, h=1):
    k = Keyboard.Key(pose={
        "x": x,
        "y": y,
        "r": r
    },
                     unit_width=w,
                     unit_height=h)
    return k
