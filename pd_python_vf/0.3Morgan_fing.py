import glob
import multiprocessing
import os
import time
from contextlib import closing
from multiprocessing import Pool

import numpy as np
from config import args
from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem import AllChem

fp = args.file_path
fn = args.folder_name
t_pos = args.t_pos
data_directory = args.data_directory
zinc_directory = args.zinc_directory
node_num = args.node_num


def morgan_fing(fname):
    ct = 0
    nbits = 1024
    radius = 2
    fsplit = fname.split('/')[-1]
    ref2 = open(os.path.join(data_directory,fsplit),'a')
    with open(fname,'r') as ref:
        # ref.readline()
        for line in ref:
            zinc_id, smile, path= line.rstrip().split(' ')
            arg = np.zeros((1,))
            try:
                DataStructs.ConvertToNumpyArray(AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(smile), radius, nBits=nbits),arg)
                ref2.write(zinc_id + ' ')
                ref2.write((',').join([str(elem) for elem in np.where(arg == 1)[0]]) + '\n')
                ct +=1
            except:
                pass
    print('fname,ct',fname,ct)

if __name__=='__main__':
    start = time.time()
    files = []
    for f in glob.glob(zinc_directory+'/smile_all_*.txt'):
        files.append(f)

    try:
        os.mkdir(data_directory)
    except:
        pass

    print('len(files)',len(files))

    with closing(Pool(np.min([multiprocessing.cpu_count()*node_num,t_pos]))) as pool:
        pool.map(morgan_fing,files)
    print('all run time Morgan_fing',time.time()-start)
