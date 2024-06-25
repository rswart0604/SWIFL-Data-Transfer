#!/bin/bash
#SBATCH -c 4  # number of cores to allocate
#SBATCH --exclude=ch001,ch002
#SBATCH --mem=5G
#SBATCH -t 0-04:00:00  # time in d-hh:mm:ss
#SBATCH --mail-type=ALL # Send an e-mail when a job starts, stops, or fails
#SBATCH -o %j.out
#SBATCH -e %j.err
#SBATCH --mail-user=rswart@asu.edu
module purge
module load mamba/latest
source activate wrfout_py_env
python3 /home/rswart/SWIFL-Data-Transfer/src/make_shp.py > /home/rswart/SWIFL-Data-Transfer/src/output_shp.txt

