import itertools

import keyboard_pb2


def make_matrix(kb, io):
    matrix = {}

    # available = list(itertools.product(range(io // 2), range(io // 2, io)))
    # for i, (key, m) in enumerate(zip(kb.key_poses, available)):
    #     matrix[i] = m

    # TODO: un-hardcode
    row_nets = (0, 7, 8, 9)
    col_nets = (17, 16, 15, 14, 13, 12, 11, 10, 6, 5, 4, 3)
    matrix = {
        i: (row_nets[i // 12], col_nets[(i % 12) + (3 if i // 12 == 3 else 0)])
        for i in range(42)
    }

    return matrix
