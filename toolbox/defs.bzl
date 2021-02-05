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
    return DefaultInfo(files = depset([output_file]))

kbpb_from_kle = rule(
    implementation = _kbpb_from_kle,
    attrs = {
        "src": attr.label(
            allow_single_file = [".json"],
            mandatory = True,
        ),
        "_from_kle": attr.label(
            default = Label("//toolbox/cli:from_kle"),
            executable = True,
            cfg = "exec",
        ),
    },
)

def _keyboard_plate_dxf(ctx):
    output_file = ctx.actions.declare_file("{}.pb".format(ctx.label.name))
    ctx.actions.run(
        inputs = [ctx.file.src],
        outputs = [output_file],
        arguments = [
            "--input={}".format(ctx.file.src.path),
            "--output={}".format(output_file.path),
            "--format=plate_dxf",
        ],
        executable = ctx.executable._toolbox,
    )
    return DefaultInfo(files = depset([output_file]))

keyboard_plate_dxf = rule(
    implementation = _keyboard_plate_dxf,
    attrs = {
        "src": attr.label(
            allow_single_file = [".pb"],
            mandatory = True,
        ),
        "_toolbox": attr.label(
            default = Label("//toolbox/cli"),
            executable = True,
            cfg = "exec",
        ),
    },
)
