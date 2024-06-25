#!/bin/bash

# this script takes a given tmy file, splits it into 3 based on the dates of wrf
#	data you want to use, and then takes the 2 ends and splices them back onto
#	all of the wrf csvs that are stored
#
#	1/1 -> WRFOUT_START_DATE and WRFOUT_END_DATE -> 12/31 are both stored
#
#	then, we do (1/1 -> WRFOUT_START_DATE) + (WRF csv for each grid cell) + (WRFOUT_END_DATE -> 12/31)
#
# change the following variables with your use case
# date variables of format f",{month number},{day number},{hour number},"
# and for END_DATE, the hour number is one more than what you want to cut off at (due to csplit functionality)

TMY_FILE='tmy.epw'
BEGIN_DATE=",5,15,18,"
END_DATE=",5,31,19,"
PARALLEL_PROCESSES=4
EPW_DIR="/scratch/rswart/epws"


csplit -f output "$TMY_FILE" /"$BEGIN_DATE"/
mv output00 beginning_tmy.epw
csplit -f newput output01 /"$END_DATE"/
rm newput00
rm output01
mv newput01 ending_tmy.epw

#find "$EPW_DIR" -type f -name "*.epw" | xargs -P "$PARALLEL_PROCESSES" -I {} sh -c 'cat beginning_tmy.epw "{}" > "{}.tmp" && mv "{}.tmp" "{}" && cat ending_tmy.epw >> "{}"'

find "$EPW_DIR" -type f -name "*.epw" | xargs -P "$PARALLEL_PROCESSES" -I {} sh -c 'header_file="${1%.epw}.header"; cat "$header_file" beginning_tmy.epw "$1" ending_tmy.epw > "$1.tmp" && mv "$1.tmp" "$1"' _ {}
rm /scratch/rswart/*.header
