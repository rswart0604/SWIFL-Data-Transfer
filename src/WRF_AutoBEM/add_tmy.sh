#!/bin/bash
#SBATCH --exclude=ch001,ch002
#SBATCH -c 4  # number of cores to allocate
#SBATCH -t 0-04:00:00  # time in d-hh:mm:ss
#SBATCH --mail-type=ALL # Send an e-mail when a job starts, stops, or fails
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --mail-user=rswart@asu.edu

module purge
./add_tmy_info.sh
