import os

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


def sample_a2ar(morgan_file):
    ef_azdata = pd.read_csv(a2ar_directory + '/ef_a2ar.smi',
                      sep=' ', header=None)
    train_set = pd.read_csv(it_dir + '/train_set.txt',
                      sep=' ', header=None)

    #a2ar_morgan
    a2ar_morgan = pd.read_csv(a2ar_directory + morgan_file, sep=' ',header=None)#1938
    id = a2ar_morgan[0].apply(lambda x:x.strip().split(',',1)[0])
    mor = a2ar_morgan[0].apply(lambda x:x.strip().split(',',1)[-1])
    a2ar_morgan = pd.DataFrame({'zinc_id':id,'morgan':mor})
    train_amdata = a2ar_morgan.loc[a2ar_morgan.zinc_id.isin(train_set[0]),:]#1162
    ef_amdata = a2ar_morgan.loc[a2ar_morgan.zinc_id.isin(ef_azdata[0]),:]
    train_amdata.to_csv(mor_dir + '/train_morgan_1024_updated.csv',
                      mode='a',sep=' ', index=None, header=None)
    ef_amdata.to_csv(a2ar_directory + '/ef_a2ar.csv',
                      mode='w',sep=' ', index=None, header=None)
    print('save a2ar_morgan ok')


if __name__=='__main__':
    morgan_file = '/a2ar_lig_1938_morgan.txt'
    sample_a2ar(morgan_file)

