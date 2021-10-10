"""Helpers for working with KiCad pcb files."""

from __future__ import annotations
from typing import NamedTuple, Any
from math import cos, radians, sin
import os
import tempfile

import pcbnew
import shapely


class Board(NamedTuple):
    """Create a KiCad pcb file that implements the provided keyboard.

    This function is limited by the capabilities of KiCad's scripting
    interface, but the idea is to build out as much of the PCB as we
    can from the provided keyboard object.

    This function generates and returns a two-layer PCB with an
    outline and ground plane built from `kb.outline_polygon` and with
    footprints for the switches, diodes, microcontroller, and mounting
    holes. The keyboard matrix will be used to configure connections
    between the switches, diodes, and controller pins.

    A few KiCad-based limitations:

    * The default trace width is loaded from a KiCad project file
      which is not generated here, therefore the default trace width
      will need to be configured manually.

    * The `pcbnew.ZONE_FILLER` is not available when running
      standalone.

    """

    outline: Any
    components: list[Any] = []
    holes: list[Any] = []
    fill_name: str | None = "ground"

    def build(self):
        board = pcbnew.BOARD()

        # outline
        PcbPolygon(self.outline).build(board)

        # Add holes
        for h in self.holes:
            h.build(board)

        # Add ground plane
        signals = {}
        if self.fill_name:
            fill_net = pcbnew.NETINFO_ITEM(board, self.fill_name)
            board.Add(fill_net)
            signals[self.fill_name] = fill_net

            item = pcbnew.ZONE(board, False)
            poly = pcbnew.wxPoint_Vector()
            for x, y in self.outline.exterior.coords:
                poly.append(pcbnew.wxPointMM(x, y))
            item.AddPolygon(poly)
            item.SetNet(fill_net)
            lset = pcbnew.LSET()
            lset.AddLayer(pcbnew.F_Cu)
            lset.AddLayer(pcbnew.B_Cu)
            item.SetLayerSet(lset)
            board.Add(item)

        for component in self.components:
            component.build(board, signals)

        return board

    def to_bytes(self):
        board = self.build()
        with tempfile.NamedTemporaryFile() as tf:
            board.Save(tf.name)
            return tf.read()


class PcbPosition(NamedTuple):
    x: float
    y: float
    r: float = 0
    flip: bool = False

    def offset(self: PcbPosition, x=0, y=0, r=0, flip=False):
        return PcbPosition(
            self.x + cos(radians(self.r)) * x - sin(radians(self.r)) * y,
            self.y + cos(radians(self.r)) * y + sin(radians(self.r)) * x,
            self.r + r, self.flip ^ flip)


def set_pcb_position(obj, pcbpos: PcbPosition):
    obj.SetPosition(pcbnew.wxPointMM(pcbpos.x, pcbpos.y))
    if pcbpos.flip:
        obj.Flip(pcbnew.wxPointMM(pcbpos.x, pcbpos.y), aFlipLeftRight=True)
    if isinstance(obj, pcbnew.FOOTPRINT):
        obj.SetOrientationDegrees(-pcbpos.r)
    elif isinstance(obj, pcbnew.PCB_TEXT):
        obj.SetTextAngle(-pcbpos.r * 10)
    else:
        raise RuntimeError(f"can't set position of type {type(obj)}")


class PcbPolygon(NamedTuple):
    geom: Any
    layer: Any = pcbnew.Edge_Cuts

    def build(self,
              board: pcbnew.BOARD,
              external_signals: dict[str, pcbnew.NETINFO_ITEM] = {},
              path: list[str] = []):
        """Yield a sequence of KiCad segments from the provided Shapely polygon.

        A Shapely polygon may have interior polygons representing holes in
        the larger polygon. The hole polygons are emitted as additional
        segments so they appear as pcb cutouts.
        """

        # coerce to polygon in case input is a ring
        geom = shapely.geometry.polygon.Polygon(self.geom)

        def make_point(p):
            x, y = p
            return pcbnew.wxPointMM(x, y)

        def make_seg(p1, p2):
            seg = pcbnew.PCB_SHAPE()
            seg.SetShape(pcbnew.S_SEGMENT)
            seg.SetStart(make_point(p1))
            seg.SetEnd(make_point(p2))
            seg.SetLayer(self.layer)
            return seg

        points = geom.exterior.coords
        for p1, p2 in [(points[i], points[(i + 1) % len(points)])
                       for i in range(len(points))]:
            board.Add(make_seg(p1, p2))

        for interior in geom.interiors:
            points = interior.coords
            for p1, p2 in [(points[i], points[(i + 1) % len(points)])
                           for i in range(len(points))]:
                board.Add(make_seg(p1, p2))


class PcbText(NamedTuple):
    pcbpos: Any
    text: str
    size: float = 1
    thickness: float = 1
    layer: Any = pcbnew.F_SilkS

    def build(self,
              board: pcbnew.BOARD,
              external_signals: dict[str, pcbnew.NETINFO_ITEM] = {},
              path: list[str] = []):
        o = pcbnew.PCB_TEXT(board)
        o.SetText(self.text)
        o.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
        o.SetTextSize(
            pcbnew.wxSize(pcbnew.FromMM(self.size), pcbnew.FromMM(self.size)))
        o.SetTextThickness(pcbnew.FromMM(self.size * self.thickness * 0.15))
        o.SetLayer(self.layer)
        set_pcb_position(o, self.pcbpos)
        board.Add(o)


class PcbCircle(NamedTuple):
    x: float
    y: float
    diameter: float
    layer: Any = pcbnew.Edge_Cuts

    def build(self,
              board: pcbnew.BOARD,
              external_signals: dict[str, pcbnew.NETINFO_ITEM] = {},
              path: list[str] = []):
        """Create and return a KiCad circle centered at x, y."""
        item = pcbnew.PCB_SHAPE()
        item.SetShape(pcbnew.S_CIRCLE)
        item.SetStart(pcbnew.wxPointMM(self.x, self.y))
        item.SetEnd(pcbnew.wxPointMM(self.x + self.diameter / 2, self.y))
        item.SetLayer(self.layer)
        board.Add(item)


def polygon_to_kicad_file(geom):
    """Build a kicad file containing an empty PCB with the provided shape."""
    return Board(shapely.affinity.scale(geom, yfact=-1)).to_bytes()


class PcbComponent(NamedTuple):
    ref: str
    reference_prefix: str
    pose: PcbPosition
    value: str = ""
    reference_visible: bool = True
    value_visible: bool = True
    keep_upright: bool = False
    clear_top: bool = False
    pins: list[str] = []

    def build(self,
              board: pcbnew.BOARD,
              external_signals: dict[str, pcbnew.NETINFO_ITEM] = {},
              path: list[str] = []):
        def load_footprint(ref: str):
            """Load a footprint otherwise raise exception"""
            library, name = ref.split(":")
            footprint = pcbnew.FootprintLoad(
                os.path.join(
                    os.environ.get("RUNFILES_DIR", "external/"), library),
                name)
            if not footprint:
                raise ValueError(
                    f"can not load footprint {name} from library {library}")
            return footprint

        fp = load_footprint(self.ref)
        fp.SetValue(self.value)
        set_pcb_position(fp, self.pose)
        fp.Value().SetVisible(self.value_visible)
        fp.Reference().SetVisible(self.reference_visible)
        fp.Reference().SetKeepUpright(self.keep_upright)
        if self.clear_top:
            for g in fp.GraphicalItems():
                layer = g.GetLayer()
                if layer == 37:
                    if isinstance(g, pcbnew.EDA_TEXT):
                        g.SetVisible(False)
                    else:
                        g.DeleteStructure()

        other = [x.GetReference() for x in board.GetFootprints()]
        x = 1
        while f"{self.reference_prefix}{x}" in other:
            x = x + 1
        fp.SetReference(f"{self.reference_prefix}{x}")
        board.Add(fp)

        for i, pin_name in enumerate(self.pins, start=1):
            if pin_name in external_signals:
                fp.FindPadByName(i).SetNet(external_signals[pin_name])
        for name in external_signals.keys():
            if name not in self.pins:
                raise RuntimeError(
                    f"no pin '{name}' in {path} ({self.reference_prefix}{x})")


class PcbSection(NamedTuple):
    """PcbSection represents a section of a board. """
    id: str
    public_signals: set[str] = set()
    private_signals: set[str] = set()
    components: list[tuple[Any, map[str, str]]] = []

    def add(self, component, signal_mapping: dict[str, str] = {}):
        return self._replace(
            components=self.components + [(component, signal_mapping)])
        self.components.append((component, signal_mapping))

    def build(self,
              board: pcbnew.BOARD,
              external_signals: dict[str, pcbnew.NETINFO_ITEM] = {},
              path: list[str] = []):
        # Populate signal map creating new signals where required
        local_signals = {}
        for name in self.public_signals:
            if name in external_signals:
                local_signals[name] = external_signals[name]
            else:
                net = pcbnew.NETINFO_ITEM(board, "/".join((*path, self.id,
                                                           name)))
                board.Add(net)
                local_signals[name] = net
        for name in self.private_signals:
            net = pcbnew.NETINFO_ITEM(board, "/".join((*path, self.id, name)))
            board.Add(net)
            local_signals[name] = net

        # TODO: Warn about unused signals?

        for component, signal_mapping in self.components:
            component.build(
                board, {
                    inner_name: local_signals[signal_name]
                    for (inner_name, signal_name) in signal_mapping.items()
                }, (*path, self.id))
