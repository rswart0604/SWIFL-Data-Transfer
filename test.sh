PARALLEL_PROCESSES=4
EPW_DIR="/scratch/rswart/epws"
find "$EPW_DIR" -type f -name "*.epw" | xargs -P "$PARALLEL_PROCESSES" -I {} sh -c 'header_file="/scratch/rswart/headers/${1%.epw}.header"; cat "$header_file" other_header.txt "$1" > "$1.tmp" && mv "$1.tmp" "$1"' _ {}

