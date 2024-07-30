#!/bin/bash
#SBATCH -c 6  # number of cores to allocate
#SBATCH -N 1
#SBATCH -t 0-01:30:00  # time in d-hh:mm:ss
#SBATCH --mail-type=ALL # Send an e-mail when a job starts, stops, or fails
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --mail-user=rswart@asu.edu

module purge
module load mamba
source activate geo_dask
source deactivate
source activate geo_dask
python3 /home/rswart/SWIFL-Data-Transfer/src/WRF_AutoBEM/epws_to_shp.py 
