import glob
import os
import time
from contextlib import closing
from multiprocessing import Pool

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
split_ratio = args.split_ratio

# dir name
it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
it_dir_old = os.path.join(file_path, protein, 'iteration_' + str(n_it-1))
updated_old = os.path.join(it_dir_old,'updated')
zinc_dir = os.path.join(it_dir, 'smile')
mor_dir = os.path.join(it_dir, 'morgan')
pre_dir = os.path.join(it_dir_old,'morgan_1024_predictions')

def train_valid_test(file_name):
    f_name = file_name.split('/')[-1]
    mol_ct = pd.read_csv(it_dir + "/Mol_ct_file_updated.csv", index_col=1)
    To_sample = int(mol_ct.loc[f_name].Sample_for_million / 3)
    To_ef = int(mol_ct.loc[f_name].Sample_for_ef)
    Total_len = int(mol_ct.loc[f_name].Number_of_Molecules) - (n_it-1)*sample_num

    shuffle_array = np.linspace(0, Total_len - 1, Total_len)
    seed = np.random.randint(0, 2 ** 32)
    np.random.seed(seed=seed)
    np.random.shuffle(shuffle_array)
    train_ind = shuffle_array[:To_sample]
    valid_ind = shuffle_array[To_sample:To_sample * 2]
    test_ind = shuffle_array[To_sample * 2:To_sample * 3]
    ef_ind = shuffle_array[To_sample * 3:To_sample * 3+To_ef]
    train_ind_dict = {}
    valid_ind_dict = {}
    test_ind_dict = {}
    ef_ind_dict = {}
    update_file = open(os.path.join(it_dir,'updated', f_name), 'a')
    train_set = open(it_dir + "/train_set.txt", 'a')
    test_set = open(it_dir + "/test_set.txt", 'a')
    valid_set = open(it_dir + "/valid_set.txt", 'a')
    ef_set = open(it_dir + "/ef_set.txt", 'a')
    for i, j, k in zip(train_ind, valid_ind, test_ind):
        train_ind_dict[i] = 1
        valid_ind_dict[j] = 1
        test_ind_dict[k] = 1
    for i in ef_ind:
        ef_ind_dict[i] = 1
    with open(file_name, 'r') as ref:
        for ind, line in enumerate(ref):
            tmpp = line.strip().split(' ')[0]
            if ind in train_ind_dict.keys():
                train_set.write(tmpp + '\n')
            elif ind in valid_ind_dict.keys():
                valid_set.write(tmpp + '\n')
            elif ind in test_ind_dict.keys():
                test_set.write(tmpp + '\n')
            elif ind in ef_ind_dict.keys():
                ef_set.write(tmpp + '\n')
            else:
                update_file.write(tmpp + '\n')

    train_set.close()
    valid_set.close()
    test_set.close()
    ef_set.close()
    update_file.close()


def train_valid_test2(file_name):
    f_name = file_name.split('/')[-1]
    mol_ct = pd.read_csv(it_dir + "/Mol_ct_file_updated.csv", index_col=1)
    To_sample = round(mol_ct.loc[f_name].Sample_for_million / 3)
    To_ef = round(mol_ct.loc[f_name].Sample_for_ef)
    Total_len = round(mol_ct.loc[f_name].Number_of_Molecules)
    shuffle_array = np.linspace(0, Total_len - 1, Total_len)
    seed = np.random.randint(0, 2 ** 32)
    np.random.seed(seed=seed)
    np.random.shuffle(shuffle_array)
    train_ind = shuffle_array[:To_sample]
    valid_ind = shuffle_array[To_sample:To_sample * 2]
    test_ind = shuffle_array[To_sample * 2:To_sample * 3]
    ef_ind = shuffle_array[To_sample * 3:To_sample * 3+To_ef]
    train_ind_dict = {}
    valid_ind_dict = {}
    test_ind_dict = {}
    ef_ind_dict = {}
    update_old_dict = {}
    with open(os.path.join(it_dir_old,'updated', f_name), 'r') as f:
        for line in f:
            tmp = line.strip().split(',')[0]
            update_old_dict[tmp] = 0
    update_file = open(os.path.join(it_dir,'updated', f_name), 'a')
    train_set = open(it_dir + "/train_set.txt", 'a')
    test_set = open(it_dir + "/test_set.txt", 'a')
    valid_set = open(it_dir + "/valid_set.txt", 'a')
    ef_set = open(it_dir + "/ef_set.txt", 'a')
    for i, j, k in zip(train_ind, valid_ind, test_ind):
        train_ind_dict[i] = 1
        valid_ind_dict[j] = 1
        test_ind_dict[k] = 1
    for i in ef_ind:
        ef_ind_dict[i] = 1
    with open(file_name, 'r') as ref:
        for ind, line in enumerate(ref):
            tmpp = line.strip().split(',')[0]
            if ind in train_ind_dict.keys():
                train_set.write(tmpp + '\n')
                update_old_dict.pop(tmpp)
            elif ind in valid_ind_dict.keys():
                valid_set.write(tmpp + '\n')
                update_old_dict.pop(tmpp)
            elif ind in test_ind_dict.keys():
                test_set.write(tmpp + '\n')
                update_old_dict.pop(tmpp)
            elif ind in ef_ind_dict.keys():
                ef_set.write(tmpp + '\n')
                update_old_dict.pop(tmpp)

    for key in update_old_dict.keys():
        update_file.write(key + '\n')

    train_set.close()
    valid_set.close()
    test_set.close()
    ef_set.close()
    update_file.close()


if __name__ == '__main__':
    start = time.time()
    print(file_path, protein, zinc_directory)
    try:
        os.mkdir(os.path.join(it_dir,'updated'))
        print('updated_dir:',os.path.join(it_dir,'updated'))
    except:
        pass
    f_names = []
    if n_it == 1:
        for f in glob.glob(zinc_directory + '/smile_all_*.txt'):
            f_names.append(f)
        with closing(Pool(np.min([tot_process, len(f_names)]))) as pool:
            pool.map(train_valid_test, f_names)
    else:
        for f in glob.glob(pre_dir + '/smile_all_*.txt'):
            f_names.append(f)
        with closing(Pool(np.min([tot_process, len(f_names)]))) as pool:
            pool.map(train_valid_test2, f_names)

    print('all time',time.time() - start)

