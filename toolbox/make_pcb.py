import tempfile

import pcbnew
from math import sin, cos, atan2, degrees, radians

from toolbox.keyboard_pb2 import Keyboard
from toolbox.kicad_utils import kicad_circle, kicad_polygon
from toolbox.outline import generate_outline


def add_pro_micro(x, y, r, ground_net, io_nets):
    mcu_offset = 8.5

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

    for i in [3, 4, 23]:
        item.FindPadByName(i).SetNet(ground_net)

    item.FindPadByName(1).SetNet(io_nets[0])
    item.FindPadByName(2).SetNet(io_nets[1])
    item.FindPadByName(5).SetNet(io_nets[2])
    item.FindPadByName(6).SetNet(io_nets[3])
    item.FindPadByName(7).SetNet(io_nets[4])
    item.FindPadByName(8).SetNet(io_nets[5])
    item.FindPadByName(9).SetNet(io_nets[6])
    item.FindPadByName(10).SetNet(io_nets[7])
    item.FindPadByName(11).SetNet(io_nets[8])
    item.FindPadByName(12).SetNet(io_nets[9])
    item.FindPadByName(13).SetNet(io_nets[10])
    item.FindPadByName(14).SetNet(io_nets[11])
    item.FindPadByName(15).SetNet(io_nets[12])
    item.FindPadByName(16).SetNet(io_nets[13])
    item.FindPadByName(17).SetNet(io_nets[14])
    item.FindPadByName(18).SetNet(io_nets[15])
    item.FindPadByName(19).SetNet(io_nets[16])
    item.FindPadByName(20).SetNet(io_nets[17])

    return item


def generate_kicad_pcb_file(kb):
    """Create a KiCad pcb file that implements the provided keyboard.

    This function is limited by the capabilities of PCB, but the idea is to
    build out as much of the PCB as we can from the provided keyboard object.

    This function will generate and return a two-layer PCB with it's outline
    built according to `generate_outline()` (with matching ground planes) and
    with footprints for the switches, diodes, microcontroller, and mounting
    holes. The keyboard matrix will be used to configure connections between
    the switches, diodes, and MCU pins.

    A few KiCad-based limitations:

    * The default trace width is loaded from a KiCad project file which is not
      generated here, therefore the default trace width will need to be
      configured manually.
    * The `pcbnew.ZONE_FILLER` is not available when running standalone.
    """
    outline = generate_outline(kb)
    x_min, y_min, x_max, y_max = outline.bounds

    x_offset = 16 - x_min
    x_scale = 1
    y_offset = 16 + y_max
    y_scale = -1

    board = pcbnew.BOARD()

    ground_net = pcbnew.NETINFO_ITEM(board, f"GND")
    board.Add(ground_net)

    outline = generate_outline(kb)
    for x in kicad_polygon(outline,
                           x_offset=x_offset,
                           y_offset=y_offset,
                           x_scale=x_scale,
                           y_scale=y_scale):
        board.Add(x)

    mcu_io = 18

    io_nets = [pcbnew.NETINFO_ITEM(board, f"io-{i}") for i in range(mcu_io)]
    for x in io_nets:
        board.Add(x)

    if kb.footprint != Keyboard.FOOTPRINT_CHERRY_MX:
        raise RuntimeError(f"unknown footprint")

    for i, key in enumerate(kb.keys):
        net1 = io_nets[key.controller_pin_low]
        net2 = io_nets[key.controller_pin_high]

        net = pcbnew.NETINFO_ITEM(board, f"switch-diode-{i}")
        board.Add(net)

        # item = pcbnew.FootprintLoad("external/com_github_keebio_keebio_parts",
        #                             "Kailh-PG1350-1u-NoLED")
        item = pcbnew.FootprintLoad(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Button_Switch_Keyboard.pretty",
            "SW_Cherry_MX_1.00u_PCB")
        item.MoveAnchorPosition(pcbnew.wxPointMM(2.54, -5.08))
        x, y = x_scale * key.pose.x + x_offset, y_scale * key.pose.y + y_offset
        r = degrees(
            atan2(y_scale * sin(radians(key.pose.r - 90)),
                  x_scale * cos(radians(key.pose.r - 90)))) + 90
        item.SetPosition(pcbnew.wxPointMM(x, y))

        item.SetOrientationDegrees(180 - r)
        item.SetReference(f"SW{i}")
        item.FindPadByName(2).SetNet(net)
        item.FindPadByName(1).SetNet(net1)
        item.Reference().SetKeepUpright(False)
        for g in item.GraphicalItems():
            if isinstance(g, pcbnew.EDA_TEXT):
                g.SetKeepUpright(False)
        board.Add(item)

        item = pcbnew.FootprintLoad(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Diode_SMD.pretty",
            "D_SOD-123")

        x, y = x_scale * key.pose.x + x_offset, y_scale * key.pose.y + y_offset
        r = degrees(
            atan2(y_scale * sin(radians(key.pose.r - 90)),
                  x_scale * cos(radians(key.pose.r - 90)))) + 90
        item.MoveAnchorPosition(pcbnew.wxPointMM(2.5, -6.5))
        item.SetPosition(pcbnew.wxPointMM(x, y))
        item.SetOrientationDegrees(180 + r)
        item.SetReference(f"D{i}")
        item.Flip(pcbnew.wxPointMM(x, y), True)
        item.FindPadByName(1).SetNet(net)
        item.FindPadByName(2).SetNet(net2)
        item.Reference().SetKeepUpright(False)
        for g in item.GraphicalItems():
            if isinstance(g, pcbnew.EDA_TEXT):
                g.SetKeepUpright(False)
            else:
                g.DeleteStructure()
        board.Add(item)

    if kb.controller == Keyboard.CONTROLLER_PROMICRO:
        x, y = x_scale * kb.controller_pose.x + x_offset, y_scale * kb.controller_pose.y + y_offset
        r = degrees(
            atan2(y_scale * sin(radians(key.pose.r - 90)),
                  x_scale * cos(radians(key.pose.r - 90)))) + 90
        board.Add(add_pro_micro(x, y, r, ground_net, io_nets))
    else:
        raise RuntimeError("unknown controller")

    # Add holes
    for h in kb.hole_positions:
        x, y = x_scale * h.x + x_offset, y_scale * h.y + y_offset
        board.Add(kicad_circle(x, y, kb.hole_diameter))

    # Add ground plane
    item = pcbnew.ZONE(board, False)
    poly = pcbnew.wxPoint_Vector()
    for x, y in outline.exterior.coords:
        x, y = x_scale * x + x_offset, y_scale * y + y_offset
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

    tf = tempfile.NamedTemporaryFile()
    board.Save(tf.name)
    return tf
