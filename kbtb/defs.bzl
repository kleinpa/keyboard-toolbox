def _build_keyboard(ctx):
    output_dxf = ctx.actions.declare_file("{}_plate_top.dxf".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_dxf],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_dxf.path),
            "--plate_type=top",
            "--format=plate_dxf",
        ],
        executable = ctx.executable._to_dxf,
    )
    output_bottom_dxf = ctx.actions.declare_file("{}_plate_bottom.dxf".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_bottom_dxf],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_bottom_dxf.path),
            "--plate_type=bottom",
            "--format=plate_dxf",
        ],
        executable = ctx.executable._to_dxf,
    )
    output_svg = ctx.actions.declare_file("{}.svg".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_svg],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_svg.path),
            "--format=svg",
        ],
        executable = ctx.executable._to_svg,
    )
    output_kicad_pcb = ctx.actions.declare_file("{}.kicad_pcb".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_kicad_pcb],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_kicad_pcb.path),
            "--format=main_pcb",
        ],
        env = {"LD_LIBRARY_PATH": ctx.executable._to_kicad.path + ".runfiles/com_gitlab_kicad_kicad"},
        executable = ctx.executable._to_kicad,
    )
    output_plate_top_kicad = ctx.actions.declare_file("{}_plate_top.kicad_pcb".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_plate_top_kicad],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_plate_top_kicad.path),
            "--format=plate_top_pcb",
        ],
        env = {"LD_LIBRARY_PATH": ctx.executable._to_kicad.path + ".runfiles/com_gitlab_kicad_kicad"},
        executable = ctx.executable._to_kicad,
    )
    output_plate_bottom_kicad = ctx.actions.declare_file("{}_plate_bottom.kicad_pcb".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_plate_bottom_kicad],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_plate_bottom_kicad.path),
            "--format=plate_bottom_pcb",
        ],
        env = {"LD_LIBRARY_PATH": ctx.executable._to_kicad.path + ".runfiles/com_gitlab_kicad_kicad"},
        executable = ctx.executable._to_kicad,
    )
    output_qmk_info = ctx.actions.declare_file("{}-info.json".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_qmk_info],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_qmk_info.path),
            "--format=qmk",
        ],
        executable = ctx.executable._to_qmk,
    )

    return [DefaultInfo(files = depset([output_svg]))]

build_keyboard = rule(
    implementation = _build_keyboard,
    attrs = {
        "src": attr.label(
            allow_single_file = [".pb"],
            mandatory = True,
        ),
        "_to_dxf": attr.label(
            default = Label("//kbtb/cli:to_dxf"),
            executable = True,
            cfg = "exec",
        ),
        "_to_svg": attr.label(
            default = Label("//kbtb/cli:to_svg"),
            executable = True,
            cfg = "exec",
        ),
        "_to_kicad": attr.label(
            default = Label("//kbtb/cli:to_kicad"),
            executable = True,
            cfg = "exec",
        ),
        "_to_qmk": attr.label(
            default = Label("//kbtb/cli:to_qmk"),
            executable = True,
            cfg = "exec",
        ),
    },
    outputs = {
        "svg": "%{name}.svg",
        "plate_bottom": "%{name}_plate_bottom.dxf",
        "plate_top": "%{name}_plate_top.dxf",
        "kicad_pcb": "%{name}.kicad_pcb",
        "plate_top_pcb": "%{name}_plate_top.kicad_pcb",
        "plate_bottom_pcb": "%{name}_plate_bottom.kicad_pcb",
        "qmk_header": "%{name}-info.json",
    },
)

def _kbpb_from_kle(ctx):
    output_file = ctx.actions.declare_file("{}.pb".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_file],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_file.path),
        ],
        executable = ctx.executable._from_kle,
    )
    return [DefaultInfo(
        files = depset([output_file]),
        runfiles = ctx.runfiles([output_file]),
    )]

kbpb_from_kle = rule(
    implementation = _kbpb_from_kle,
    attrs = {
        "src": attr.label(
            allow_single_file = [".json"],
            mandatory = True,
        ),
        "_from_kle": attr.label(
            default = Label("//kbtb/cli:from_kle"),
            executable = True,
            cfg = "exec",
        ),
    },
)
