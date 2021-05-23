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
