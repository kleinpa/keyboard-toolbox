#!/bin/bash -ue

ibazel --run_command_after 'bash -c "rsync -zvh bazel-bin/* dist || true"' build //:quine_mk1_svg //:quine_mk1_plate_dxf //:quine_mk1_plate_kicad //:quine_mk1_plate_gerbers //:quine_mk1_board_kicad //:quine_mk1_qmk_header //:planckish_svg //:planckish_board_kicad //:pumnad_svg //:pumnad_board_kicad //:planckish_header

