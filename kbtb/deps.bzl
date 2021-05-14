load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
load("@rules_python//python:pip.bzl", "pip_install")
load("@com_github_kleinpa_kicadbazel//:deps.bzl", "kicadbazel_deps")

def kbtb_deps():
    protobuf_deps()
    kicadbazel_deps()

    pip_install(
        name = "com_github_kleinpa_keyboardtoolbox_py_deps",
        requirements = "@com_github_kleinpa_keyboardtoolbox//:requirements.txt",
    )
