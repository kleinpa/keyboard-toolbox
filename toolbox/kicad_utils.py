import io
import os
import shutil
import sys
import tempfile
import zipfile

import pcbnew


def kicad_polygon(geom, x_offset=0, y_offset=0, x_scale=1, y_scale=-1):
    def make_point(p):
        x, y = p
        return pcbnew.wxPointMM(x_scale * x + x_offset, y_scale * y + y_offset)

    points = geom.exterior.coords
    for p1, p2 in [(points[i], points[(i + 1) % len(points)])
                   for i in range(len(points))]:
        seg = pcbnew.PCB_SHAPE()
        seg.SetStart(make_point(p1))
        seg.SetEnd(make_point(p2))
        seg.SetLayer(pcbnew.Edge_Cuts)
        yield seg

    for interior in geom.interiors:
        points = interior.coords
        for p1, p2 in [(points[i], points[(i + 1) % len(points)])
                       for i in range(len(points))]:
            seg = pcbnew.PCB_SHAPE()
            seg.SetShape(pcbnew.S_SEGMENT)
            seg.SetStart(make_point(p1))
            seg.SetEnd(make_point(p2))
            seg.SetLayer(pcbnew.Edge_Cuts)
            yield seg


def kicad_text(text, x, y, r, size=pcbnew.FromMM(1.27), layer=pcbnew.F_SilkS):
    item = pcbnew.PCB_TEXT(None)
    item.SetPosition(pcbnew.wxPointMM(x, y))
    item.SetTextAngle(r * 10)
    item.SetLayer(layer)
    item.SetText(text)
    item.SetTextSize(pcbnew.wxSize(size, size))

    if layer == pcbnew.B_SilkS:  # all mirrored layers?
        item.SetMirrored(True)  #item.Flip(pcbnew.wxPointMM(x, y), False)
    return item


def kicad_circle(x, y, diameter, layer=pcbnew.Edge_Cuts):
    item = pcbnew.PCB_SHAPE()
    item.SetShape(pcbnew.S_CIRCLE)
    item.SetStart(pcbnew.wxPointMM(x, y))
    item.SetEnd(pcbnew.wxPointMM(x + diameter / 2, y))
    item.SetLayer(layer)
    return item


def shape_to_kicad_file(geom):
    board = pcbnew.BOARD()

    for x in kicad_polygon(geom):
        board.Add(x)

    tf = tempfile.NamedTemporaryFile()
    board.Save(tf.name)
    return tf


def kicad_file_to_gerber_archive_file(kicad_fp):
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

    with tempfile.TemporaryDirectory() as temp_path:
        popt.SetOutputDirectory(temp_path)

        # Functional Gerber Plots
        for suffix, layer, description in plot_plan:
            pctl.SetLayer(layer)
            pctl.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, description)
            pctl.PlotLayer()
            pctl.ClosePlot()

        # Internal Copper Layers
        for layer in range(1, board.GetCopperLayerCount() - 1):
            pctl.SetLayer(layer)
            lyrname = 'inner%s' % layer
            pctl.OpenPlotfile(lyrname, pcbnew.PLOT_FORMAT_GERBER, "inner")
            pctl.PlotLayer()
            pctl.ClosePlot()

        drlwriter = pcbnew.EXCELLON_WRITER(board)
        drlwriter.SetMapFileFormat(pcbnew.PLOT_FORMAT_GERBER)
        drlwriter.SetOptions(aMirror=False,
                             aMinimalHeader=False,
                             aOffset=pcbnew.wxPoint(0, 0),
                             aMerge_PTH_NPTH=True)

        metricFmt = True
        drlwriter.SetFormat(metricFmt)

        drlwriter.CreateDrillandMapFilesSet(aPlotDirectory=temp_path,
                                            aGenDrill=True,
                                            aGenMap=False)

        fp = io.BytesIO()
        with zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    print(f"wrote {file}", file=sys.stderr)

                    # This change seems to be required for JLCPCB to process the archive.
                    z.write(os.path.join(root, file),
                            file.replace("gm1", "gko"))
        fp.seek(0)
        return fp
