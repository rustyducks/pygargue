#!/bin/bash

# Generate protobuf python code
mkdir -p ./generated
protoc -I protoduck/ --python_out=./generated protoduck/*.proto

#generate PyQt5 widget
mkdir -p ui
pyuic5 ui/arm_hat.ui -o generated/arm_hat.py
