from math import atan2, cos, degrees, radians, sin

import shapely.geometry

from kbtb.keyboard_pb2 import Keyboard
from kbtb.kicad import PcbPosition, PcbComponent, PcbSection, PcbCircle, PcbText, Board


def package_0603(val: str, pose: PcbPosition, ref):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Resistor_SMD.pretty:R_0603_1608Metric",
        reference_prefix=ref,
        pose=pose,
        value=val,
        pins=["a", "b"])


def resistor_0603(val: str, pose: PcbPosition):
    return package_0603(val, pose, "R")


def capacitor_0603(val: str, pose: PcbPosition):
    return package_0603(val, pose, "C")


def diode_sod323(val: str, pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Diode_SMD.pretty:D_SOD-323",
        reference_prefix="D",
        pose=pose,
        value=val,
        keep_upright=True,
        pins=["a", "b"])


def crystal_3225(value: str, pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Crystal.pretty:Crystal_SMD_3225-4Pin_3.2x2.5mm",
        "X",
        pose=pose,
        value=value,
        pins=["in", "ground", "out", "ground"],
    )


def tagconnect_2030(id: str, pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Connector.pretty:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical",
        reference_prefix="J",
        pose=pose,
        reference_visible=False,
        value_visible=False,
        pins=["1", "2", "3", "4", "5", "6"])


def promicro(pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_github_keebio_keebio_parts:ArduinoProMicro",
        reference_prefix="U",
        pose=pose,
        pins=[
            "d3", "d2", "ground", "ground", "d1", "d0", "d4", "c6", "d7", "e6",
            "b4", "b5", "b6", "b2", "b3", "b1", "f7", "f6", "f5", "f4", "vcc",
            "reset", "ground", "raw"
        ],
    )


def usbc_connector(pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_github_ai03_2725_typec:HRO-TYPE-C-31-M-12",
        "J",
        pose,
        reference_visible=False,
        value_visible=False,
        pins=[
            "ground", "vbus", "sbu2", "cc1", "dn", "dp", "dn", "dp", "sbu1",
            "cc2", "vbus", "ground", "shield"
        ])


def usb_esd_protection(pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Package_SON.pretty:USON-10_2.5x1.0mm_P0.5mm",
        "U",
        pose=pose,
        value="TPD4E05U06DQAR",
        reference_visible=False,
        value_visible=False,
        pins=[
            "dp", "dn", "ground", "dp", "dn", "dn", "dp", "ground", "dn", "dp"
        ],
    )


def voltage_regulator_sot23(pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Package_TO_SOT_SMD.pretty:SOT-23",
        "U",
        pose=pose,
        value="MCP1700T-3302E/TT",
        pins=["ground", "vout", "vin"])


def atmega32u(pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Package_QFP.pretty:TQFP-44_10x10mm_P0.8mm",
        "U",
        pose=pose,
        value="ATMEGA32U4-AU",
        pins=[
            "pe6", "vcc", "dn", "dp", "ground", "ucap", "vcc", "pb0",
            "icsp_sck", "icsp_mosi", "icsp_miso", "pb7", "reset", "vcc",
            "ground", "xtal2", "xtal1", "pd0", "pd1", "pd2", "pd3", "pd5",
            "ground", "vcc", "pd4", "pd6", "pd7", "pb4", "pb5", "pb6", "pc6",
            "pc7", "ground", "vcc", "ground", "pf7", "pf6", "pf5", "pf4",
            "pf1", "pf0", "pin-42", "ground", "vcc"
        ])


def stm32f072(pose: PcbPosition):
    return PcbComponent(
        "_main~repos_bzlmod~com_gitlab_kicad_libraries_kicad_footprints/Package_QFP.pretty:LQFP-48_7x7mm_P0.5mm",
        "U",
        pose,
        value="STM32F072C8T6",
        pins=[
            "vcc", "c13", "c14", "c15", "f0", "f1", "reset", "ground", "vcc",
            "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "b0", "b1", "b2",
            "b10", "b11", "ground", "vcc", "b12", "b13", "b14", "b15", "a8",
            "a9", "a10", "a11", "a12", "a13", "ground", "vcc", "a14", "???",
            "b3", "b4", "b5", "b6", "b7", "ground", "b8", "b9", "ground", "vcc"
        ])


def mx_switch(pose: PcbPosition):
    return PcbComponent("keyboard_toolbox/kbtb/kicad_modules:SW_Cherry_MX_PCB",
                        "SW",
                        pose=pose,
                        value_visible=False,
                        reference_visible=False,
                        pins=["a", "b"])


def mx_stabilizer(size: float, pose: PcbPosition):
    if size == 2:
        return PcbComponent(
            "_main/kbtb/kicad_modules:Stab_Cherry_MX_2.00u_PCB",
            "ST",
            pose=pose,
            value_visible=False,
            reference_visible=False)
    elif size == 6.25:
        return PcbComponent(
            "_main/kbtb/kicad_modules:Stab_Cherry_MX_6.25u_PCB",
            "ST",
            pose=pose,
            value_visible=False,
            reference_visible=False)
    else:
        raise RuntimeError(f"unknown mx_stabilizer size: {size}")


# Everything above this line is not keyboard-specific
# TODO: move elsewhere


def usbc_legacy_hub(id: str,
                    pose: PcbPosition,
                    ds_poses: 'list[PcbPosition]' = []):
    cmp = PcbSection(id, {"ground", "u_vbus", "mcu_dp", "mcu_dn"}, {
        "u_dp", "u_dn", "u_cc1", "u_cc2", "d1_dp", "d1_dn", "d2_dp", "d2_dn",
        "vdd18_cap", "vdd33_cap", "d1_cc1", "d1_cc2", "d2_cc1", "d2_cc2",
        "xtal1", "xtal2"
    })

    cmp = cmp.add(
        usbc_connector(pose), {
            "ground": "ground",
            "vbus": "u_vbus",
            "dp": "u_dp",
            "dn": "u_dn",
            "cc1": "u_cc1",
            "cc2": "u_cc2",
        })

    # usb cc resistors
    cmp = cmp.add(resistor_0603("5.1 kΩ", pose.offset(-2.3, 10.5, 90)), {
        "a": "ground",
        "b": "u_cc1",
    })
    cmp = cmp.add(resistor_0603("5.1 kΩ", pose.offset(2.3, 10.5, 90)), {
        "b": "ground",
        "a": "u_cc2",
    })
    cmp = cmp.add(usb_esd_protection(pose.offset(0, 9.6, 90 + 180)), {
        "ground": "ground",
        "dp": "u_dp",
        "dn": "u_dn",
    })

    if len(ds_poses) >= 1:
        cmp = cmp.add(
            usbc_connector(ds_poses[0]), {
                "ground": "ground",
                "vbus": "u_vbus",
                "dp": "d1_dp",
                "dn": "d2_dn",
                "cc1": "d2_cc1",
                "cc2": "d2_cc2",
            })
        cmp = cmp.add(
            resistor_0603("56 kΩ", ds_poses[0].offset(-2.3, 10.5, 90)), {
                "a": "u_vbus",
                "b": "d2_cc1",
            })
        cmp = cmp.add(
            resistor_0603("56 kΩ", ds_poses[0].offset(2.3, 10.5, 90)), {
                "b": "u_vbus",
                "a": "d2_cc2",
            })
    if len(ds_poses) >= 2:
        cmp = cmp.add(
            usbc_connector(ds_poses[1]), {
                "ground": "ground",
                "vbus": "u_vbus",
                "dp": "d2_dp",
                "dn": "d2_dn",
                "cc1": "d2_cc1",
                "cc2": "d2_cc2",
            })
        cmp = cmp.add(
            resistor_0603("56 kΩ", ds_poses[1].offset(-2.3, 10.5, 90)), {
                "a": "ground",
                "b": "d2_cc1",
            })
        cmp = cmp.add(
            resistor_0603("56 kΩ", ds_poses[1].offset(2.3, 10.5, 90)), {
                "b": "ground",
                "a": "d2_cc2",
            })
    if len(ds_poses) >= 3:
        raise RuntimeError("unsupported number of downstream usb ports")

    def sl21a(pose: PcbComponent):
        return PcbComponent(
            "com_gitlab_kicad_libraries_kicad_footprints/Package_SO.pretty:SOP-16_3.9x9.9mm_P1.27mm",
            "X",
            pose=pose,
            value="SL2.1A",
            pins=[
                "dn4", "dp4", "dn3", "dp3", "dn2", "dp2", "dn1", "dp1", "dn",
                "dp", "vdd5", "gnd", "vdd33", "vdd18", "xout", "xin"
            ])

    hub_pose = pose.offset(x=10)
    cmp = cmp.add(  # hub chip SL2.1A
        sl21a(hub_pose), {
            "gnd": "ground",
            "vdd5": "u_vbus",
            "dp":"u_dp",
            "dn":"u_dn",
            "dp1": "mcu_dp",
            "dn1": "mcu_dn",
            "dp2": "d1_dp",
            "dn2": "d1_dn",
            "dp3": "d2_dp",
            "dn3": "d2_dn",
            "vdd18":"vdd18_cap",
            "vdd33":"vdd33_cap",
            "xout": "xtal1",
            "xin": "xtal2",
        })
    cmp = cmp.add(crystal_3225("12 MHz", hub_pose.offset(x=5)), {
        "ground": "ground",
        "in": "xtal1",
        "out": "xtal2",
    })

    cmp = cmp.add(capacitor_0603("10 µF", pose.offset(15)), {
        "a": "vdd18_cap",
        "b": "ground",
    })

    cmp = cmp.add(capacitor_0603("10 µF", pose.offset(20)), {
        "a": "vdd33_cap",
        "b": "ground",
    })
    cmp = cmp.add(capacitor_0603("10 µF", pose.offset(20)), {
        "a": "u_vbus",
        "b": "ground",
    })

    # TODO: downstream port power cap

    return cmp


def controller_pro_micro(id: str, pose: PcbPosition):
    matrix = ["matrix-{i}" for i in range(18)]
    cmp = PcbSection(id, {"ground"} | set(matrix))
    mcu_offset = 17.78 - 9.525

    cmp = cmp.add(
        promicro(pose.offset(0, mcu_offset, 90)), {
            "ground": "ground",
            "d3": matrix[0],
            "d2": matrix[1],
            "d1": matrix[2],
            "d0": matrix[3],
            "d4": matrix[4],
            "c6": matrix[5],
            "d7": matrix[6],
            "e6": matrix[7],
            "b4": matrix[8],
            "b5": matrix[9],
            "b6": matrix[10],
            "b2": matrix[11],
            "b3": matrix[12],
            "b1": matrix[13],
            "f7": matrix[14],
            "f6": matrix[15],
            "f5": matrix[16],
            "f4": matrix[17],
        })

    return cmp


# Add a USB Type-C connector configured as a Legacy Device Adapter.
def usbc_legacy(id: str, pose: PcbPosition):
    cmp = PcbSection(id, {"ground", "usb_vbus", "usb_dp", "usb_dn"},
                     {"cc1", "cc2"})

    cmp = cmp.add(
        usbc_connector(pose), {
            "ground": "ground",
            "vbus": "usb_vbus",
            "dp": "usb_dp",
            "dn": "usb_dn",
            "cc1": "cc1",
            "cc2": "cc2",
        })

    # usb cc resistors
    cmp = cmp.add(resistor_0603("5.1 kΩ", pose.offset(-2.3, 10.5, 90)), {
        "a": "ground",
        "b": "cc1",
    })
    cmp = cmp.add(resistor_0603("5.1 kΩ", pose.offset(2.3, 10.5, 90)), {
        "b": "ground",
        "a": "cc2",
    })
    cmp = cmp.add(usb_esd_protection(pose.offset(0, 9.6, 90 + 180)), {
        "ground": "ground",
        "dp": "usb_dp",
        "dn": "usb_dn",
    })
    return cmp


def controller_stm32(id: str, pose: PcbPosition):
    matrix = [f"matrix-{i}" for i in range(36)]
    cmp = PcbSection(
        id,
        {
            "ground",
            "usb_vbus",
            "usb_dp",
            "usb_dn",
        } | set(matrix),
        {
            "swdio",
            "swdclk",
            "reset",
            "mcu_vcc",
        },
    )

    # stm32f072
    # https://www.st.com/resource/en/datasheet/stm32f072c8.pdf
    io_pins = [
        "c13", "c14", "c15", "f0", "f1", "a0", "a1", "a2", "a3", "a4", "a5",
        "a6", "a7", "b0", "b1", "b2", "b10", "b11", "b12", "b13", "b14", "b15",
        "a8", "a9", "a10", "a13", "b3", "b4", "b5", "b6", "b7", "b8", "b9"
    ]
    cmp = cmp.add(
        stm32f072(pose.offset(r=180 + 45)), {
            "ground": "ground",
            "reset": "reset",
            "vcc": "mcu_vcc",
            "a11": "usb_dn",
            "a12": "usb_dp",
            "a13": "swdio",
            "a14": "swdclk",
            **dict(zip(io_pins, matrix))
        })

    cmp = cmp.add(  # debug connector
        tagconnect_2030("tc", pose.offset(0, 19, -90)), {
            "1": "mcu_vcc",
            "2": "swdio",
            "3": "reset",
            "4": "swdclk",
            "5": "ground"
        })

    # mcu decoupling
    cmp = cmp.add(capacitor_0603("0.1 µF", pose.offset(7, 0, 90)), {
        "a": "mcu_vcc",
        "b": "ground",
    })
    cmp = cmp.add(capacitor_0603("0.1 µF", pose.offset(-7, 0, 90)), {
        "a": "ground",
        "b": "mcu_vcc",
    })
    cmp = cmp.add(capacitor_0603("0.1 µF", pose.offset(0, -7, 0)), {
        "a": "mcu_vcc",
        "b": "ground",
    })
    cmp = cmp.add(capacitor_0603("0.1 µF", pose.offset(0, 7, 0)), {
        "a": "ground",
        "b": "mcu_vcc",
    })

    cmp = cmp.add(  # voltage regulator
        voltage_regulator_sot23(pose.offset(y=-10)), {
            "ground": "ground",
            "vin": "usb_vbus",
            "vout": "mcu_vcc"
        })

    ## TODO: add voltage regulator caps

    return cmp


def controller_atmega32u4(id: str, pose: PcbPosition):
    matrix = [f"matrix-{i}" for i in range(22)]
    cmp = PcbSection(id, {
        "ground",
        "usb_vbus",
        "usb_dp",
        "usb_dn",
    } | set(matrix), {
        "swdio",
        "swdclk",
        "reset",
        "mcu_vcc",
        "icsp_sck",
        "icsp_mosi",
        "icsp_miso",
        "ucap",
        "xtal1",
        'xtal2',
    })

    cmp = cmp.add(  # vbus filter
        capacitor_0603("10 µF",
                       pose.offset(11 - (2.12 * 4.5), -(2.12 * 4.5), 45)), {
                           "a": "ground",
                           "b": "usb_vbus",
                       })

    # atmega32u4
    # https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7766-8-bit-AVR-ATmega16U4-32U4_Datasheet.pdf
    # https://cdn.sparkfun.com/datasheets/Dev/Arduino/Boards/Pro_Micro_v13b.pdf
    cmp = cmp.add(
        atmega32u(pose.offset(r=45 + 90)), {
            "ground": "ground",
            "reset": "reset",
            "vcc": "usb_vbus",
            "icsp_sck": "icsp_sck",
            "icsp_mosi": "icsp_mosi",
            "icsp_miso": "icsp_miso",
            "ucap": "ucap",
            "xtal1": "xtal1",
            "xtal2": "xtal2",
            "pb0": "matrix-0",
            "pb7": "matrix-1",
            "pd0": "matrix-2",
            "pd1": "matrix-3",
            "pd2": "matrix-4",
            "pd3": "matrix-5",
            "pd5": "matrix-6",
            "pd4": "matrix-7",
            "pd6": "matrix-8",
            "pd7": "matrix-9",
            "pb4": "matrix-10",
            "pb5": "matrix-11",
            "pb6": "matrix-12",
            "pc6": "matrix-13",
            "pc7": "matrix-14",
            "pf7": "matrix-15",
            "pf6": "matrix-16",
            "pf5": "matrix-17",
            "pf4": "matrix-18",
            "pf1": "matrix-19",
            "pf0": "matrix-20",
            "pe6": "matrix-21",
        })
    # TODO: directly connecing vbus to vcc seems non-ideal [14, 24, 34, 44]

    # crystal
    crystal_pose = pose.offset(0, 13, 90)
    cmp = cmp.add(crystal_3225("16 MHz", crystal_pose), {
        "ground": "ground",
        "in": "xtal1",
        "out": "xtal2",
    })
    cmp = cmp.add(capacitor_0603("22 pF", crystal_pose.offset(y=-2.45)), {
        "a": "xtal1",
        "b": "ground",
    })
    cmp = cmp.add(capacitor_0603("22 pF", crystal_pose.offset(0, 2.45)), {
        "a": "xtal2",
        "b": "ground",
    })


    cmp=cmp.add(  # debug connector
        tagconnect_2030("tc", pose.offset( 0, 19, -90)), {
            "1": "icsp_miso",
            "2": "usb_vbus",
            "3": "icsp_sck",
            "4": "icsp_mosi",
            "5": "reset",
            "6": "ground",
        })
    cmp = cmp.add(  # ucap
        capacitor_0603("1 µF", pose.offset(11 - (2.12 * 2.5), -(2.12 * 2.5),
                                           45)), {
                                               "a": "ground",
                                               "b": "ucap",
                                           })
    cmp = cmp.add(  # reset pullup
        resistor_0603("10 kΩ", pose.offset(11 - (2.12 * 1), (2.12 * 1), -45)),
        {
            "a": "usb_vbus",
            "b": "reset",
        })

    # mcu decoupling
    cmp = cmp.add(
        capacitor_0603("0.1 µF", pose.offset(11 - (2.12 * 2), (2.12 * 2),
                                             -45)), {
                                                 "a": "ground",
                                                 "b": "usb_vbus",
                                             })
    cmp = cmp.add(
        capacitor_0603("0.1 µF", pose.offset(-11 + (2.12 * 4), (2.12 * 4),
                                             45)), {
                                                 "a": "usb_vbus",
                                                 "b": "ground",
                                             })
    cmp = cmp.add(
        capacitor_0603("0.1 µF", pose.offset(-11 + (2.12 * 4), -(2.12 * 4),
                                             -45)), {
                                                 "a": "ground",
                                                 "b": "usb_vbus",
                                             })
    cmp = cmp.add(
        capacitor_0603("0.1 µF", pose.offset(-11 + (2.12 * 1), -(2.12 * 1),
                                             -45)), {
                                                 "a": "usb_vbus",
                                                 "b": "ground",
                                             })

    return cmp


def mx_switch_set(id: str, pose: PcbPosition, key, i):
    cmp = PcbSection(id, {"a", "b", "switch-to-diode"})
    cmp = cmp.add(mx_switch(pose.offset(r=key.switch_r)), {
        "a": "a",
        "b": "switch-to-diode"
    })
    cmp = cmp.add(diode_sod323("4148", pose.offset(-5, -5.5, 180, flip=True)),
                  {
                      "b": "b",
                      "a": "switch-to-diode",
                  })

    if key.HasField("stabilizer"):
        cmp = cmp.add(
            mx_stabilizer(key.stabilizer.size,
                          pose.offset(r=-key.stabilizer.r)))

    return cmp


def generate_kicad_pcb_file(kb):
    x_scale = 1
    x_offset = 16 - min(p.x * x_scale for p in kb.outline_polygon)
    y_scale = -1
    y_offset = 16 - min(p.y * y_scale for p in kb.outline_polygon)

    # convert from keyboard.proto coordinates to PcbPosition
    def scale(pose, flip=False):
        x, y = x_scale * pose.x + x_offset, y_scale * pose.y + y_offset
        r = degrees(
            atan2(y_scale * sin(radians(pose.r)),
                  x_scale * cos(radians(pose.r))))
        return PcbPosition(x, y, r, flip)

    outline = shapely.geometry.polygon.Polygon(
        (x_offset + x_scale * o.x, y_offset + y_scale * o.y)
        for o in kb.outline_polygon)

    matrix = {f"matrix-{k.controller_pin_low}"
              for k in kb.keys
              } | {f"matrix-{k.controller_pin_high}"
                   for k in kb.keys}

    cmp = PcbSection("keyboard", {
        "ground",
        "usb_vbus",
        "usb_dp",
        "usb_dn",
    } | matrix)

    if kb.controller == Keyboard.CONTROLLER_PROMICRO:
        cmp = cmp.add(
            controller_pro_micro("controller",
                                 scale(kb.controller_pose, flip=True)), {
                                     "ground": "ground",
                                     **{
                                         s: s
                                         for s in matrix
                                     },
                                 })
    elif kb.controller == Keyboard.CONTROLLER_STM32F072:
        cmp = cmp.add(
            usbc_legacy("usb", scale(kb.connector_pose, flip=True)), {
                "ground": "ground",
                "usb_dp": "usb_dp",
                "usb_dn": "usb_dn",
                "usb_vbus": "usb_vbus",
            })
        cmp = cmp.add(
            controller_stm32("controller", scale(kb.controller_pose,
                                                 flip=True)), {
                                                     "ground": "ground",
                                                     "usb_dp": "usb_dp",
                                                     "usb_dn": "usb_dn",
                                                     "usb_vbus": "usb_vbus",
                                                     **{
                                                         s: s
                                                         for s in matrix
                                                     }
                                                 })
    elif kb.controller == Keyboard.CONTROLLER_ATMEGA32U4:
        cmp = cmp.add(
            usbc_legacy("usb", scale(kb.connector_pose, flip=True)), {
                "ground": "ground",
                "usb_dp": "usb_dp",
                "usb_dn": "usb_dn",
                "usb_vbus": "usb_vbus",
            })
        cmp = cmp.add(
            controller_atmega32u4("controller",
                                  scale(kb.controller_pose, flip=True)),
            {
                "ground": "ground",
                "usb_dp": "usb_dp",
                "usb_dn": "usb_dn",
                "usb_vbus": "usb_vbus",
                **{
                    s: s
                    for s in matrix
                },
            },
        )
    elif kb.controller == Keyboard.CONTROLLER_ATMEGA32U4_HUB2:
        cmp = cmp.add(
            usbc_legacy_hub("usb", scale(kb.connector_pose, flip=True), [
                scale(kb.reference_pose["usb_ds_1"], flip=True),
                scale(kb.reference_pose["usb_ds_2"], flip=True),
            ]), {
                "ground": "ground",
                "mcu_dp": "usb_dp",
                "mcu_dn": "usb_dn",
                "u_vbus": "usb_vbus",
            })
        cmp = cmp.add(
            controller_atmega32u4("controller",
                                  scale(kb.controller_pose, flip=True)),
            {
                "ground": "ground",
                "usb_dp": "usb_dp",
                "usb_dn": "usb_dn",
                "usb_vbus": "usb_vbus",
                **{
                    s: s
                    for s in matrix
                },
            },
        )

    else:
        raise RuntimeError("unknown controller")

    if kb.switch == Keyboard.SWITCH_CHERRY_MX:
        for i, key in enumerate(kb.keys):
            cmp = cmp.add(
                mx_switch_set(f"switch-{i}", scale(key.pose), key, i), {
                    "a": f"matrix-{key.controller_pin_low}",
                    "b": f"matrix-{key.controller_pin_high}",
                })
    else:
        raise RuntimeError(f"unknown footprint")

    txt = PcbText(scale(kb.info_pose, flip=True), kb.info_text, size=1.3)
    holes = [
        PcbCircle(x_scale * h.x + x_offset, y_scale * h.y + y_offset,
                  kb.hole_diameter) for h in kb.hole_positions
    ]
    return Board(outline, [cmp, txt], holes).to_bytes()
