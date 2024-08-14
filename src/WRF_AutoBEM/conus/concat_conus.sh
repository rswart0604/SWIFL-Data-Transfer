#!/bin/bash
#SBATCH -c 1  # number of cores to allocate
#SBATCH -t 0-02:00:00  # time in d-hh:mm:ss
#SBATCH --mail-type=ALL # Send an e-mail when a job starts, stops, or fails
#SBATCH --exclude=sch001,sch002
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --mail-user=rswart@asu.edu

module purge
module load mamba/latest
source activate ncl_env

ncrcat /scratch/rswart/conus404small/* /scratch/rswart/conus404.nc
