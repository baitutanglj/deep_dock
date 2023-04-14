import os
import time
import glob
import pandas as pd
import numpy as np
import multiprocessing
from contextlib import closing
from multiprocessing import Pool
from config import args

file_path = args.file_path
protein = args.protein_name
data_directory = args.data_directory
zinc_directory = args.zinc_directory
n_it = args.n_iteration
t_pos = args.tot_process
sample_num = args.sample_num
split_ratio = args.split_ratio
ef_num = args.ef_num
chunk_size = args.chunk_size


it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
it_dir_old = os.path.join(file_path, protein, 'iteration_' + str(n_it-1))
zinc_dir = os.path.join(it_dir, 'smile')
mor_dir = os.path.join(it_dir, 'morgan')
pre_dir = os.path.join(it_dir_old,'morgan_1024_predictions')

def molecule_count(fname):
    '''count every file lines'''
    os.system('find '+fname+' | xargs wc -l >> '+it_dir+'/count_lines.txt')

def save_Mol_ct(it_dir):
    '''save result as Mol_ct_file.csv'''
    ref = open(it_dir+'/Mol_ct_file.csv','a')
    with open(it_dir+'/count_lines.txt') as f:
        for line in f:
            tmp = line.strip().split(' ')
            tmp_fname = tmp[-1].strip().rsplit('/',1)[-1]
            print(tmp[0],tmp_fname)
            ref.write(tmp[0]+','+tmp_fname+'\n')



if __name__=='__main__':
    t = time.time()
    try:
        os.mkdir(it_dir)
    except:
        pass


    if n_it==1:
        fnames = glob.glob(zinc_directory + "/smile_all_*.txt")
    else:
        fnames = glob.glob(pre_dir + "/smile_all_*.txt")
    with closing(Pool(np.min([multiprocessing.cpu_count(),len(fnames),t_pos]))) as pool:
        pool.map(molecule_count,fnames)

    save_Mol_ct(it_dir)

    # write_mol_count_list(it_dir+'/Mol_ct_file.csv',rt)
    mol_ct = pd.read_csv(it_dir+'/Mol_ct_file.csv',header=None)
    mol_ct.columns = ['Number_of_Molecules','file_name']
    Total_mols_available = np.sum(mol_ct.Number_of_Molecules)#Number_of_Molecules:53038114+....
    mol_ct['Sample_for_million'] = [round(sample_num/Total_mols_available*elem) for elem in mol_ct.Number_of_Molecules]
    mol_ct['Sample_for_ef'] = [round(ef_num / Total_mols_available * elem) for elem in mol_ct.Number_of_Molecules]
    mol_ct['Sample_for_chunk'] = [round(sample_num/Total_mols_available*elem) for elem in mol_ct.Number_of_Molecules]
    mol_ct.to_csv(it_dir+'/Mol_ct_file_updated.csv',sep=',',index=False)

    print('run 1.molecular_file_count_updated.py time:', time.time() - t)


