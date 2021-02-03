"""Helpers for working with keyboard.proto data."""

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


def load_keyboard(input_path):
    with open(input_path, "rb") as fn:
        kb = Keyboard()
        kb.ParseFromString(fn.read())
        return kb
