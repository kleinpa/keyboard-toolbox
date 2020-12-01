import os
import sys
import tempfile
import zipfile

import pcbnew
from absl import app, flags

FLAGS = flags.FLAGS
flags.DEFINE_string('input', '', 'Format to emit')
flags.DEFINE_string('output', '', 'Format to emit')


def main(argv):

    with tempfile.TemporaryDirectory() as temp_path:
        board = pcbnew.LoadBoard(FLAGS.input)

        pctl = pcbnew.PLOT_CONTROLLER(board)

        popt = pctl.GetPlotOptions()
        popt.SetOutputDirectory(temp_path)

        # Set some important plot options:
        popt.SetPlotFrameRef(False)
        #popt.SetLineWidth(pcbnew.FromMM(0.35))

        # TODO(kleinpa): Will JLCPCB accept file without this set?
        popt.SetUseGerberProtelExtensions(True)

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

        plot_plan = [("F_Cu", pcbnew.F_Cu, "Top layer"),
                     ("B_Cu", pcbnew.B_Cu, "Bottom layer"),
                     ("B_Mask", pcbnew.B_Mask, "Mask Bottom"),
                     ("F_Mask", pcbnew.F_Mask, "Mask top"),
                     ("B_Paste", pcbnew.B_Paste, "Paste Bottom"),
                     ("F_Paste", pcbnew.F_Paste, "Paste Top"),
                     ("F_SilkS", pcbnew.F_SilkS, "Silk Top"),
                     ("B_SilkS", pcbnew.B_SilkS, "Silk Bottom"),
                     ("Edge_Cuts", pcbnew.Edge_Cuts, "Edges")]

        # Functional Gerber Plots
        for suffix, layer, description in plot_plan:
            pctl.SetLayer(layer)
            pctl.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER, description)
            pctl.PlotLayer()
            pctl.ClosePlot()

        # #generate internal copper layers, if any
        for layer in range(1, board.GetCopperLayerCount() - 1):
            pctl.SetLayer(layer)
            lyrname = 'inner%s' % layer
            pctl.OpenPlotfile(lyrname, pcbnew.PLOT_FORMAT_GERBER, "inner")
            pctl.PlotLayer()
            pctl.ClosePlot()

        # Fabricators need drill files.
        # sometimes a drill map file is asked (for verification purpose)
        drlwriter = pcbnew.EXCELLON_WRITER(board)
        drlwriter.SetMapFileFormat(pcbnew.PLOT_FORMAT_PDF)

        mirror = False
        minimalHeader = False

        if False and popt.GetUseAuxOrigin():
            offset = board.GetAuxOrigin()
        else:
            offset = pcbnew.wxPoint(0, 0)

        mergeNPTH = True
        drlwriter.SetOptions(mirror, minimalHeader, offset, mergeNPTH)

        metricFmt = True
        drlwriter.SetFormat(metricFmt)

        genDrl = True
        genMap = False
        drlwriter.CreateDrillandMapFilesSet(temp_path, genDrl, genMap)

        with zipfile.ZipFile(FLAGS.output, 'w', zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    print(f"wrote {file}", file=sys.stderr)
                    zip.write(os.path.join(root, file),
                              file.replace("gm1", "gko"))


if __name__ == "__main__":
    app.run(main)
