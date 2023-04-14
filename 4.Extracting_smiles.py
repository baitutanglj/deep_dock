import glob
import os
import time
from contextlib import closing
from multiprocessing import Pool

import numpy as np
from config import args

protein = args.protein_name
file_path = args.file_path
n_it = args.n_iteration
zinc_directory = args.zinc_directory
tot_process = args.tot_process

##dir name
it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
it_dir_old = os.path.join(file_path, protein, 'iteration_' + str(n_it - 1))
zinc_dir = os.path.join(it_dir, 'smile')


def extract_morgan(file_name):
    train = {}
    test = {}
    valid = {}
    with open(it_dir + "/train_set.txt", 'r') as ref:
        for line in ref:
            train[line.rstrip()] = 0
    with open(it_dir + "/valid_set.txt", 'r') as ref:
        for line in ref:
            valid[line.rstrip()] = 0
    with open(it_dir + "/test_set.txt", 'r') as ref:
        for line in ref:
            test[line.rstrip()] = 0
    # for file_name in file_names:
    ref1 = open(zinc_dir + '/train_' + file_name.split('/')[-1], 'a')
    ref2 = open(zinc_dir + '/valid_' + file_name.split('/')[-1], 'a')
    ref3 = open(zinc_dir + '/test_' + file_name.split('/')[-1], 'a')
    with open(file_name, 'r') as ref:
        flag = 0
        for line in ref:
            tmpp = line.strip().split(' ')[0]
            if tmpp in train.keys():
                train[tmpp] += 1
                fn = 1
                if train[tmpp] == 1: flag = 1
            elif tmpp in valid.keys():
                valid[tmpp] += 1
                fn = 2
                if valid[tmpp] == 1: flag = 1
            elif tmpp in test.keys():
                test[tmpp] += 1
                fn = 3
                if test[tmpp] == 1: flag = 1
            if flag == 1:
                if fn == 1:
                    ref1.write(line)
                if fn == 2:
                    ref2.write(line)
                if fn == 3:
                    ref3.write(line)
            flag = 0


def alternate_concat(files):
    to_return = []
    with open(files, 'r') as ref:
        for line in ref:
            to_return.append(line)
    return to_return


def delete_all(files):
    os.remove(files)


def morgan_duplicacy(f_name):
    # print(f_name)#test_BE_smiles.txt
    flag = 0
    mol_list = {}
    ref1 = open(f_name + '_updated.smi', 'a')
    with open(f_name, 'r') as ref:
        for line in ref:
            tmpp = line.strip().split(' ')[0]
            if tmpp not in mol_list:
                mol_list[tmpp] = 1
                flag = 1
            if flag == 1:
                ref1.write(line)
                flag = 0
    os.remove(f_name)


if __name__ == '__main__':
    start = time.time()
    try:
        os.mkdir(zinc_dir)
    except:
        pass
    files = []
    for f in glob.glob(zinc_directory + "/smile_all_*.txt"):
        files.append(f)

    t = time.time()
    with closing(Pool(np.min([tot_process, len(files)]))) as pool:
        pool.map(extract_morgan, files)
    print(time.time() - t)

    for type_to in ['train', 'valid', 'test']:
        t = time.time()
        files = []
        for f in glob.glob(os.path.join(zinc_dir, type_to + '*.txt')):
            files.append(f)
        if len(files) == 0:
            print("Error in address above")
            break
        with closing(Pool(np.min([tot_process, len(files)]))) as pool:
            to_print = pool.map(alternate_concat, files)
        with open(os.path.join(zinc_dir, type_to + '_smiles_final'), 'w') as ref:
            for file_data in to_print:
                for line in file_data:
                    ref.write(line)
        to_print = []
        print(type_to, time.time() - t)

    f_names = []
    for f in glob.glob(file_path + '/' + protein + '/iteration_' + str(n_it) + '/smile/*smile*'):
        f_names.append(f)

    t = time.time()
    with closing(Pool(np.min([tot_process, len(f_names)]))) as pool:
        pool.map(morgan_duplicacy, f_names)
    print(time.time() - t)

    all_to_delete = []
    for f in glob.glob(os.path.join(zinc_dir,'*.txt*')):
        all_to_delete.append(f)
    with closing(Pool(np.min([tot_process, len(all_to_delete)]))) as pool:
        pool.map(delete_all, all_to_delete)
    print('all_time:', time.time() - start)