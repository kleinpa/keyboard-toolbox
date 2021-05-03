load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def kbtb_repos():
    if "rules_python" not in native.existing_rules():
        http_archive(
            name = "rules_python",
            sha256 = "b6d46438523a3ec0f3cead544190ee13223a52f6a6765a29eae7b7cc24cc83a0",
            url = "https://github.com/bazelbuild/rules_python/releases/download/0.1.0/rules_python-0.1.0.tar.gz",
        )

    if "com_google_protobuf" not in native.existing_rules():
        http_archive(
            name = "com_google_protobuf",
            sha256 = "bf0e5070b4b99240183b29df78155eee335885e53a8af8683964579c214ad301",
            strip_prefix = "protobuf-3.14.0",
            url = "https://github.com/protocolbuffers/protobuf/archive/v3.14.0.zip",
        )

    BUILD_ALL_CONTENT = """filegroup(name = "all", srcs = glob(["**"], exclude=["3dmodels/*","USB-Mini-B_ LCSC-C46398.kicad_mod","*.step"]), visibility = ["//visibility:public"])"""

    if "com_gitlab_kicad_libraries_kicad_footprints" not in native.existing_rules():
        http_archive(
            name = "com_gitlab_kicad_libraries_kicad_footprints",
            build_file_content = BUILD_ALL_CONTENT,
            sha256 = "af33022480e698b01c3fb80ed71c0ee2eaf96808e31bc7ac5e3d12d338c70b09",
            strip_prefix = "kicad-footprints-15ffd67e01257d4d8134dbd6708cb58977eeccbe",
            url = "https://gitlab.com/kicad/libraries/kicad-footprints/-/archive/15ffd67e01257d4d8134dbd6708cb58977eeccbe/kicad-footprints-15ffd67e01257d4d8134dbd6708cb58977eeccbe.tar.gz",
        )
    if "com_github_keebio_keebio_parts" not in native.existing_rules():
        http_archive(
            name = "com_github_keebio_keebio_parts",
            build_file_content = BUILD_ALL_CONTENT,
            sha256 = "01ab881944905fcaa86517eff75135623b435722b3b20ef832fd2babb39b61e7",
            strip_prefix = "Keebio-Parts.pretty-c7ae3b44674679f4d767767c002fed1eacd414a1",
            url = "https://github.com/keebio/Keebio-Parts.pretty/archive/c7ae3b44674679f4d767767c002fed1eacd414a1.zip",
        )
    if "com_github_ai03_2725_typec" not in native.existing_rules():
        http_archive(
            name = "com_github_ai03_2725_typec",
            build_file_content = BUILD_ALL_CONTENT,
            sha256 = "348486e854174d3abb56eb35022e0e8471b9573d625d1f245aefbb7dbb6cbe6c",
            strip_prefix = "Type-C.pretty-fecd1a97dee885e7daf32da80dfa47e726d59529",
            url = "https://github.com/ai03-2725/Type-C.pretty/archive/fecd1a97dee885e7daf32da80dfa47e726d59529.zip",
        )
    if "com_gitlab_kicad_kicad" not in native.existing_rules():
        http_archive(
            name = "com_gitlab_kicad_kicad",
            build_file = "@com_github_kleinpa_kbtb//external:kicad-BUILD.bazel",
            patch_args = ["-p1"],
            patches = ["@com_github_kleinpa_kbtb//external:kicad.patch"],
            sha256 = "8e10e556e45aebb73a75f67801bca27241a747ed7bd4e06ab4eff330ae16b6c8",
            strip_prefix = "kicad-320ca5a0d0df232455718dffe9d62e05d5122ac7",
            url = "https://gitlab.com/kicad/code/kicad/-/archive/320ca5a0d0df232455718dffe9d62e05d5122ac7/kicad-320ca5a0d0df232455718dffe9d62e05d5122ac7.tar.gz",
        )
    if "rules_foreign_cc" not in native.existing_rules():
        http_archive(
            name = "rules_foreign_cc",
            sha256 = "0339cb90f49427446f80489bc20a474d536755120b23dc7a4e4283df5f26ad88",
            strip_prefix = "rules_foreign_cc-57500442a623bed3664bf9cc8460ba290a8a577b",
            url = "https://github.com/bazelbuild/rules_foreign_cc/archive/57500442a623bed3664bf9cc8460ba290a8a577b.zip",
        )
