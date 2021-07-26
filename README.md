# keyboard-toolkit

This repository contains tools for designing computer keyboards using
code. It brings together [KiCad](https://gitlab.com/kicad/code/kicad),
[exdxf](https://ezdxf.mozman.at/),
[Shapely](https://github.com/Toblerity/Shapely), and
[Bazel](https://bazel.build/) to hopefully make building keyboards a
little bit more like building a web site. Designing hardware with code
ideally enables fast iteration on key positions other design choices
with the support of an automated build system. It also means that a
single source of truth can be used to generate both the electrical
schematic and firmware.

## Overview

To build a keyboard with this library, just write a [small python
program](examples/build_numpad17.py) that generates a list of key
positions (and a few other things) and records that information in a
Keyboard protobuf message. Tools in this repository can use the
Keyboard message to generate PCBs, plates, firmware, and more. Some
post-processing, like PCB routing, will need to be done by hand but
hopefully it's less work than the alternatives.

Once a program exists to generate the keyboard definition, the Bazel
build system can be used to feed it's output into the generator tools
provided by this reposiory.

## Features

### Output Generation
* Generate Switch plates in DXF, SVG formats
* Generate unrouted PCBs with all required components
* [QMK info.json files](https://beta.docs.qmk.fm/developing-qmk/qmk-reference/reference_info_json)
* Generate [KLE JSON](http://www.keyboard-layout-editor.com/) data
* (Untested) Generate FR4 switch plates

### Input and Processing
* Load [KLE JSON](http://www.keyboard-layout-editor.com/) data
* Generate form-fitting PCBs and Plates based on the key arrangment
* Configure switch matrix positions based on the key arrangment

### Microcontrollers
* ATmega32u4
* Pro Micro
* (Untested) STM32F072

### Switchs

For now this project is focused on switch-specific PCBs.

* [Cherry MX](https://deskthority.net/wiki/Cherry_MX) compatible
* (WIP) [Kailh PG1350](https://deskthority.net/wiki/Kailh_PG1350_series)
* (WIP) [ALPS](https://deskthority.net/wiki/Alps_SKCL/SKCM_series) compatible

### Cases

Keyboard case come in many differnet styles are some of the least
trivial parts to generate. To keep things simple this repository only
supports the "PCB-to-Base-Plate Sandwich". This is a minimalist
approach where the PCB is attached to a base plate with standoffs and
an optional switch plate is 'floating' on the switches. Additional
case types may be added eventually and would be a welcome addition to
this library.

## Getting Started

This project uses the Bazel build system internally and also provides
build rules for downstream projects. Additionally, PCB file
processing is provided by the
[`kicad-bazel`](https://github.com/kleinpa/kicad-bazel) project which
works by building KiCAD from source
([issue](https://github.com/kleinpa/kicad-bazel/issues/2)). All tools
that interact with PCBs unfortunately depend on all of KiCAD's build
dependencies.

## Bazel Build Rules

It makes sense to use some tool to generate the keyboard proto and
here is an example of stock Baezl rules can be used to make that
happen:

```python
py_binary(
    name = "build_kbxyz",
    srcs = ["build_kbxyz.py"],
    deps = [
        "//kbtb:keyboard_lib",
    ],
)

genrule(
    name = "kbxyz_proto",
    outs = ["kbxyz.pb"],
    cmd = "$(execpath :build_kbxyz) $@",
    exec_tools = [":build_kbxyz"],
)
```

### build_keyboard

This is the main entry point to the output generation tools provided by this repository.

```python
load("@com_github_kleinpa_keyboardtoolbox//kbtb:defs.bzl", "build_keyboard")

build_keyboard(
    name = "kbxyz",
    src = ":kbxyz_proto",
)
```

The following files can be requested from this rule:

* `kbxyz.svg`
* `kbxyz.kicad_pcb`
* `kbxyz-info.json`
* `kbxyz_plate_top.dxf`
* `kbxyz_plate_top.kicad_pcb`
* `kbxyz_plate_bottom.dxf`
* `kbxyz_plate_bottom.kicad_pcb`

### kbpb_from_kle

This is an experimenal build rule that can produce a basic keyboard
from a kle file is also provided. It's probably more flexible to just
do this via python like in the genrule example above.

```python
load("@com_github_kleinpa_keyboardtoolbox//kbtb:defs.bzl", "kbpb_from_kle")

kbpb_from_kle(
    name = "kbxyz_proto",
    src = "kbxyz-kle.json",
)
```

## The Future

The biggest question that remains unanswered is: _Why just keyboards?_
If there's one thing I've figured out while working on this project is
that the idea of generating electronic hardware with software is worth
exploring more.
