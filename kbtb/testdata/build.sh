#!/bin/bash -ue

targets=()
files=()


targets+=("//kbtb/testdata:test_layout_svg")
files+=("kbtb/testdata/test_layout.svg")

targets+=("//kbtb/testdata:test_plate_kicad")
files+=("kbtb/testdata/plate.kicad_pcb")

targets+=("//kbtb/testdata:test_plate_gerbers")
files+=("kbtb/testdata/plate_gerbers.zip")

targets+=("//kbtb/testdata:test_board_kicad")
files+=("kbtb/testdata/board.kicad_pcb")

targets+=("//kbtb/testdata:test_qmk")
files+=("kbtb/testdata/test_qmk.h")

targets+=("//kbtb/testdata:test_top_plate")
files+=("kbtb/testdata/test_top_plate.dxf")
targets+=("//kbtb/testdata:test_bottom_plate")
files+=("kbtb/testdata/test_bottom_plate.dxf")

targets+=("//kbtb/testdata:tkl_layout_svg")
files+=("kbtb/testdata/tkl_layout.svg")

targets+=("//kbtb/testdata:numpad_top_plate")
files+=("kbtb/testdata/numpad_top_plate.dxf")
targets+=("//kbtb/testdata:numpad_bottom_plate")
files+=("kbtb/testdata/numpad_bottom_plate.dxf")

targets+=("//kbtb/testdata:numpad_kicad")
files+=("kbtb/testdata/numpad_board.kicad_pcb")

targets+=("//kbtb/testdata:numpad_plate_gerbers")
files+=("kbtb/testdata/numpad_plate_gerbers.zip")

targets+=("//kbtb/testdata:numpad_layout_svg")
files+=("kbtb/testdata/numpad_layout.svg")

bazel build ${targets[@]}
rm -rf $(bazel info workspace)/dist/*
mkdir -p $(bazel info workspace)/dist
for path in "${files[@]}"
do
    rsync -L --perms --chmod=a=rw,Da+x $(bazel info bazel-bin)/$path $(bazel info workspace)/dist/$(basename $path)
done
