"""Helpers for working with KiCad pcb files."""

import io
import os
import shutil
import sys
import tempfile
import zipfile

import pcbnew

import shapely


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

    tf = tempfile.NamedTemporaryFile()
    board.Save(tf.name)
    return tf


def kicad_file_to_gerber_archive_file(kicad_fp):
    """Created an archive of gerber files from the provided kicad PCB file."""

    # copy kicad file to a named file
    with tempfile.NamedTemporaryFile(suffix=".kicad_pcb") as kicad_file:
        shutil.copyfileobj(kicad_fp, kicad_file)
        board = pcbnew.LoadBoard(kicad_file.name)

    pctl = pcbnew.PLOT_CONTROLLER(board)

    popt = pctl.GetPlotOptions()
    popt.SetPlotFrameRef(False)
    popt.SetAutoScale(False)
    popt.SetScale(1)
    popt.SetMirror(False)
    popt.SetUseGerberAttributes(False)
    popt.SetExcludeEdgeLayer(True)
    popt.SetScale(1)
    popt.SetUseAuxOrigin(True)
    popt.SetNegative(False)
    popt.SetPlotReference(True)
    popt.SetPlotValue(True)
    popt.SetPlotInvisibleText(False)
    popt.SetSubtractMaskFromSilk(True)
    popt.SetMirror(False)
    popt.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE)

    # TODO(kleinpa): Will JLCPCB accept file without this set?
    popt.SetUseGerberProtelExtensions(True)

    plot_plan = [("F_Cu", pcbnew.F_Cu, "Top layer"),
                 ("B_Cu", pcbnew.B_Cu, "Bottom layer"),
                 ("B_Mask", pcbnew.B_Mask, "Mask Bottom"),
                 ("F_Mask", pcbnew.F_Mask, "Mask top"),
                 ("B_Paste", pcbnew.B_Paste, "Paste Bottom"),
                 ("F_Paste", pcbnew.F_Paste, "Paste Top"),
                 ("F_SilkS", pcbnew.F_SilkS, "Silk Top"),
                 ("B_SilkS", pcbnew.B_SilkS, "Silk Bottom"),
                 ("Edge_Cuts", pcbnew.Edge_Cuts, "Edges")]

    for layer in range(1, board.GetCopperLayerCount() - 1):
        plot_plan += (f"inner{layer}", layer, "inner")

    with tempfile.TemporaryDirectory() as temp_path:
        popt.SetOutputDirectory(temp_path)

        # Plot layers
        for suffix, layer, description in plot_plan:
            pctl.SetLayer(layer)
            pctl.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, description)
            pctl.PlotLayer()
            pctl.ClosePlot()

        # Generate drill file
        drlwriter = pcbnew.EXCELLON_WRITER(board)
        drlwriter.SetMapFileFormat(aMapFmt=pcbnew.PLOT_FORMAT_GERBER)
        drlwriter.SetOptions(aMirror=False,
                             aMinimalHeader=False,
                             aOffset=pcbnew.wxPoint(0, 0),
                             aMerge_PTH_NPTH=True)
        formatMetric = True
        drlwriter.SetFormat(formatMetric)
        drlwriter.CreateDrillandMapFilesSet(aPlotDirectory=temp_path,
                                            aGenDrill=True,
                                            aGenMap=False)

        # Copy files from output directory to in-memory zip file
        fp = io.BytesIO()
        with zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    z.write(
                        os.path.join(root, file),
                        # TODO(kleinpa): Required for JLCPCB, any alternative?
                        file.replace("gm1", "gko"))
        fp.seek(0)
        return fp