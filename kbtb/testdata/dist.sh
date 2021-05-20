#!/bin/bash -ue

targets=()
files=()

targets+=("//kbtb/testdata:test_layout_svg")
files+=("kbtb/testdata/test_layout.svg")
targets+=("//kbtb/testdata:test_plate_kicad")
files+=("kbtb/testdata/plate.kicad_pcb")
targets+=("//kbtb/testdata:test_plate_pcb")
files+=("kbtb/testdata/test_plate_pcb.zip")
targets+=("//kbtb/testdata:test_board_kicad")
files+=("kbtb/testdata/board.kicad_pcb")
targets+=("//kbtb/testdata:test_top_plate")
files+=("kbtb/testdata/test_top_plate.dxf")
targets+=("//kbtb/testdata:test_bottom_plate")
files+=("kbtb/testdata/test_bottom_plate.dxf")
targets+=("//kbtb/testdata:test_qmk")
files+=("kbtb/testdata/test_qmk.h")


targets+=("//kbtb/testdata:tkl_layout_svg")
files+=("kbtb/testdata/tkl_layout.svg")


targets+=("//kbtb/testdata:numpad_kicad")
files+=("kbtb/testdata/numpad_board.kicad_pcb")
targets+=("//kbtb/testdata:numpad_plate_pcb")
files+=("kbtb/testdata/numpad_plate_pcb.zip")
targets+=("//kbtb/testdata:numpad_layout_svg")
files+=("kbtb/testdata/numpad_layout.svg")
targets+=("//kbtb/testdata:numpad_top_plate")
files+=("kbtb/testdata/numpad_top_plate.dxf")
targets+=("//kbtb/testdata:numpad_bottom_plate")
files+=("kbtb/testdata/numpad_bottom_plate.dxf")
targets+=("//kbtb/testdata/routed:numpad")
files+=("kbtb/testdata/routed/numpad.zip")

targets+=("//kbtb/testdata:stm32f072_demo_kicad")
files+=("kbtb/testdata/stm32f072_demo.kicad_pcb")



bazelisk build ${targets[@]} $@
rm -rf $(bazelisk info workspace)/dist/*
for path in "${files[@]}"
do
    mkdir -p $(dirname $(bazelisk info workspace)/dist/$path)
    cp $(bazelisk info bazel-bin)/$path $(bazelisk info workspace)/dist/$path
done
