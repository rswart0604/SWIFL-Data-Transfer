import pandas as pd
import os
import numpy as np


from multiprocessing import Pool

import time

if __name__ == '__main__':

    # i want to read in every epw
    # and just change 384 characters at a specific row
    # and then write back
    def read_write_epw(epw_num: int) -> None:
        filename = f'/scratch/rswart/epws/{epw_num}.epw'
        df = pd.read_csv(filename, header=None, skiprows=8, engine='pyarrow')
        df.iloc[3242-9:3626-8, 9] = df.iloc[3242-9:3626-8, 9] * 100.0
        df.to_csv(filename, index=False, header=False)

    

    old = time.time()
    with Pool(processes=4) as pool:
        pool.map(read_write_epw, list(range(100,146556)))
        print(time.time()-old)

#    for i in range(60,80):
#        read_write_epw(i)
