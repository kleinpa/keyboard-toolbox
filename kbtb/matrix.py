"""Generate keyboard matrices for keyboard definitions."""

import itertools
import random


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
