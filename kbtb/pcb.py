import os
import tempfile
from math import atan2, cos, degrees, radians, sin

import pcbnew
import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard
from kbtb.kicad import kicad_circle, kicad_polygon


def load_footprint(library, footprint):
    module = pcbnew.FootprintLoad(library, footprint)
    if not module:
        raise ValueError(
            f"can not load footprint {footprint} from library {library}")
    return module


def place_module(module, x, y, r, flip=False):
    module = pcbnew.FOOTPRINT(module)
    module.SetPosition(pcbnew.wxPointMM(x, y))
    if flip:
        module.Flip(pcbnew.wxPointMM(x, y), aFlipLeftRight=True)
    module.SetOrientationDegrees(180 - r)
    for g in module.GraphicalItems():
        if isinstance(g, pcbnew.EDA_TEXT):
            g.SetKeepUpright(False)
    return module


def add_pro_micro(x, y, r, parent, ground_net, io_nets):
    mcu_offset = 17.75

    controller = load_footprint("external/com_github_keebio_keebio_parts",
                                "ArduinoProMicro")
    controller.MoveAnchorPosition(pcbnew.wxPointMM(mcu_offset, 0))
    controller.SetPosition(pcbnew.wxPointMM(x, y))
    controller.SetOrientationDegrees(90 + r)
    controller.SetReference(f"U1")
    controller.Flip(pcbnew.wxPointMM(x, y), True)
    for g in controller.GraphicalItems():
        if isinstance(g, pcbnew.EDA_TEXT):
            pass  #g.SetVisible(False)
        else:
            pass  #g.DeleteStructure()

    for i in [3, 4, 23]:
        controller.FindPadByName(i).SetNet(ground_net)

    controller.FindPadByName(1).SetNet(io_nets[0])
    controller.FindPadByName(2).SetNet(io_nets[1])
    controller.FindPadByName(5).SetNet(io_nets[2])
    controller.FindPadByName(6).SetNet(io_nets[3])
    controller.FindPadByName(7).SetNet(io_nets[4])
    controller.FindPadByName(8).SetNet(io_nets[5])
    controller.FindPadByName(9).SetNet(io_nets[6])
    controller.FindPadByName(10).SetNet(io_nets[7])
    controller.FindPadByName(11).SetNet(io_nets[8])
    controller.FindPadByName(12).SetNet(io_nets[9])
    controller.FindPadByName(13).SetNet(io_nets[10])
    controller.FindPadByName(14).SetNet(io_nets[11])
    controller.FindPadByName(15).SetNet(io_nets[12])
    controller.FindPadByName(16).SetNet(io_nets[13])
    controller.FindPadByName(17).SetNet(io_nets[14])
    controller.FindPadByName(18).SetNet(io_nets[15])
    controller.FindPadByName(19).SetNet(io_nets[16])
    controller.FindPadByName(20).SetNet(io_nets[17])

    return controller

# Adds a USB Type-C connector configured as a Legacy Device Adapter.
def add_usbc_legacy(x, y, r, parent, ground_net, net_usb_plus, net_usb_minus, net_usb_vbus, flip=False):
    net_usb_cc1 = pcbnew.NETINFO_ITEM(parent, f"usb-cc1")
    parent.Add(net_usb_cc1)
    net_usb_cc2 = pcbnew.NETINFO_ITEM(parent, f"usb-cc2")
    parent.Add(net_usb_cc2)

    def offset(x1,y1,r1,x2,y2,r2):
        return (x1+cos(radians(r1))*x2-sin(radians(r1))*y2,
               y1+cos(radians(r1))*y2+sin(radians(r1))*x2,
               r1+r2)

    # usb type-c connector
    item = place_module(
        load_footprint(
            "external/com_github_ai03_2725_typec",
            "HRO-TYPE-C-31-M-12",
        ), *offset(x,y,r,0,0,180 if flip else 0), flip)

    item.SetReference(f"J1")
    item.FindPadByName(1).SetNet(ground_net)
    item.FindPadByName(2).SetNet(net_usb_vbus)
    #item.FindPadByName(3).SetNet() # sbu2
    item.FindPadByName(4).SetNet(net_usb_cc1)
    item.FindPadByName(5).SetNet(net_usb_minus)
    item.FindPadByName(6).SetNet(net_usb_plus)
    item.FindPadByName(7).SetNet(net_usb_minus)
    item.FindPadByName(8).SetNet(net_usb_plus)
    #item.FindPadByName(9).SetNet() # sbu1
    item.FindPadByName(10).SetNet(net_usb_cc2)
    item.FindPadByName(11).SetNet(net_usb_vbus)
    item.FindPadByName(12).SetNet(ground_net)
    #item.FindPadByName(13).SetNet()  # shield
    yield item

    ## usb cc resistors
    def resistor(x,y,r,ref,val,net_a,net_b):
        item = place_module(
            load_footprint(
                "external/com_gitlab_kicad_libraries_kicad_footprints/Resistor_SMD.pretty",
                "R_0603_1608Metric"), x, y, r, flip)
        item.SetReference(ref)
        item.SetValue(val)
        item.FindPadByName(1).SetNet(net_a)
        item.FindPadByName(2).SetNet(net_b)
        return item


    yield resistor(*offset(x,y,r,-2.8,10,90),"R6","5.1 kΩ",net_usb_cc1, ground_net)
    yield resistor(*offset(x,y,r,2.8,10,90),"R7","5.1 kΩ",net_usb_cc2, ground_net)


    # esd protection
    # https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diode_arrays/littelfuse_tvs_diode_array_sr05_datasheet.pdf.pdf
    item = place_module(
        load_footprint(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Package_TO_SOT_SMD.pretty",
            "SOT-143"), *offset(x,y,r,0,12,0), flip)
    item.SetReference(f"U3")
    item.SetValue("SR05")
    item.FindPadByName(1).SetNet(ground_net)
    item.FindPadByName(2).SetNet(net_usb_minus)
    item.FindPadByName(3).SetNet(net_usb_plus)
    item.FindPadByName(4).SetNet(net_usb_vbus)
    yield item



def add_stm32(x, y, r, parent, ground_net, net_usb_plus, net_usb_minus, net_usb_vbus, io_nets, flip=False):
    net_mcu_vcc = pcbnew.NETINFO_ITEM(parent, f"vcc")
    parent.Add(net_mcu_vcc)
    net_mcu_boot = pcbnew.NETINFO_ITEM(parent, f"boot")
    parent.Add(net_mcu_boot)
    net_mcu_reset = pcbnew.NETINFO_ITEM(parent, f"reset")
    parent.Add(net_mcu_reset)

    net_swd_swdio = pcbnew.NETINFO_ITEM(parent, f"swdio")
    parent.Add(net_swd_swdio)
    net_swd_swdclk = pcbnew.NETINFO_ITEM(parent, f"swdclk")
    parent.Add(net_swd_swdclk)


    def offset(x1,y1,r1,x2,y2,r2):
        return (x1 + x2 * cos(radians(r1)) - y2 * sin(radians(r1)),
                y1 + y2 * cos(radians(r1)) + x2 * sin(radians(r1)),
                r1 + r2)

    # stm32f072
    item = place_module(
        load_footprint(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Package_QFP.pretty",
            "LQFP-48_7x7mm_P0.5mm"), *offset(x,y,r,0,0,45), flip)
    item.SetReference(f"U1")
    item.SetValue("STM32F072C8T6")
    #raise RuntimeError(f"r={r} offset={offset(x,y,r,0,0,0)}")
    yield item

    for p in [8, 23, 35, 47]:
        item.FindPadByName(p).SetNet(ground_net)
    for p in [1, 9, 24, 36, 48]:
        item.FindPadByName(p).SetNet(net_mcu_vcc)

    item.FindPadByName(7).SetNet(net_mcu_reset)
    item.FindPadByName(44).SetNet(net_mcu_boot)

    item.FindPadByName(34).SetNet(net_swd_swdio)
    item.FindPadByName(37).SetNet(net_swd_swdclk)
    item.FindPadByName(32).SetNet(net_usb_minus)
    item.FindPadByName(33).SetNet(net_usb_plus)

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

    # swd headers
    item = place_module(
        load_footprint(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Connector.pretty",
            "Tag-Connect_TC2030-IDC-FP_2x03_P1.27mm_Vertical"), *offset(x,y,r,0,19,0), flip)
    item.SetReference(f"J2")
    item.FindPadByName(1).SetNet(net_mcu_vcc)
    item.FindPadByName(2).SetNet(net_swd_swdio)
    item.FindPadByName(3).SetNet(net_mcu_reset)
    item.FindPadByName(4).SetNet(net_swd_swdclk)  # bad
    item.FindPadByName(5).SetNet(ground_net)
    yield item


    def resistor(x,y,r,ref,val,net_a,net_b):
        item = place_module(
            load_footprint(
                "external/com_gitlab_kicad_libraries_kicad_footprints/Resistor_SMD.pretty",
                "R_0603_1608Metric"), x, y, r, flip)
        item.SetReference(ref)
        item.SetValue(val)
        item.FindPadByName(1).SetNet(net_a)
        item.FindPadByName(2).SetNet(net_b)
        return item

    # boot resistor
    yield resistor(*offset(x,y,r,4.5,-4.5,225),"R1","10 kΩ",ground_net, net_mcu_boot)

    # mcu decoupling
    asdf=7
    yield resistor(*offset(x,y,r,asdf,0,90),"C1","0.1 uF",ground_net, net_mcu_vcc)
    yield resistor(*offset(x,y,r,-asdf,0,90),"C2","0.1 uF",net_mcu_vcc, ground_net)
    #yield resistor(*offset(x,y,r,0,asdf,0),"C3","0.1 uF",net_mcu_vcc, ground_net)
    yield resistor(*offset(x,y,r,0,-asdf,0),"C3","0.1 uF",ground_net,net_mcu_vcc)

    # voltage regulator
    item = place_module(
        load_footprint(
            "external/com_gitlab_kicad_libraries_kicad_footprints/Package_TO_SOT_SMD.pretty",
            "SOT-23"), x, y + 10, r, flip)
    item.SetReference(f"U2")
    item.SetValue("MCP1700T-3302E/TT")
    item.FindPadByName(1).SetNet(ground_net)
    item.FindPadByName(2).SetNet(net_mcu_vcc)
    item.FindPadByName(3).SetNet(net_usb_vbus)
    yield item

    ## TODO: voltage regulator caps



def add_mx_switch(x, y, r, parent, key, i, net1, net2):
    stab_size = 1
    rotate_switch = 0
    rotate_stab = 0

    # if key is wide then add stab
    if key.unit_width > 1 and key.unit_height == 1:
        rotate_stab = -180
        stab_size = key.unit_width

    # if key is tall then rotate switch and add stab
    if key.unit_width == 1 and key.unit_height > 1:
        rotate_switch = 90
        rotate_stab = -90
        stab_size = key.unit_height

    # net to connect diode to switch
    net = pcbnew.NETINFO_ITEM(parent, f"switch-diode-{i}")
    yield net

    item = pcbnew.FootprintLoad(
        os.path.join(os.path.dirname(__file__), "kicad_modules"),
        "SW_Cherry_MX_PCB")

    item.SetPosition(pcbnew.wxPointMM(x, y))
    item.SetOrientationDegrees(180 - r + rotate_switch)

    item.SetReference(f"SW{i}")
    item.FindPadByName(2).SetNet(net)
    item.FindPadByName(1).SetNet(net1)
    item.Reference().SetKeepUpright(False)

    for g in item.GraphicalItems():
        if isinstance(g, pcbnew.EDA_TEXT):
            g.SetKeepUpright(False)

    yield item

    if stab_size == 1:
        pass
    elif stab_size == 2:
        item = pcbnew.FootprintLoad("kbtb/kicad_modules",
                                    "Stab_Cherry_MX_2.00u_PCB")
        item.SetPosition(pcbnew.wxPointMM(x, y))
        item.SetOrientationDegrees(180 - r + rotate_stab)
        item.SetReference(f"ST{i}")
        yield item
    elif stab_size == 6.25:
        item = pcbnew.FootprintLoad("kbtb/kicad_modules",
                                    "Stab_Cherry_MX_6.25u_PCB")
        item.SetPosition(pcbnew.wxPointMM(x, y))
        item.SetOrientationDegrees(180 - r + rotate_stab)
        item.SetReference(f"ST{i}")
        yield item
    else:
        raise RuntimeError(f"unknown stabilizer size: {stab_size}")

    item = pcbnew.FootprintLoad(
        "external/com_gitlab_kicad_libraries_kicad_footprints/Diode_SMD.pretty",
        "D_SOD-123")
    item.MoveAnchorPosition(pcbnew.wxPointMM(2.5, -6.5))
    item.SetPosition(pcbnew.wxPointMM(x, y))
    item.SetOrientationDegrees(180 + r)
    item.SetReference(f"D{i}")
    item.SetValue("4148")
    item.Flip(pcbnew.wxPointMM(x, y), True)
    item.FindPadByName(1).SetNet(net)
    item.FindPadByName(2).SetNet(net2)
    item.Reference().SetKeepUpright(False)
    for g in item.GraphicalItems():
        if isinstance(g, pcbnew.EDA_TEXT):
            g.SetKeepUpright(False)
        else:
            g.DeleteStructure()
    yield item


def generate_kicad_pcb_file(kb):
    """Create a KiCad pcb file that implements the provided keyboard.

    This function is limited by the capabilities of PCB, but the idea is to
    build out as much of the PCB as we can from the provided keyboard object.

    This function will generate and return a two-layer PCB with it's outline
    built according to `kb.outline_polygon` (with matching ground planes) and
    with footprints for the switches, diodes, microcontroller, and mounting
    holes. The keyboard matrix will be used to configure connections between
    the switches, diodes, and MCU pins.

    A few KiCad-based limitations:

    * The default trace width is loaded from a KiCad project file which is not
      generated here, therefore the default trace width will need to be
      configured manually.
    * The `pcbnew.ZONE_FILLER` is not available when running standalone.
    """
    outline = shapely.geometry.polygon.Polygon(
        (o.x, o.y) for o in kb.outline_polygon)
    x_min, y_min, x_max, y_max = outline.bounds

    x_offset = 16 - x_min
    x_scale = 1
    y_offset = 16 + y_max
    y_scale = -1

    board = pcbnew.BOARD()

    ground_net = pcbnew.NETINFO_ITEM(board, f"GND")
    board.Add(ground_net)

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

    if kb.footprint == Keyboard.FOOTPRINT_CHERRY_MX:
        for i, key in enumerate(kb.keys):
            net1 = io_nets[key.controller_pin_low]
            net2 = io_nets[key.controller_pin_high]
            x, y = x_scale * key.pose.x + x_offset, y_scale * key.pose.y + y_offset

            r = degrees(
                atan2(y_scale * sin(radians(key.pose.r - 90)),
                      x_scale * cos(radians(key.pose.r - 90)))) + 90

            for x in add_mx_switch(x, y, r, board, key, i, net1, net2):
                board.Add(x)
    else:
        raise RuntimeError(f"unknown footprint")

    if kb.controller == Keyboard.CONTROLLER_PROMICRO:
        x, y = x_scale * kb.controller_pose.x + x_offset, y_scale * kb.controller_pose.y + y_offset
        r = degrees(
            atan2(y_scale * sin(radians(kb.controller_pose.r - 90)),
                  x_scale * cos(radians(kb.controller_pose.r - 90))))
        board.Add(add_pro_micro(x, y, r, board, ground_net, io_nets))
    elif kb.controller == Keyboard.CONTROLLER_STM32F072:

        def scale(x,y,r,x_scale=x_scale, y_scale=y_scale, x_offset=x_offset, y_offset=y_offset):
            x, y = x_scale * x + x_offset, y_scale * y + y_offset
            r = degrees(
                atan2(y_scale * sin(radians(r)),
                    x_scale * cos(radians(r))))
            return x,y,r

        net_usb_plus = pcbnew.NETINFO_ITEM(board, f"usb-dp")
        board.Add(net_usb_plus)
        net_usb_minus = pcbnew.NETINFO_ITEM(board, f"usb-dm")
        board.Add(net_usb_minus)
        net_usb_vbus = pcbnew.NETINFO_ITEM(board, f"usb-vcc")
        board.Add(net_usb_vbus)

        x,y,r=scale(kb.connector_pose.x,kb.connector_pose.y,kb.connector_pose.r)
        for x in add_usbc_legacy(x, y, r, board, ground_net, net_usb_plus, net_usb_minus, net_usb_vbus, flip=True):
            board.Add(x)
        # project controller pose to outline (consider doing this in board generation)


        x,y,r=scale(kb.controller_pose.x,kb.controller_pose.y,kb.controller_pose.r)
        for x in add_stm32(x, y, r, board, ground_net, net_usb_plus, net_usb_minus, net_usb_vbus, io_nets, flip=True):
            board.Add(x)
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
    # item.SetFillMode(pcbnew.ZONE_FILL_MODE_HATCH_PATTERN)
    # item.SetHatchThickness(pcbnew.FromMM(1))
    # item.SetHatchGap(pcbnew.FromMM(5))
    # item.SetHatchOrientation(45)
    # item.SetHatchSmoothingLevel(3)
    # item.SetHatchSmoothingValue(1)

    board.Add(item)

    tf = tempfile.NamedTemporaryFile()
    board.Save(tf.name)
    return tf
