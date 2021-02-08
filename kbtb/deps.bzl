load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
load("@rules_foreign_cc//:workspace_definitions.bzl", "rules_foreign_cc_dependencies")
load("@rules_python//python:pip.bzl", "pip_install")

def kbtb_deps():
    protobuf_deps()
    rules_foreign_cc_dependencies()

    pip_install(
        name = "com_github_kleinpa_kbtb_py_deps",
        requirements = "@com_github_kleinpa_kbtb//:requirements.txt",
    )
