load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    sha256 = "b6d46438523a3ec0f3cead544190ee13223a52f6a6765a29eae7b7cc24cc83a0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.1.0/rules_python-0.1.0.tar.gz",
)

load("@rules_python//python:pip.bzl", "pip_install")

pip_install(
    name = "my_deps",
    requirements = "//:requirements.txt",
)

http_archive(
    name = "rules_foreign_cc",
    sha256 = "0339cb90f49427446f80489bc20a474d536755120b23dc7a4e4283df5f26ad88",
    strip_prefix = "rules_foreign_cc-57500442a623bed3664bf9cc8460ba290a8a577b",
    url = "https://github.com/bazelbuild/rules_foreign_cc/archive/57500442a623bed3664bf9cc8460ba290a8a577b.zip",
)

load("@rules_foreign_cc//:workspace_definitions.bzl", "rules_foreign_cc_dependencies")

rules_foreign_cc_dependencies()

http_archive(
    name = "com_gitlab_kicad_kicad",
    build_file = "kicad-BUILD.bazel",
    patch_args = ["-p1"],
    patches = [":kicad.patch"],
    sha256 = "8e10e556e45aebb73a75f67801bca27241a747ed7bd4e06ab4eff330ae16b6c8",
    strip_prefix = "kicad-320ca5a0d0df232455718dffe9d62e05d5122ac7",
    url = "https://gitlab.com/kicad/code/kicad/-/archive/320ca5a0d0df232455718dffe9d62e05d5122ac7/kicad-320ca5a0d0df232455718dffe9d62e05d5122ac7.tar.gz",
)

BUILD_ALL_CONTENT = """filegroup(name = "all", srcs = glob(["**"], exclude=["3dmodels/*","USB-Mini-B_ LCSC-C46398.kicad_mod"]), visibility = ["//visibility:public"])"""

http_archive(
    name = "com_github_keebio_keebio_parts",
    build_file_content = BUILD_ALL_CONTENT,
    sha256 = "01ab881944905fcaa86517eff75135623b435722b3b20ef832fd2babb39b61e7",
    strip_prefix = "Keebio-Parts.pretty-c7ae3b44674679f4d767767c002fed1eacd414a1",
    url = "https://github.com/keebio/Keebio-Parts.pretty/archive/c7ae3b44674679f4d767767c002fed1eacd414a1.zip",
)

http_archive(
    name = "com_github_keebio_keebio_components",
    build_file_content = BUILD_ALL_CONTENT,
    sha256 = "5c144583e08d7569a4fbd3d996a787e190b5cd8077799adb1030571fd6c7959a",
    strip_prefix = "keebio-components-f4530381e415e10941960bc9d64e0844de96c47b",
    url = "https://github.com/keebio/keebio-components/archive/f4530381e415e10941960bc9d64e0844de96c47b.tar.gz",
)

http_archive(
    name = "com_gitlab_kicad_libraries_kicad_footprints",
    build_file_content = BUILD_ALL_CONTENT,
    sha256 = "af33022480e698b01c3fb80ed71c0ee2eaf96808e31bc7ac5e3d12d338c70b09",
    strip_prefix = "kicad-footprints-15ffd67e01257d4d8134dbd6708cb58977eeccbe",
    url = "https://gitlab.com/kicad/libraries/kicad-footprints/-/archive/15ffd67e01257d4d8134dbd6708cb58977eeccbe/kicad-footprints-15ffd67e01257d4d8134dbd6708cb58977eeccbe.tar.gz",
)

http_archive(
    name = "com_google_protobuf",
    sha256 = "0075c64cef80524b1d855df5f405845ded9b8d055022cc17b94e1589eb946b90",
    strip_prefix = "protobuf-4.0.0-rc2",
    url = "https://github.com/protocolbuffers/protobuf/archive/v4.0.0-rc2.zip",
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()
