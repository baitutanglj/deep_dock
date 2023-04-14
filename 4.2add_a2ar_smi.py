import os

import numpy as np
import pandas as pd
from config import args

protein = args.protein_name
file_path = args.file_path
data_directory = args.data_directory
zinc_directory = args.zinc_directory
n_it = args.n_iteration
tot_process = args.tot_process
sample_num = args.sample_num
a2ar_directory = args.a2ar_directory
r = args.a2ar_ratio

it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
zinc_dir = os.path.join(it_dir, 'smile')
mor_dir = os.path.join(it_dir, 'morgan')


def sample_a2ar(zinc_file):
    #a2ar_zinc
    a2ar_zinc = pd.read_csv(a2ar_directory + zinc_file,sep='\t',header=None)#1938
    a2ar_zinc.columns = ['smiles','zinc_id']
    a2ar_zinc['path'] = list(np.repeat('ar/local.tar/00000',len(a2ar_zinc)))
    a2ar_zinc = a2ar_zinc.loc[:,['zinc_id','smiles','path']]
    a2ar_zinc = a2ar_zinc.reindex(np.random.permutation(a2ar_zinc.index))
    train_azdata = a2ar_zinc.sample(n=int(len(a2ar_zinc)*r),random_state=123,axis=0)#1162
    train_a2ar_id = train_azdata['zinc_id']
    ef_azdata = a2ar_zinc.loc[-a2ar_zinc['zinc_id'].isin(train_a2ar_id),:]#776
    train_azdata.to_csv(zinc_dir + '/train_smiles_final_updated.smi',
                      sep=' ', mode='a', index=None, header=None)
    ef_azdata.to_csv(a2ar_directory + '/ef_a2ar.smi',
                      sep=' ', mode='w', index=None, header=None)
    train_a2ar_id.to_csv(it_dir+ '/train_set.txt', mode='a', index=None, header=None)
    print('save a2ar_zinc ok')

    return train_a2ar_id


if __name__=='__main__':
    zinc_file = '/a2ar_lig_1938_new.txt'
    sample_a2ar(zinc_file)