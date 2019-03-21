#!/bin/bash

#cd "$(dirname "$0")"
cd "${0%/*}"
python3 -m pytest -v ../
