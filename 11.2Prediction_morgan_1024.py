import argparse
import glob
import os
import re as re_split
import time

import numpy as np
import pandas as pd
from keras.models import model_from_json

parser = argparse.ArgumentParser()
parser.add_argument('-mname','--morgan_name',required=True)
parser.add_argument('-id','--id_name',required=True)
parser.add_argument('-protein','--protein',required=True)
parser.add_argument('-n_it','--n_iteration',required=True)
parser.add_argument('-file_path','--file_path',required=True)
parser.add_argument('-dd','--data_directory',required=True)
parser.add_argument('-chs','--chunk_size',required=True)

io_args = parser.parse_args()
morgan_name = io_args.morgan_name#'smile_all_1.txt'
id_name = io_args.id_name#update_id.csv
protein = str(io_args.protein)
n_it = int(io_args.n_iteration)
file_path = io_args.file_path
data_directory = io_args.data_directory#zinc/morgan/morgan
chunk_size = io_args.chunk_size


it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
mor_dir = os.path.join(it_dir, 'morgan')#n_it/morgan

# data_directory = '/home/linjie/projects/D2/zinc1/morgan/morgan'
# mname = 'smile_all_1.txt'

#####get update morgan######
# morgan_file = os.path.join(data_directory, 'smile_all_1.txt')
# update_id_file = os.path.join(mor_dir,'update_id.csv')
##get extract id####
ex_id = pd.DataFrame(columns=['zinc_id'])
for i in range(1, n_it + 1):
    for f in glob.glob(os.path.join(file_path, protein, 'iteration_' + str(i), '*_set.txt')):
        tmp_set = pd.read_csv(f, sep=',', header=0)
        tmp_set.columns = ['zinc_id']
        ex_id = pd.concat([ex_id, tmp_set])
print('get label ok')


def get_update_mor(morgan,ex_id) :
    morgan.columns = ['zinc_id','mor']
    update_morgan = morgan.loc[-morgan.zinc_id.isin(ex_id['zinc_id']),:]
    # print(len(update_morgan))
    return update_morgan

def prediction_morgan(morgan,ex_id,models,thresh):
    update_morgan = get_update_mor(morgan,ex_id)
    # print('get update morgan ok')
    per_time = len(update_morgan)
    n_features = 1024
    z_id = []
    #thresh = tr
    X_set = np.zeros([per_time,n_features],dtype='float16')
    total_passed = 0
    no=0
    for line in update_morgan:
        # tmp=line.rstrip().split(',')
        tmp = re_split.split(' |,', line)
        on_bit_vector = tmp[1:]
        z_id.append(tmp[0])
        for elem in on_bit_vector:
            X_set[no,int(elem)] = 1
        no+=1
        if no == per_time:
            X_set = X_set[:no,:]
            pred = []
            for Progressive_docking in models:
                pred.append(Progressive_docking.predict(X_set))

            with open(it_dir+'/morgan_1024_predictions/'+morgan_name,'a') as ref:
                for j in range(len(pred[0])):
                    is_pass = 0
                    for i,thr in enumerate(thresh):
                        if float(pred[i][j])>thr:
                            is_pass+=1
                    if is_pass>=1:
                        total_passed+=1
                        ref.write(z_id[j]+','+str(float(pred[i][j]))+'\n')
            X_set = np.zeros([per_time,n_features])
            z_id = []
            no = 0
    if no!=0:
        X_set = X_set[:no,:]
        pred = []
        for Progressive_docking in models:
            pred.append(Progressive_docking.predict(X_set))
        with open(it_dir+'/morgan_1024_predictions/'+morgan_name,'a') as ref:
            for j in range(len(pred[0])):
                is_pass = 0
                for i,thr in enumerate(thresh):
                    if float(pred[i][j])>thr:
                        is_pass+=1
                if is_pass>=1:
                    total_passed+=1
                    ref.write(z_id[j]+','+str(float(pred[i][j]))+'\n')

    return total_passed


if __name__=='__main__':
    start = time.time()
    try:
        os.mkdir(it_dir+'/morgan_1024_predictions')
    except:
        pass

    ###load model###
    thresholds = pd.read_csv(it_dir+'/best_models/thresholds.txt',header=None)
    thresholds.columns = ['model_no','thresh','cutoff']
    tr = []
    models = []
    for f in glob.glob(it_dir+'/best_models/*.h5'):
        mn = int(f.split('/')[-1].split('_')[1])
        tr.append(thresholds[thresholds.model_no==mn].thresh.iloc[0])
        with open(it_dir+'/best_models/model_'+str(mn)+'.json','r') as ref:
            models.append(model_from_json(ref.read()))
        models[-1].load_weights(f)

    ####read morgan ####
    morgan_dir = os.path.join(data_directory, morgan_name)#zinc/morgan/morgan/smile_all_1.txt
    print('morgan_dir',morgan_dir)
    all_mor = pd.read_csv(morgan_dir, sep=' ', header=None,chunksize=chunk_size)
    sum_returned=0
    for i,morgan in enumerate(all_mor):
        t = time.time()
        returned = prediction_morgan(morgan,ex_id,models,tr)
        sum_returned += returned
        print(i,': chunk time',time.time()-t)
        print('total_passed',sum_returned)
    with open(it_dir+'/morgan_1024_predictions/passed_file_ct'+morgan_name.split('_')[-1],'w') as ref:
        ref.write(morgan_name+','+str(sum_returned)+'\n')
    print('all_time:',time.time()-start)
    # os.remove(fn)
    # print('remove',fn,'ok')

