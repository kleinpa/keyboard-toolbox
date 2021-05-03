"""A basic example keyboard layout used for testing."""

from absl import app, flags

from kbtb.keyboard_pb2 import Keyboard
from kbtb.layout import between, between_pose, pose_closest_point, mirror_keys, rotate_keys, grid
from kbtb.matrix import fill_matrix
from kbtb.outline import generate_outline_tight

FLAGS = flags.FLAGS
flags.DEFINE_string('output', '', 'Output path')


def test_layout():
    kb = Keyboard(
        name="test-layout",
        controller=Keyboard.CONTROLLER_PROMICRO,
        footprint=Keyboard.FOOTPRINT_CHERRY_MX,

        # Plate parameters
        hole_diameter=2.4,
    )

    rows = 4

    pitch = 19.05
    column_offsets = [-1, 0, 1, 0, -1, -2]
    keys = [
        *(grid(x, row, y_offset=column_offsets[x])
          for row in range(rows - 1, 0, -1) for x in range(6)),
        *(grid(x,
               0,
               arc_radius=120,
               x_offset=-1 / 3 * pitch,
               y_offset=column_offsets[1]) for x in range(3)),
    ]

    for key in mirror_keys(rotate_keys(keys, angle=19), middle_space=0):
        kb.keys.append(key)
    kb.hole_positions.extend([
        between(kb.keys[0].pose, kb.keys[13].pose),
        between(kb.keys[11].pose, kb.keys[22].pose),
        between(kb.keys[4].pose, kb.keys[17].pose),
        between(kb.keys[7].pose, kb.keys[18].pose),
        between(kb.keys[25 + (rows - 5) * 12].pose,
                kb.keys[36 + (rows - 5) * 12].pose),
        between(kb.keys[35 + (rows - 5) * 12].pose,
                kb.keys[46 + (rows - 5) * 12].pose),
        between(kb.keys[41 + (rows - 5) * 12].pose,
                kb.keys[50 + (rows - 5) * 12].pose),
        between(kb.keys[42 + (rows - 5) * 12].pose,
                kb.keys[51 + (rows - 5) * 12].pose)
    ])
    kb.controller_pose.CopyFrom(kb.keys[8].pose)
    fill_matrix(kb)

    outline = generate_outline_tight(
        kb,
        outline_concave=120,
        outline_convex=1.5,
    ).simplify(0.001)

    for x, y in outline.coords:
        kb.outline_polygon.add(x=x, y=y)

    return kb


def main(argv):
    kb = test_layout()

    with open(FLAGS.output, 'wb') as fn:
        fn.write(kb.SerializeToString())


if __name__ == "__main__":
    app.run(main)
