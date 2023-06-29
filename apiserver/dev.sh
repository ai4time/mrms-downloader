#! /usr/bin/env bash

set -euo pipefail

docker build . -t yipengh/demo-mrms-apiserver:devel

docker run --rm \
  -v /Users/yhuang/dev/demo/demo-mrms/data:/data \
  -v /Users/yhuang/dev/demo/demo-mrms/apiserver:/app \
  -p 8000:8000 \
  yipengh/demo-mrms-apiserver:devel
