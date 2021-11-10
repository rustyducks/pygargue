#!/bin/bash

# Generate the desktop source code.
mkdir -p ./generated
protoc -I../firmware/proto/ --python_out=./generated ../firmware/proto/*.proto
