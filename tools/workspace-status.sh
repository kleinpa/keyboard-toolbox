#!/bin/bash -ue

if [[ -z $(git status -s) ]]; then
  echo "STABLE_HASH $(git rev-parse --short HEAD)"
else
 echo "STABLE_HASH $(git rev-parse --short HEAD)-dirty"
fi
