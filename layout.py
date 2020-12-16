import shapely
import shapely.geometry

from utils import pose_to_xyr

# Polygon describing the shape of an individual key cutout
cutout_geom_square = shapely.geometry.polygon.Polygon([
    # untested
    (7, 7),
    (7, -7),
    (-7, -7),
    (-7, 7),
])
cutout_geom_mx_alps = shapely.geometry.polygon.Polygon([
    # from https://github.com/swill/kad/blob/62948e9/key.go
    # untested
    (7, -7),
    (7, -6.4),
    (7.8, -6.4),
    (7.8, 6.4),
    (7, 6.4),
    (7, 7),
    (-7, 7),
    (-7, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
    (-7, -6.4),
    (-7, -7),
])
cutout_geom_mx_wings = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    # untested
    (7, -7),
    (7, -6),
    (7.8, -6),
    (7.8, -2.9),
    (7, -2.9),
    (7, 2.9),
    (7.8, 2.9),
    (7.8, 6),
    (7, 6),
    (7, 7),
    (-7, 7),
    (-7, 6),
    (-7.8, 6),
    (-7.8, 2.9),
    (-7, 2.9),
    (-7, -2.9),
    (-7.8, -2.9),
    (-7.8, -6),
    (-7, -6),
    (-7, -7),
])
cutout_geom_alps = shapely.geometry.polygon.Polygon([
    # adapted from https://github.com/swill/kad/blob/62948e9/key.go
    # untested
    (7.8, -6.4),
    (7.8, 6.4),
    (-7.8, 6.4),
    (-7.8, -6.4),
])
cutout_geom = cutout_geom_mx_wings


def rotate_keys(keys, angle):
    for key in keys:
        yield shapely.affinity.rotate(key, angle / 2, origin=(0, 0))


def holes_between_keys(keys, hole_map):
    for k1, k2 in hole_map:
        x1, y1, _ = pose_to_xyr(keys[k1])
        x2, y2, _ = pose_to_xyr(keys[k2])
        yield shapely.geometry.Point((x1 + x2) / 2, (y1 + y2) / 2)


# Split the keys by x-value into monotonically increasing sublists
def rows(keys):
    row = []
    last_x = None
    for key in keys:
        x, y, r = pose_to_xyr(key)
        if last_x and x < last_x:
            yield row
            row = []
        last_x = x
        row.append(key)

    if len(row) > 0: yield row


def generate_key_placeholders(keys):
    def placeholder(key):
        p = shapely.geometry.polygon.Polygon([
            (9.525, 9.525),
            (9.525, -9.525),
            (-9.525, -9.525),
            (-9.525, 9.525),
        ])
        x, y, r = pose_to_xyr(key)
        return shapely.affinity.translate(shapely.affinity.rotate(p, r), x, y)

    return shapely.geometry.multipolygon.MultiPolygon(
        placeholder(key) for key in keys)


def mirror_keys(keys, middle_space):
    keys = list(keys)
    x_min, y_min, _, _ = generate_key_placeholders(keys).bounds

    row = []
    last_x = None
    for row in rows(keys):
        full_row = []
        for key in row:
            key = shapely.affinity.translate(key,
                                             xoff=-x_min + middle_space / 2,
                                             yoff=-y_min)
            mirror_key = shapely.affinity.scale(key, -1, origin=(0, 0))
            full_row.insert(0, mirror_key)
            full_row.append(key)

        yield from full_row
