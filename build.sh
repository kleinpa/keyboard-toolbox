#!/bin/bash -ue

ibazel --run_command_after 'bash -c "mkdir -p dist && rm -rf dist/* && cp -f  bazel-bin/*{.zip,.kicad_pcb,.svg,.h} dist"' build //:quine_mk1_svg //:quine_mk1_plate_dxf //:quine_mk1_plate_kicad //:quine_mk1_plate_gerbers //:quine_mk1_board_kicad

