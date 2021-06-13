#!/bin/bash -ue

targets=()
files=()

targets+=("//examples:unisplit42")
files+=("examples/unisplit42.svg")

targets+=("//examples:tkl")
files+=("examples/tkl.svg")

targets+=("//examples:numpad17")
files+=("examples/numpad17.svg")
targets+=("//examples:numpad17_tar")
files+=("examples/numpad17_tar.tar")

targets+=("//examples:stm32f072_demo")
files+=("examples/stm32f072_demo.svg")

targets+=("//examples/routed:numpad17")
files+=("examples/routed/numpad17.zip")
targets+=("//examples/routed:numpad17_bom")
files+=("examples/routed/numpad17_bom.csv")
targets+=("//examples/routed:numpad17_cpl")
files+=("examples/routed/numpad17_cpl.csv")

bazelisk build ${targets[@]} $@
rm -rf $(bazelisk info workspace)/dist/*
for path in "${files[@]}"
do
    mkdir -p $(dirname $(bazelisk info workspace)/dist/$path)
    cp $(bazelisk info bazel-bin)/$path $(bazelisk info workspace)/dist/$path
done
