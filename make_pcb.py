import sys
from math import atan, atan2, cos, degrees, radians, sin, sqrt

import itertools
import shapely
import shapely.geometry
from absl import app, flags

import pcbnew
from utils import pose, generate_outline, pose_to_xyr
from kicad_utils import kicad_text, kicad_polygon, kicad_circle


def generate_kicad_pcb(output_path, kb):
    keys = [pose(k.x, k.y, k.r) for k in kb.key_poses]
    holes = [shapely.geometry.Point(h.x, h.y) for h in kb.hole_positions]

    outline = generate_outline(kb)
    x_min, y_min, x_max, y_max = shapely.affinity.scale(outline,
                                                        yfact=-1,
                                                        origin=(0, 0)).bounds

    margin = 16

    # block_margin = 48 # TODO: use bounds to set page size

    # Transform geometry into kicad coordinate system (top-left origin)
    def page_transform(geom):
        geom = shapely.affinity.scale(geom, yfact=-1, origin=(0, 0))
        geom = shapely.affinity.translate(geom,
                                          xoff=-x_min + margin,
                                          yoff=-y_min + margin)
        return geom

    board = pcbnew.BOARD()

    # TODO: Is there a good way to set default track width to 0.5mm

    board.Add(
        kicad_text(page_transform(pose(79, 43, 180 - 39)),
                   "quine mk1\npeterklein.dev"))

    import inspect
    item = kicad_text(page_transform(pose(-x_min, 60, 180)),
                      "inspect.getsource(quine_1_keyboard)", pcbnew.FromMM(4),
                      pcbnew.B_SilkS)
    item.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_LEFT)
    board.Add(item)

    ground_net = pcbnew.NETINFO_ITEM(board, f"GND")
    board.Add(ground_net)

    outline = page_transform(generate_outline(kb))
    for x in kicad_polygon(outline):
        board.Add(x)

    # TODO: un-hardcode
    col_net = [pcbnew.NETINFO_ITEM(board, f"col-{i}") for i in range(12)]
    for x in col_net:
        board.Add(x)
    row_net = [pcbnew.NETINFO_ITEM(board, f"row-{i}") for i in range(4)]
    for x in row_net:
        board.Add(x)

    for i, key in enumerate(keys):
        # TODO: un-hardcode
        col = i % 12
        row = i // 12
        if row == 3: col += 3

        net = pcbnew.NETINFO_ITEM(board, f"switch-diode-{i}")
        board.Add(net)

        # m = pcbnew.FootprintLoad("external/com_github_keebio_keebio_parts",
        #                          "MX-Alps-Choc-1U-NoLED")
        item = pcbnew.FootprintLoad(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Button_Switch_Keyboard.pretty",
            "SW_Cherry_MX_1.00u_PCB")
        item.MoveAnchorPosition(pcbnew.wxPointMM(2.54, -5.08))

        x, y, r = pose_to_xyr(page_transform(key))
        item.SetPosition(pcbnew.wxPointMM(x, y))

        item.SetOrientationDegrees(180 - r)
        item.SetReference(f"SW{i}")
        item.FindPadByName(2).SetNet(net)
        item.FindPadByName(1).SetNet(row_net[row])
        item.Reference().SetKeepUpright(False)
        for g in item.GraphicalItems():
            if isinstance(g, pcbnew.EDA_TEXT):
                g.SetKeepUpright(False)
            else:
                g.DeleteStructure()
        board.Add(item)

        item = pcbnew.FootprintLoad(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Diode_SMD.pretty",
            "D_SOD-123")

        x, y, r = pose_to_xyr(page_transform(key))
        item.MoveAnchorPosition(pcbnew.wxPointMM(2.5, -6.5))
        item.SetPosition(pcbnew.wxPointMM(x, y))
        item.SetOrientationDegrees(180 + r)
        item.SetReference(f"D{i}")
        item.Flip(pcbnew.wxPointMM(x, y), True)
        item.FindPadByName(1).SetNet(net)
        item.FindPadByName(2).SetNet(col_net[col])
        item.Reference().SetKeepUpright(False)
        for g in item.GraphicalItems():
            if isinstance(g, pcbnew.EDA_TEXT):
                g.SetKeepUpright(False)
        board.Add(item)

    mcu_offset = 8.5

    x, y, r = pose_to_xyr(
        page_transform(
            pose(kb.controller_pose.x, kb.controller_pose.y,
                 kb.controller_pose.r)))
    item = pcbnew.FootprintLoad("external/com_github_keebio_keebio_parts",
                                "ArduinoProMicro")
    item.MoveAnchorPosition(pcbnew.wxPointMM(mcu_offset, 0))
    item.SetPosition(pcbnew.wxPointMM(x, y))
    item.SetOrientationDegrees(90 + r)
    item.SetReference(f"MCU0")
    item.Flip(pcbnew.wxPointMM(x, y), True)
    for g in item.GraphicalItems():
        if isinstance(g, pcbnew.EDA_TEXT):
            g.SetVisible(False)
        else:
            g.DeleteStructure()

    board.Add(item)
    for i in [3, 4, 23]:
        item.FindPadByName(i).SetNet(ground_net)

    # io_pins = [
    #     m.FindPadByName(i) for i in (1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
    #                                  15, 16, 17, 18, 19, 20)  # clockwise
    # ]
    # for mcu_pin, net in zip(io_pins, reversed(itertools.chain(col_net, row_net))):
    #     mcu_pin.SetNet(net)

    # TODO: un-hardcode
    item.FindPadByName(1).SetNet(row_net[0])
    item.FindPadByName(10).SetNet(row_net[1])
    item.FindPadByName(11).SetNet(row_net[2])
    item.FindPadByName(12).SetNet(row_net[3])

    item.FindPadByName(20).SetNet(col_net[0])
    item.FindPadByName(19).SetNet(col_net[1])
    item.FindPadByName(18).SetNet(col_net[2])
    item.FindPadByName(17).SetNet(col_net[3])
    item.FindPadByName(16).SetNet(col_net[4])
    item.FindPadByName(15).SetNet(col_net[5])
    item.FindPadByName(14).SetNet(col_net[6])
    item.FindPadByName(13).SetNet(col_net[7])
    item.FindPadByName(9).SetNet(col_net[8])
    item.FindPadByName(8).SetNet(col_net[9])
    item.FindPadByName(7).SetNet(col_net[10])
    item.FindPadByName(6).SetNet(col_net[11])

    # Add holes
    for h in holes:
        board.Add(kicad_circle(page_transform(h), kb.hole_diameter))

    # Add ground plane
    item = pcbnew.ZONE(board, False)
    poly = pcbnew.wxPoint_Vector()
    for x, y in outline.exterior.coords:
        poly.append(pcbnew.wxPointMM(x, y))
    item.AddPolygon(poly)
    item.SetNet(ground_net)
    lset = pcbnew.LSET()
    lset.AddLayer(pcbnew.F_Cu)
    lset.AddLayer(pcbnew.B_Cu)
    item.SetLayerSet(lset)

    # Use hatched fill because it looks cooler
    item.SetFillMode(pcbnew.ZONE_FILL_MODE_HATCH_PATTERN)
    item.SetHatchThickness(pcbnew.FromMM(1))
    item.SetHatchGap(pcbnew.FromMM(5))
    item.SetHatchOrientation(45)
    item.SetHatchSmoothingLevel(3)
    item.SetHatchSmoothingValue(1)

    board.Add(item)

    # pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    board.Save(output_path)
