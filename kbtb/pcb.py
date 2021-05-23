import os
import tempfile
from math import atan2, cos, degrees, radians, sin

import pcbnew
import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard
from kbtb.kicad import kicad_circle, kicad_polygon, kicad_add_text, set_pcb_position, PCBPosition


def offset(pose: PCBPosition, x, y, r=0, flip=False):
    return PCBPosition(
        pose.x + cos(radians(pose.r)) * x - sin(radians(pose.r)) * y,
        pose.y + cos(radians(pose.r)) * y + sin(radians(pose.r)) * x,
        pose.r + r, pose.flip ^ flip)


# pcbnew.FootprintLoad fails silently so use this function instead.
def load_footprint(library, name):
    footprint = pcbnew.FootprintLoad(
        os.path.join(os.environ.get("RUNFILES_DIR", "external/"), library),
        name)
    if not footprint:
        raise ValueError(
            f"can not load footprint {name} from library {library}")
    return footprint


def set_next_prefix(board, footprint, prefix):
    other = [x.GetReference() for x in board.GetFootprints()]
    x = 1
    while f"{prefix}{x}" in other:
        x = x + 1
    footprint.SetReference(f"{prefix}{x}")


def resistor(val, net_a, net_b):
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Resistor_SMD.pretty",
        "R_0603_1608Metric")
    item.SetValue(val)
    item.FindPadByName(1).SetNet(net_a)
    item.FindPadByName(2).SetNet(net_b)
    return item


def add_pro_micro(pose: PCBPosition, board, ground_net, io_nets):
    mcu_offset = 17.78 - 9.525
    controller = load_footprint("com_github_keebio_keebio_parts",
                                "ArduinoProMicro")

    set_pcb_position(controller, offset(pose, 0, mcu_offset, 90))
    set_next_prefix(board, controller, "U")

    # TODO: make this change to actual footprint instead of hacking it here
    for g in controller.GraphicalItems():
        layer = g.GetLayer()
        # delete everything from top
        if layer == 37:
            if isinstance(g, pcbnew.EDA_TEXT):
                g.SetVisible(False)
            else:
                g.DeleteStructure()

    for i in [3, 4, 23]:
        controller.FindPadByName(i).SetNet(ground_net)

    for i, net in enumerate(io_nets):
        [
            controller.FindPadByName(1),
            controller.FindPadByName(2),
            controller.FindPadByName(5),
            controller.FindPadByName(6),
            controller.FindPadByName(7),
            controller.FindPadByName(8),
            controller.FindPadByName(9),
            controller.FindPadByName(10),
            controller.FindPadByName(11),
            controller.FindPadByName(12),
            controller.FindPadByName(13),
            controller.FindPadByName(14),
            controller.FindPadByName(15),
            controller.FindPadByName(16),
            controller.FindPadByName(17),
            controller.FindPadByName(18),
            controller.FindPadByName(19),
            controller.FindPadByName(20),
        ][i].SetNet(net)

    board.Add(controller)


# Add a USB Type-C connector configured as a Legacy Device Adapter.
def add_usbc_legacy(pose: PCBPosition, board, ground_net, usb_nets):
    net_usb_dp, net_usb_dn, net_usb_vbus = usb_nets

    net_usb_cc1 = pcbnew.NETINFO_ITEM(board, f"usb-cc1")
    board.Add(net_usb_cc1)
    net_usb_cc2 = pcbnew.NETINFO_ITEM(board, f"usb-cc2")
    board.Add(net_usb_cc2)

    # usb type-c connector
    item = load_footprint(
        "com_github_ai03_2725_typec",
        "HRO-TYPE-C-31-M-12",
    )
    set_pcb_position(item, offset(pose, 0, 0, 0))
    set_next_prefix(board, item, "J")
    item.Reference().SetVisible(False)
    item.Value().SetVisible(False)
    item.FindPadByName(1).SetNet(ground_net)
    item.FindPadByName(2).SetNet(net_usb_vbus)
    #item.FindPadByName(3).SetNet() # sbu2
    item.FindPadByName(4).SetNet(net_usb_cc1)
    item.FindPadByName(5).SetNet(net_usb_dn)
    item.FindPadByName(6).SetNet(net_usb_dp)
    item.FindPadByName(7).SetNet(net_usb_dn)
    item.FindPadByName(8).SetNet(net_usb_dp)
    #item.FindPadByName(9).SetNet() # sbu1
    item.FindPadByName(10).SetNet(net_usb_cc2)
    item.FindPadByName(11).SetNet(net_usb_vbus)
    item.FindPadByName(12).SetNet(ground_net)
    #item.FindPadByName(13).SetNet()  # shield
    board.Add(item)

    ## usb cc resistors
    item = resistor("5.1 kΩ", ground_net, net_usb_cc1)
    set_pcb_position(item, offset(pose, -1.9, 10, 0))
    set_next_prefix(board, item, "R")
    board.Add(item)
    item = resistor("5.1 kΩ", net_usb_cc2, ground_net)
    set_pcb_position(item, offset(pose, 1.9, 10, 0))
    set_next_prefix(board, item, "R")
    board.Add(item)

    # esd protection
    # https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diode_arrays/littelfuse_tvs_diode_array_sr05_datasheet.pdf.pdf
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Package_TO_SOT_SMD.pretty",
        "SOT-143")
    set_pcb_position(item, offset(pose, 0, 13.25, 90))
    set_next_prefix(board, item, "U")
    item.SetValue("SR05")
    item.FindPadByName(1).SetNet(ground_net)
    item.FindPadByName(2).SetNet(net_usb_dn)
    item.FindPadByName(3).SetNet(net_usb_dp)
    item.FindPadByName(4).SetNet(net_usb_vbus)
    board.Add(item)


def add_stm32(pose: PCBPosition, board, ground_net, usb_nets, io_nets):
    # signals for swd debug
    net_mcu_reset = pcbnew.NETINFO_ITEM(board, f"reset")
    board.Add(net_mcu_reset)
    net_swd_swdio = pcbnew.NETINFO_ITEM(board, f"swdio")
    board.Add(net_swd_swdio)
    net_swd_swdclk = pcbnew.NETINFO_ITEM(board, f"swdclk")
    board.Add(net_swd_swdclk)

    # this section is powered by usb and includes a voltage regulator
    net_usb_dp, net_usb_dn, net_usb_vbus = usb_nets
    net_mcu_vcc = pcbnew.NETINFO_ITEM(board, f"vcc")
    board.Add(net_mcu_vcc)

    # stm32f072
    # https://www.st.com/resource/en/datasheet/stm32f072c8.pdf
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Package_QFP.pretty",
        "LQFP-48_7x7mm_P0.5mm")
    set_pcb_position(item, offset(pose, 0, 0, 180 + 45))
    set_next_prefix(board, item, "U")
    item.SetValue("STM32F072C8T6")
    board.Add(item)

    for p in [8, 23, 35, 44, 47]:  # VSS/VSSA/BOOT0
        item.FindPadByName(p).SetNet(ground_net)
    for p in [1, 9, 24, 36, 48]:  # VDD/VDDA
        item.FindPadByName(p).SetNet(net_mcu_vcc)

    item.FindPadByName(7).SetNet(net_mcu_reset)  # NRST

    item.FindPadByName(34).SetNet(net_swd_swdio)  # PA13
    item.FindPadByName(37).SetNet(net_swd_swdclk)  # PA14
    item.FindPadByName(32).SetNet(net_usb_dn)  # PA11
    item.FindPadByName(33).SetNet(net_usb_dp)  # PA12

    for i, net in enumerate(io_nets):
        [
            item.FindPadByName(2),  # C13 pin 2
            item.FindPadByName(3),  # C14
            item.FindPadByName(4),  # C15
            item.FindPadByName(5),  # F0
            item.FindPadByName(6),  # F1
            item.FindPadByName(10),  # A0 pin 10
            item.FindPadByName(11),  # A1
            item.FindPadByName(12),  # A2
            item.FindPadByName(13),  # A3 pin 13
            item.FindPadByName(14),  # A4
            item.FindPadByName(15),  # A5
            item.FindPadByName(16),  # A6
            item.FindPadByName(17),  # A7
            item.FindPadByName(18),  # B0
            item.FindPadByName(19),  # B1
            item.FindPadByName(20),  # B2
            item.FindPadByName(21),  # B10
            item.FindPadByName(22),  # B11
            item.FindPadByName(25),  # B12 pin 25
            item.FindPadByName(26),  # B13
            item.FindPadByName(27),  # B14
            item.FindPadByName(28),  # B15
            item.FindPadByName(29),  # A8
            item.FindPadByName(30),  # A9
            item.FindPadByName(31),  # A10
            item.FindPadByName(32),  # A11
            item.FindPadByName(33),  # A12
            item.FindPadByName(34),  # A13
            item.FindPadByName(39),  # B3 pin 39
            item.FindPadByName(40),  # B4
            item.FindPadByName(41),  # B5
            item.FindPadByName(42),  # B6
            item.FindPadByName(43),  # B7
            item.FindPadByName(45),  # B8 pin 45
            item.FindPadByName(46),  # B9
        ][i].SetNet(net)

    # debug connector
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Connector.pretty",
        "Tag-Connect_TC2030-IDC-FP_2x03_P1.27mm_Vertical")
    set_pcb_position(item, offset(pose, 0, 19, -90))
    set_next_prefix(board, item, "J")
    item.Value().SetVisible(False)
    item.Reference().SetVisible(False)
    item.FindPadByName(1).SetNet(net_mcu_vcc)
    item.FindPadByName(2).SetNet(net_swd_swdio)
    item.FindPadByName(3).SetNet(net_mcu_reset)
    item.FindPadByName(4).SetNet(net_swd_swdclk)
    item.FindPadByName(5).SetNet(ground_net)
    board.Add(item)

    # mcu decoupling
    item = resistor("0.1 µF", ground_net, net_mcu_vcc)
    set_pcb_position(item, offset(pose, 7, 0, 90))
    set_next_prefix(board, item, "C")
    board.Add(item)
    item = resistor("0.1 µF", net_mcu_vcc, ground_net)
    set_pcb_position(item, offset(pose, -7, 0, 90))
    set_next_prefix(board, item, "C")
    board.Add(item)
    item = resistor("0.1 µF", net_mcu_vcc, ground_net)
    set_pcb_position(item, offset(pose, 0, -7, 0))
    set_next_prefix(board, item, "C")
    board.Add(item)
    item = resistor("0.1 µF", ground_net, net_mcu_vcc)
    set_pcb_position(item, offset(pose, 0, 7, 0))
    set_next_prefix(board, item, "C")
    board.Add(item)

    # voltage regulator
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Package_TO_SOT_SMD.pretty",
        "SOT-23")
    set_pcb_position(item, offset(pose, 0, -10, 0))
    set_next_prefix(board, item, "U")
    item.SetValue("MCP1700T-3302E/TT")
    item.FindPadByName(1).SetNet(ground_net)
    item.FindPadByName(2).SetNet(net_mcu_vcc)
    item.FindPadByName(3).SetNet(net_usb_vbus)
    board.Add(item)

    ## TODO: add voltage regulator caps


def add_atmega32u4(pose: PCBPosition, board, ground_net, usb_nets, io_nets):
    # signals for icsp debug
    net_icsp_reset = pcbnew.NETINFO_ITEM(board, f"icsp-reset")
    board.Add(net_icsp_reset)
    net_icsp_mosi = pcbnew.NETINFO_ITEM(board, f"icsp-mosi")
    board.Add(net_icsp_mosi)
    net_icsp_miso = pcbnew.NETINFO_ITEM(board, f"icsp-miso")
    board.Add(net_icsp_miso)
    net_icsp_sck = pcbnew.NETINFO_ITEM(board, f"icsp-sck")
    board.Add(net_icsp_sck)

    net_mcu_xtal1 = pcbnew.NETINFO_ITEM(board, f"xtal1")
    board.Add(net_mcu_xtal1)
    net_mcu_xtal2 = pcbnew.NETINFO_ITEM(board, f"xtal2")
    board.Add(net_mcu_xtal2)
    net_mcu_ucap = pcbnew.NETINFO_ITEM(board, f"ucap")
    board.Add(net_mcu_ucap)

    # this section is powered by usb
    net_usb_dp, net_usb_dn, net_usb_vbus = usb_nets
    # TODO: directly connecing vbus to vcc seems non-ideal
    net_mcu_vcc = net_usb_vbus  # pcbnew.NETINFO_ITEM(board, f"vcc")
    #board.Add(net_mcu_vcc)

    # vbus filter
    item = resistor("10 µF", ground_net, net_usb_vbus)
    set_pcb_position(item, offset(pose, 0, -13, 0))
    set_next_prefix(board, item, "C")
    board.Add(item)

    # atmega32u4
    # https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7766-8-bit-AVR-ATmega16U4-32U4_Datasheet.pdf
    # https://cdn.sparkfun.com/datasheets/Dev/Arduino/Boards/Pro_Micro_v13b.pdf
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Package_QFP.pretty",
        "TQFP-44_10x10mm_P0.8mm")
    set_pcb_position(item, offset(pose, 0, 0, 45 + 90))
    set_next_prefix(board, item, "U")
    item.SetValue("ATMEGA32U4-AU")

    for p in [5, 15, 23, 35, 43, 33]:  # UGND/GND/^HWB
        item.FindPadByName(p).SetNet(ground_net)
    for p in [14, 24, 34, 44]:  # VCC
        item.FindPadByName(p).SetNet(net_mcu_vcc)
    for p in [7, 2]:  # VBUS/UVCC
        item.FindPadByName(p).SetNet(net_usb_vbus)

    item.FindPadByName(3).SetNet(net_usb_dn)
    item.FindPadByName(4).SetNet(net_usb_dp)

    item.FindPadByName(6).SetNet(net_mcu_ucap)

    # icsp pins
    item.FindPadByName(9).SetNet(net_icsp_sck)
    item.FindPadByName(10).SetNet(net_icsp_mosi)
    item.FindPadByName(11).SetNet(net_icsp_miso)
    item.FindPadByName(13).SetNet(net_icsp_reset)

    # crystal pins
    item.FindPadByName(17).SetNet(net_mcu_xtal1)
    item.FindPadByName(16).SetNet(net_mcu_xtal2)

    for i, net in enumerate(io_nets):
        [
            item.FindPadByName(8),  # PB0
            item.FindPadByName(12),  # PB7
            item.FindPadByName(18),  # PD0
            item.FindPadByName(19),  # PD1
            item.FindPadByName(20),  # PD2
            item.FindPadByName(21),  # PD3
            item.FindPadByName(22),  # PD5
            item.FindPadByName(25),  # PD4
            item.FindPadByName(26),  # PD6
            item.FindPadByName(27),  # PD7
            item.FindPadByName(28),  # PB4
            item.FindPadByName(29),  # PB5
            item.FindPadByName(30),  # PB6
            item.FindPadByName(31),  # PC6
            item.FindPadByName(32),  # PC7
            item.FindPadByName(36),  # PF7
            item.FindPadByName(37),  # PF6
            item.FindPadByName(38),  # PF5
            item.FindPadByName(39),  # PF4
            item.FindPadByName(40),  # PF1
            item.FindPadByName(41),  # PF0
            item.FindPadByName(1),  # PE6
        ][i].SetNet(net)
    board.Add(item)

    # stack of 0603 components on the right
    right_cluster = offset(pose, 10.4, 2, 45)

    # crystal
    crystal_pose = offset(pose, 0, 13, 90)
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Crystal.pretty",
        "Crystal_SMD_3225-4Pin_3.2x2.5mm")
    # should we use hand-solderable footprint here?
    set_pcb_position(item, offset(crystal_pose, 0, 0, 0))
    set_next_prefix(board, item, "X")
    item.SetValue("16 MHz")
    item.FindPadByName(1).SetNet(net_mcu_xtal1)
    item.FindPadByName(2).SetNet(ground_net)
    item.FindPadByName(3).SetNet(net_mcu_xtal2)
    item.FindPadByName(4).SetNet(ground_net)
    board.Add(item)
    item = resistor("22 pF", net_mcu_xtal1, ground_net)
    set_pcb_position(item, offset(crystal_pose, 0, -2.45))
    set_next_prefix(board, item, "C")
    board.Add(item)
    item = resistor("22 pF", net_mcu_xtal2, ground_net)
    set_pcb_position(item, offset(crystal_pose, 0, 2.45))
    set_next_prefix(board, item, "C")
    board.Add(item)

    # debug connector
    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Connector.pretty",
        "Tag-Connect_TC2030-IDC-FP_2x03_P1.27mm_Vertical")
    set_pcb_position(item, offset(pose, 0, 19, -90))
    set_next_prefix(board, item, "Jx")
    item.Value().SetVisible(False)
    item.Reference().SetVisible(False)
    item.FindPadByName(1).SetNet(net_icsp_miso)
    item.FindPadByName(2).SetNet(net_mcu_vcc)
    item.FindPadByName(3).SetNet(net_icsp_sck)
    item.FindPadByName(4).SetNet(net_icsp_mosi)
    item.FindPadByName(5).SetNet(net_icsp_reset)
    item.FindPadByName(6).SetNet(ground_net)
    board.Add(item)

    # ucap
    item = resistor("1 µF", ground_net, net_mcu_ucap)
    set_pcb_position(item, offset(pose, 11 - (2.12 * 2.5), -(2.12 * 2.5), 45))
    set_next_prefix(board, item, "C")
    board.Add(item)

    # reset pullup
    item = resistor("10 kΩ", net_mcu_vcc, net_icsp_reset)
    set_pcb_position(item, offset(pose, 11 - (2.12 * 1), (2.12 * 1), -45))
    set_next_prefix(board, item, "R")
    board.Add(item)

    # mcu decoupling
    item = resistor("0.1 µF", ground_net, net_mcu_vcc)
    set_pcb_position(item, offset(pose, 11 - (2.12 * 2), (2.12 * 2), -45))
    set_next_prefix(board, item, "C")
    board.Add(item)
    item = resistor("0.1 µF", net_mcu_vcc, ground_net)
    set_pcb_position(item, offset(pose, -11 + (2.12 * 4), (2.12 * 4), 45))
    set_next_prefix(board, item, "C")
    board.Add(item)
    item = resistor("0.1 µF", ground_net, net_mcu_vcc)
    set_pcb_position(item, offset(pose, -11 + (2.12 * 4), -(2.12 * 4), -45))
    set_next_prefix(board, item, "C")
    board.Add(item)
    item = resistor("0.1 µF", net_mcu_vcc, ground_net)
    set_pcb_position(item, offset(pose, -11 + (2.12 * 1), -(2.12 * 1), -45))
    set_next_prefix(board, item, "C")
    board.Add(item)

    # TODO: add power led?


def add_mx_switch(pose: PCBPosition, board, key, i, net1, net2):

    # net to connect diode to switch
    net = pcbnew.NETINFO_ITEM(board, f"switch-diode-{i}")
    board.Add(net)

    item = load_footprint(
        "com_github_kleinpa_keyboardtoolbox/kbtb/kicad_modules",
        "SW_Cherry_MX_PCB")
    set_pcb_position(item, offset(pose, 0, 0, key.switch_r))
    item.SetReference(f"SW{i}")
    item.Value().SetVisible(False)
    item.Reference().SetKeepUpright(False)
    item.FindPadByName(2).SetNet(net)
    item.FindPadByName(1).SetNet(net1)

    board.Add(item)

    item = load_footprint(
        "com_gitlab_kicad_libraries_kicad_footprints/Diode_SMD.pretty",
        "D_SOD-123")
    set_pcb_position(item, offset(pose, -3.5, -5.5, 180, flip=True))
    set_next_prefix(board, item, "D")
    item.SetValue("4148")
    item.Reference().SetKeepUpright(False)
    item.FindPadByName(1).SetNet(net)
    item.FindPadByName(2).SetNet(net2)
    board.Add(item)

    # Stabilizers are still a WIP. Orientation is hard to get right
    # automatically so it should probably be pushed up into keyboard.proto

    if key.HasField("stabilizer"):
        if key.stabilizer.size == 2:
            item = load_footprint(
                "com_github_kleinpa_keyboardtoolbox/kbtb/kicad_modules",
                "Stab_Cherry_MX_2.00u_PCB")
            set_pcb_position(item, offset(pose, 0, 0, -key.stabilizer.r))
            item.SetReference(f"ST{i}")
            item.Value().SetVisible(False)
            item.Reference().SetVisible(False)
            board.Add(item)

        elif key.stabilizer.size == 6.25:
            item = load_footprint(
                "com_github_kleinpa_keyboardtoolbox/kbtb/kicad_modules",
                "Stab_Cherry_MX_6.25u_PCB")
            set_pcb_position(item, offset(pose, 0, 0, -key.stabilizer.r))
            item.SetReference(f"ST{i}")
            item.Value().SetVisible(False)
            item.Reference().SetVisible(False)
            board.Add(item)
        else:
            raise RuntimeError(
                f"unknown stabilizer size: {key.stabilizer.size}")


def generate_kicad_pcb_file(kb, stamp_hash=None):
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
    outline = shapely.geometry.polygon.Polygon(
        (o.x, o.y) for o in kb.outline_polygon)
    x_min, y_min, x_max, y_max = outline.bounds

    x_offset = 16 - x_min
    x_scale = 1
    y_offset = 16 + y_max
    y_scale = -1

    # convert from keyboard.proto coordinates to PCBPosition
    def scale(pose,
              x_scale=x_scale,
              y_scale=y_scale,
              x_offset=x_offset,
              y_offset=y_offset,
              flip=False):
        x, y = x_scale * pose.x + x_offset, y_scale * pose.y + y_offset
        r = degrees(
            atan2(y_scale * sin(radians(pose.r)),
                  x_scale * cos(radians(pose.r))))
        return PCBPosition(x, y, r, flip)

    board = pcbnew.BOARD()

    ground_net = pcbnew.NETINFO_ITEM(board, f"GND")
    board.Add(ground_net)

    for x in kicad_polygon(
            outline,
            x_offset=x_offset,
            y_offset=y_offset,
            x_scale=x_scale,
            y_scale=y_scale):
        board.Add(x)

    matrix_pins = set([
        *[key.controller_pin_low for key in kb.keys],
        *[key.controller_pin_high for key in kb.keys]
    ])

    matrix_nets = dict(
        (p, pcbnew.NETINFO_ITEM(board, f"matrix-{p}")) for p in matrix_pins)
    for x in matrix_nets.values():
        board.Add(x)

    if kb.switch == Keyboard.SWITCH_CHERRY_MX:
        for i, key in enumerate(kb.keys):
            add_mx_switch(
                scale(key.pose), board, key, i,
                matrix_nets[key.controller_pin_low],
                matrix_nets[key.controller_pin_high])
    else:
        raise RuntimeError(f"unknown footprint")

    if kb.controller == Keyboard.CONTROLLER_PROMICRO:
        # For the pro
        add_pro_micro(
            scale(kb.controller_pose, flip=True), board, ground_net,
            matrix_nets.values())
    elif kb.controller == Keyboard.CONTROLLER_STM32F072:
        net_usb_dp = pcbnew.NETINFO_ITEM(board, f"usb-dp")
        board.Add(net_usb_dp)
        net_usb_dn = pcbnew.NETINFO_ITEM(board, f"usb-dn")
        board.Add(net_usb_dn)
        net_usb_vbus = pcbnew.NETINFO_ITEM(board, f"usb-vcc")
        board.Add(net_usb_vbus)
        usb_nets = net_usb_dp, net_usb_dn, net_usb_vbus

        add_usbc_legacy(
            scale(kb.connector_pose, flip=True), board, ground_net, usb_nets)

        add_stm32(
            scale(kb.controller_pose, flip=True), board, ground_net, usb_nets,
            matrix_nets.values())
    elif kb.controller == Keyboard.CONTROLLER_ATMEGA32U4:
        net_usb_dp = pcbnew.NETINFO_ITEM(board, f"usb-dp")
        board.Add(net_usb_dp)
        net_usb_dn = pcbnew.NETINFO_ITEM(board, f"usb-dn")
        board.Add(net_usb_dn)
        net_usb_vbus = pcbnew.NETINFO_ITEM(board, f"usb-vcc")
        board.Add(net_usb_vbus)
        usb_nets = net_usb_dp, net_usb_dn, net_usb_vbus

        add_usbc_legacy(
            scale(kb.connector_pose, flip=True), board, ground_net, usb_nets)

        add_atmega32u4(
            scale(kb.controller_pose, flip=True), board, ground_net, usb_nets,
            matrix_nets.values())
    else:
        raise RuntimeError("unknown controller")

    if kb.info_text:

        text = kb.info_text.replace("{git}", stamp_hash or "unknown")

        kicad_add_text(board, scale(kb.info_pose, flip=True), text, size=1.3)

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

    # Use hatched fill because it looks cool
    # item.SetFillMode(pcbnew.ZONE_FILL_MODE_HATCH_PATTERN)
    # item.SetHatchThickness(pcbnew.FromMM(1))
    # item.SetHatchGap(pcbnew.FromMM(5))
    # item.SetHatchOrientation(45)
    # item.SetHatchSmoothingLevel(3)
    # item.SetHatchSmoothingValue(1)

    board.Add(item)

    with tempfile.NamedTemporaryFile() as tf:
        board.Save(tf.name)
        return tf.read()
