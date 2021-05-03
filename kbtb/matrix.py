"""Generate keyboard matrices for keyboard definitions."""

import itertools
import random


def group_by_row(keys):  # duplicated from layout.py
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


def fill_matrix(kb, io=18):
    """Generates an unoptomized keyboard matrix for the provided keyboard.

    Populate the controller_pin_* fields with a simple matrix that
    splits the IO pins evenly into rows and columns then sequentially
    assigns keys to that matrix. This is really only suitable for
    playing around with designs.
    """
    available = list(itertools.product(range(io // 2), range(io // 2, io)))
    for key, (low, high) in zip(kb.keys, available):
        key.controller_pin_low = low
        key.controller_pin_high = high


def fill_matrix_rows(kb, io=18):
    """Generates an unoptomized keyboard matrix for the provided keyboard.

    Populate the controller_pin_* fields with a simple matrix that
    splits the IO pins evenly into rows and columns then sequentially
    assigns keys to that matrix. This is really only suitable for
    playing around with designs.
    """
    rows = list(group_by_row(kb.keys))
    row_count = len(rows)
    col_count = max(len(col) for col in rows)

    if row_count + col_count > io:
        raise RuntimeError(
            f"unable to build matrix: {row_count+col_count} pins needed but only {io} available"
        )

    for row, keys in enumerate(rows):
        for col, key in enumerate(keys):
            key.controller_pin_low = row
            key.controller_pin_high = len(rows) + col


def fill_matrix_random(kb, io=18):
    """Generates a random keyboard matrix for the provided keyboard.

    To demonstrate a worst-case scenario matrix, randomly assign keys to
    positions in the full matrix.
    """
    rnd = random.Random(0)

    available = list(itertools.product(range(io // 2), range(io // 2, io)))
    for key in kb.keys:
        low, high = available.pop(rnd.randrange(len(available)))
        key.controller_pin_low = low
        key.controller_pin_high = high
