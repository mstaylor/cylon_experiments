import os
from pycylon import DataFrame, CylonEnv
from pycylon.net import MPIConfig
import argparse
import pandas as pd 
import numpy as np
import time
import gc


parser = argparse.ArgumentParser(description='run cylon join')
parser.add_argument('-r', dest='rows', type=int, required=True)
parser.add_argument('-w', dest='world', type=int, required=True)
parser.add_argument('-i', dest='it', type=int, required=True)
parser.add_argument('-o', dest='out', type=str, required=True)
parser.add_argument('-u', dest='unique', type=float, default=1.0, help="unique factor")

script = os.path.basename(__file__).replace('.py', '')

args = vars(parser.parse_args())

w = args['world']
global_r = args['rows']
r = int(global_r/w)
cols = 2
max_val = int(r * args['unique'])


data = pd.DataFrame(np.random.randint(0, max_val, size=(r, cols))).add_prefix('col') 
data1 = pd.DataFrame(np.random.randint(0, max_val, size=(r, cols))).add_prefix('col') 
print(f"data generated", flush=True)

env = CylonEnv(config=MPIConfig())
rank = env.rank

timing = {'rows': [], 'world':[], 'it':[], 'time':[]}

# print("rank ", rank, flush=True)

try:
    for i in range(args['it']):
        df1 = DataFrame(data)
        df2 = DataFrame(data1)

        t1 = time.time()
        df3 = df1.merge(df2, on=[0], env=env)
        env.barrier()
        t2 = time.time()

        timing['rows'].append(global_r)
        timing['world'].append(w)
        timing['it'].append(i)
        timing['time'].append((t2 - t1) * 1000)

        del df1
        del df2
        del df3
        gc.collect()
finally:
    if rank == 0:
        pd.DataFrame(timing).to_csv(f"{args['out']}/{script}.csv", mode='a', index=False, header=False)
    env.finalize()

