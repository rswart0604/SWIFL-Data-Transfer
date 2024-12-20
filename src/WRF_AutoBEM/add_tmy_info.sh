#!/bin/bash
#SBATCH -c 4  # number of cores to allocate
#SBATCH -t 0-01:00:00  # time in d-hh:mm:ss
#SBATCH --mail-type=ALL # Send an e-mail when a job starts, stops, or fails
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --mail-user=rswart@asu.edu

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
#
# case in point; BEGIN_DATE should be the time of the first record you have in your wrfout
#		 and END_DATE is one hour later than the time of the last record in wrfout

module purge

TMY_FILE='tmy.epw'
BEGIN_DATE=",5,14,18,"
END_DATE=",5,31,18,"
PARALLEL_PROCESSES=4
EPW_DIR="/scratch/rswart/conus404_epws"


csplit -f output "$TMY_FILE" /"$BEGIN_DATE"/
mv output00 beginning_tmy.epw
csplit -f newput output01 /"$END_DATE"/
rm newput00
rm output01
mv newput01 ending_tmy.epw

find "$EPW_DIR" -type f -name "*.epw" | xargs -P "$PARALLEL_PROCESSES" -I {} sh -c \
'header_file="${1%.epw}.header"; cat "$header_file" beginning_tmy.epw "$1" ending_tmy.epw > "$1.tmp" && mv "$1.tmp" "$1"' _ {}
