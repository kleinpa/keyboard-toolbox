#!/bin/bash -ue

targets=()
files=()

targets+=("//examples:test_layout_svg")
files+=("examples/test_layout.svg")
targets+=("//examples:test_plate_kicad")
files+=("examples/plate.kicad_pcb")
targets+=("//examples:test_plate_pcb")
files+=("examples/test_plate_pcb.zip")
targets+=("//examples:test_board_kicad")
files+=("examples/board.kicad_pcb")
targets+=("//examples:test_top_plate")
files+=("examples/test_top_plate.dxf")
targets+=("//examples:test_bottom_plate")
files+=("examples/test_bottom_plate.dxf")
targets+=("//examples:test_qmk")
files+=("examples/test_qmk.h")


targets+=("//examples:tkl_layout_svg")
files+=("examples/tkl_layout.svg")


targets+=("//examples:numpad_kicad")
files+=("examples/numpad_board.kicad_pcb")
targets+=("//examples:numpad_plate_pcb")
files+=("examples/numpad_plate_pcb.zip")
targets+=("//examples:numpad_layout_svg")
files+=("examples/numpad_layout.svg")
targets+=("//examples:numpad_top_plate")
files+=("examples/numpad_top_plate.dxf")
targets+=("//examples:numpad_bottom_plate")
files+=("examples/numpad_bottom_plate.dxf")
targets+=("//examples/routed:numpad")
files+=("examples/routed/numpad.zip")

targets+=("//examples:stm32f072_demo_kicad")
files+=("examples/stm32f072_demo.kicad_pcb")



bazelisk build ${targets[@]} $@
rm -rf $(bazelisk info workspace)/dist/*
for path in "${files[@]}"
do
    mkdir -p $(dirname $(bazelisk info workspace)/dist/$path)
    cp $(bazelisk info bazel-bin)/$path $(bazelisk info workspace)/dist/$path
done
