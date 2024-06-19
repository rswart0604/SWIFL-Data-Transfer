#!/bin/bash

PARALLEL_PROCESSES=4
EPW_DIR="/scratch/rswart/epws"


find "$EPW_DIR" -type f -name "*.epw" | xargs -P "$PARALLEL_PROCESSES" -I {} sh -c 'cat ~/former.csv "{}" > "{}.tmp" && mv "{}.tmp" "{}" && cat ~/latter.csv >> "{}"'

