import sys

from kbtb.keyboard import save_keyboard
from kbtb.keyboard_pb2 import Keyboard
from kbtb.layout import holes_between_keys, project_to_outline, mirror_keys, rotate_keys, grid, pose_closest_point, between_pose, pose_closest_point
from kbtb.outline import generate_outline_tight


def main():
    kb = Keyboard(
        name="unisplit42",
        info_text="unisplit42\npeterklein.dev",
        controller=Keyboard.CONTROLLER_ATMEGA32U4,
        switch=Keyboard.SWITCH_CHERRY_MX,
    )

    pitch = 19.05

    column_offsets = [-1.6, 0.0, 8.0, 3.6, -7.68, -10.08]

    keys = [
        *(grid(x, 3, y_offset=column_offsets[x]) for x in range(6)),
        *(grid(x, 2, y_offset=column_offsets[x]) for x in range(6)),
        *(grid(x, 1, y_offset=column_offsets[x]) for x in range(6)),
        *(grid(
            x,
            arc_radius=90,
            x_offset=-0.65 * pitch,
            y_offset=column_offsets[0] + 1) for x in range(3)),
    ]

    for key in mirror_keys(rotate_keys(keys, angle=51)):
        kb.keys.append(key)

    for hole in holes_between_keys(kb.keys,
                                   ((1, 12), (12, 25), (5, 16), (29, 38),
                                    (30, 39), (6, 19), (10, 23), (23, 34))):
        kb.hole_positions.append(hole)

    outline = generate_outline_tight(
        kb,
        outline_concave=80,
        outline_convex=1.5,
    )

    kb.connector_pose.CopyFrom(
        pose_closest_point(outline,
                           between_pose(kb.keys[5].pose, kb.keys[6].pose)))

    kb.controller_pose.CopyFrom(
        between_pose(kb.keys[17].pose, kb.keys[18].pose))

    # TODO: un-hardcode
    row_nets = (0, 5, 6, 7)
    col_nets = list(reversed((1, 2, 3, 4, 8, 9, 10, 11, 12, 13, 14, 15)))
    for i, key in enumerate(kb.keys):
        key.controller_pin_low = row_nets[i // 12]
        key.controller_pin_high = col_nets[(i % 12) +
                                           (3 if i // 12 == 3 else 0)]

    for x, y in outline.coords:
        kb.outline_polygon.add(x=x, y=y)

    kb.info_pose.CopyFrom(
        project_to_outline(
            outline,
            between_pose(kb.keys[25].pose, kb.keys[36].pose),
            offset=-4))

    kb.qmk.layout = "split_3x6_3"
    kb.qmk.layout_sequence[:] = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
        20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
        38, 39, 40, 41
    ]

    with open(sys.argv[1], 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    main()
