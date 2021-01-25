import itertools

import keyboard_pb2


def fill_matrix(kb, io=18):
    available = list(itertools.product(range(io // 2), range(io // 2, io)))
    for i, (key, (low, high)) in enumerate(zip(kb.keys, available)):
        key.controller_pin_low = low
        key.controller_pin_high = high


def fill_matrix_random(kb, io=18):
    import random

    available = list(itertools.product(range(io // 2), range(io // 2, io)))
    rnd = random.Random(0)
    for i, key in enumerate(kb.keys):
        low, high = available.pop(random.randrange(len(available)))
        key.controller_pin_low = low
        key.controller_pin_high = high
