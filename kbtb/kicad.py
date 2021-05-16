"""Helpers for working with KiCad pcb files."""

import io
import os
import sys
import tempfile
import csv
import zipfile
import re

import pcbnew

import shapely

lcsc_parts = {
    ("D_SOD-123", "4148"): "C81598",
    ("HRO-TYPE-C-31-M-12", "HRO-TYPE-C-31-M-12"): "C165948",
    ("LQFP-48_7x7mm_P0.5mm", "STM32F072C8T6"): "C80488",
    ("R_0603_1608Metric", "0.1 uF"): "C14663",
    ("R_0603_1608Metric", "10 kΩ"): "C25803",
    ("R_0603_1608Metric", "5.1 kΩ"): "C23186",
    ("SOT-143", "SR05"): "C521962",
    ("SOT-23", "MCP1700T-3302E/TT"): "C5446",
}


def kicad_polygon(geom,
                  x_offset=0,
                  y_offset=0,
                  x_scale=1,
                  y_scale=-1,
                  layer=pcbnew.Edge_Cuts):
    """Yield a sequence of KiCad segments from the provided Shapely polygon.

    A Shapely polygon may have interior polygons representing holes in
    the larger polygon. The hole polygons are emitted as additional
    segments so they appear as pcb cutouts.
    """

    # coerce to polygon in case input is a ring
    geom = shapely.geometry.polygon.Polygon(geom)

    def make_point(p):
        x, y = p
        return pcbnew.wxPointMM(x_scale * x + x_offset, y_scale * y + y_offset)

    def make_seg(p1, p2):
        seg = pcbnew.PCB_SHAPE()
        seg.SetShape(pcbnew.S_SEGMENT)
        seg.SetStart(make_point(p1))
        seg.SetEnd(make_point(p2))
        seg.SetLayer(layer)
        return seg

    points = geom.exterior.coords
    for p1, p2 in [(points[i], points[(i + 1) % len(points)])
                   for i in range(len(points))]:
        yield make_seg(p1, p2)

    for interior in geom.interiors:
        points = interior.coords
        for p1, p2 in [(points[i], points[(i + 1) % len(points)])
                       for i in range(len(points))]:
            yield make_seg(p1, p2)


def kicad_circle(x, y, diameter, layer=pcbnew.Edge_Cuts):
    """Create and return a KiCad circle centered at x, y."""
    item = pcbnew.PCB_SHAPE()
    item.SetShape(pcbnew.S_CIRCLE)
    item.SetStart(pcbnew.wxPointMM(x, y))
    item.SetEnd(pcbnew.wxPointMM(x + diameter / 2, y))
    item.SetLayer(layer)
    return item


def polygon_to_kicad_file(geom):
    """Build a kicad file containing an empty PCB with the provided shape."""
    board = pcbnew.BOARD()

    for x in kicad_polygon(geom):
        board.Add(x)

    with tempfile.NamedTemporaryFile() as tf:
        board.Save(tf.name)
        return tf.read()


def kicad_bom(board, layer=pcbnew.B_Cu):
    # https://support.jlcpcb.com/article/79-pick-place-file-for-smt-assembly
    fieldnames = ['Designator', 'Description', 'Value', 'LCSC Part Number']
    fp = io.StringIO()
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()

    for footprint in board.GetFootprints():
        if footprint.GetLayer() != layer:
            continue

        writer.writerow({
            'Designator':
            footprint.GetReference(),
            'Description':
            footprint.GetFPID().GetLibItemName(),
            'Value':
            footprint.GetValue(),
            'LCSC Part Number':
            lcsc_parts.get((str(footprint.GetFPID().GetLibItemName()),
                            str(footprint.GetValue())), 'unknown'),
        })
    fp.seek(0)
    return fp.read()


def kicad_centroid(board, layer=pcbnew.B_Cu):
    # https://support.jlcpcb.com/article/79-pick-place-file-for-smt-assembly
    fieldnames = ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer']
    fp = io.StringIO()
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()

    for footprint in board.GetFootprints():
        if footprint.GetLayer() != layer:
            continue
        writer.writerow({
            'Designator': footprint.GetReference(),
            'Mid X': footprint.GetPosition().x * pcbnew.MM_PER_IU,
            'Mid Y': footprint.GetPosition().y * pcbnew.MM_PER_IU,
            'Rotation': footprint.GetOrientationDegrees(),
            'Layer': 'bottom',
        })
    fp.seek(0)
    return fp.read()


def bomcpl_from_kicad(kicad_file):
    """Created an archive of gerber files from the provided kicad PCB file."""

    # copy kicad file to a named file
    with tempfile.NamedTemporaryFile(suffix=".kicad_pcb") as fp:
        fp.write(kicad_file)
        board = pcbnew.LoadBoard(fp.name)

        # Copy files from output directory to in-memory zip file
        fp = io.BytesIO()
        with zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('bom.csv', kicad_bom(board))
            z.writestr('cpl.csv', kicad_centroid(board))
        return fp.getvalue()
