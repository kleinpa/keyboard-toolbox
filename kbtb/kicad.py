"""Helpers for working with KiCad pcb files."""

from typing import NamedTuple

import io
import os
import sys
import tempfile
import csv
import zipfile
import re
import logging

import pcbnew

import shapely

lcsc_parts = {
    ("D_SOD-123", "4148"):
    "C81598",
    ("HRO-TYPE-C-31-M-12", "HRO-TYPE-C-31-M-12"):
    "C165948",
    ("LQFP-48_7x7mm_P0.5mm", "STM32F072C8T6"):
    "C80488",
    ("R_0603_1608Metric", "0.1 µF"):
    "C14663",
    ("R_0603_1608Metric", "10 kΩ"):
    "C25803",
    ("R_0603_1608Metric", "5.1 kΩ"):
    "C23186",
    ("SOT-143", "SR05"):
    "C521962",
    ("SOT-23", "MCP1700T-3302E/TT"):
    "C5446",
    ("", "ATMEGA32U4-AU"):
    "C44854",
    ("Crystal_SMD_3225-4Pin_3.2x2.5mm", "16 MHz"):
    "C13738",
    ('Tag-Connect_TC2030-IDC-FP_2x03_P1.27mm_Vertical', 'Tag-Connect_TC2030-IDC-FP_2x03_P1.27mm_Vertical'):
    None,
    ('R_0603_1608Metric', '10 µF'):
    "C19702",
    ('R_0603_1608Metric', '22 pF'):
    "C1653",
    ('R_0603_1608Metric', '1 µF'):
    "C15849",
    ('TQFP-44_10x10mm_P0.8mm', 'ATMEGA32U4-AU'):
    "",
}


class PCBPosition(NamedTuple):
    x: int
    y: int
    r: int = 0
    flip: bool = False


def set_pcb_position(obj, pcbpos: PCBPosition):
    obj.SetPosition(pcbnew.wxPointMM(pcbpos.x, pcbpos.y))
    if pcbpos.flip:
        obj.Flip(pcbnew.wxPointMM(pcbpos.x, pcbpos.y), aFlipLeftRight=True)
    if isinstance(obj, pcbnew.FOOTPRINT):
        obj.SetOrientationDegrees(-pcbpos.r)
    elif isinstance(obj, pcbnew.PCB_TEXT):
        obj.SetTextAngle(-pcbpos.r * 10)
        #obj.SetMirrored(pcbpos.flip)
    else:
        raise RuntimeError(f"can't set position of type {type(obj)}")
    return obj


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


def kicad_add_text(board,
                   pcbpos,
                   text,
                   size=1,
                   thickness=1,
                   layer=pcbnew.F_SilkS):
    test_obj = pcbnew.PCB_TEXT(board)
    test_obj.SetText(text)
    test_obj.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
    test_obj.SetTextSize(
        pcbnew.wxSize(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    test_obj.SetTextThickness(pcbnew.FromMM(size * thickness * 0.15))
    test_obj.SetLayer(layer)
    set_pcb_position(test_obj, pcbpos)
    board.Add(test_obj)


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

        lcsc_part = "unknown"

        key = (str(footprint.GetFPID().GetLibItemName()),
               str(footprint.GetValue()))
        if key in lcsc_parts:
            if lcsc_parts[key]:
                writer.writerow({
                    'Designator':
                    footprint.GetReference(),
                    'Description':
                    footprint.GetFPID().GetLibItemName(),
                    'Value':
                    footprint.GetValue(),
                    'LCSC Part Number':
                    lcsc_parts[key],
                })
        else:
            logging.warn(f"unknown lcsc part number for {key}")

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
