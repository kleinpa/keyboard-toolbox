# keyboard-toolkit

A helpful box of tools that bring together
[KiCad](https://gitlab.com/kicad/code/kicad),
[exdxf](https://ezdxf.mozman.at/),
[Shapely](https://github.com/Toblerity/Shapely), and
[Bazel](https://bazel.build/) to explore code-based CAD ideas and make
neat keyboards. There's lots of fun stuff inside:

* Write a function to arrange your keys or load them from
  [keyboard-layout-editor.com](http://www.keyboard-layout-editor.com/).
* Produce ready-to-route PCBs with your choice of microcontroller and
  switch.
* Generate DXF files (or Gerbers!) for top and bottom plates.
* Generate QMK headers from the same source of truth as the schematic.

My [kicad-bazel](https://github.com/kleinpa/kicad-bazel) project was
originally a part of this project before being seperated and generalized.
There's still lots of work to do before I'd trust the output of this
tool, but it has already proven itself at least partially working.

The 'numpad17' example was routed by hand and then built using a PCBA
service. Some pictures of the final product can be found
[on imgur](https://imgur.com/a/V2k2rSG).
