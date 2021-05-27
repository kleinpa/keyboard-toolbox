#!/bin/bash -ue

targets=()
files=()

targets+=("//examples:unisplit42")
files+=("examples/unisplit42.svg")

targets+=("//examples:tkl")
files+=("examples/tkl.svg")

targets+=("//examples:numpad")
files+=("examples/numpad.svg")
targets+=("//examples:numpad_tar")
files+=("examples/numpad_tar.tar")

targets+=("//examples:stm32f072_demo")
files+=("examples/stm32f072_demo.svg")

targets+=("//examples/routed:numpad")
files+=("examples/routed/numpad.zip")
targets+=("//examples/routed:numpad_bom")
files+=("examples/routed/numpad_bom.csv")
targets+=("//examples/routed:numpad_cpl")
files+=("examples/routed/numpad_cpl.csv")

bazelisk build ${targets[@]} $@
rm -rf $(bazelisk info workspace)/dist/*
for path in "${files[@]}"
do
    mkdir -p $(dirname $(bazelisk info workspace)/dist/$path)
    cp $(bazelisk info bazel-bin)/$path $(bazelisk info workspace)/dist/$path
done
