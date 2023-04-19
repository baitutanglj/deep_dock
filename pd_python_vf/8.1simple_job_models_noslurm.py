import glob
import math
import os

import numpy as np
import pandas as pd
from config import args

n_it = args.n_iteration
time = args.time
protein = args.protein_name
file_path = args.file_path
data_directory = args.data_directory
pd_folder_path = args.pd_folder_path
dd_project_file = args.dd_project_file
min_last = float(args.min_mols_last)
sample_num = args.sample_num
split_ratio = args.split_ratio
mdd = os.path.join(dd_project_file, 'iteration_' + str(n_it),'morgan')#morgan_directory
it_dir = os.path.join(dd_project_file, 'iteration_' + str(n_it))
# vlen = int(sample_num * split_ratio)#valid_len
vlen = args.valid_len
num_units = [1000,1500,2000]
dropout = [0.7]
learn_rate = [0.0001]
bin_array = [2,3]
wt = [2,3]
bs = [256]
oss = [10]

try:
    os.mkdir(it_dir + '/simple_job')
except:
    pass

for f in glob.glob(it_dir + '/simple_job/*'):
    os.remove(f)


scores_val = []
with open(file_path+'/'+protein+'/iteration_'+str(1)+'/validation_labels.txt','r') as ref:
    ref.readline()
    for line in ref:
        scores_val.append(float(line.rstrip().split(',')[0]))
scores_val = np.array(scores_val)

db_len = pd.read_csv(it_dir+'/Mol_ct_file.csv',header=None)[[0]].sum()[0]
t_mol = db_len / vlen
fold = db_len/(vlen*100)#15
print('db_len',db_len)
print('vlen',vlen)
print('t_mol',t_mol)
print('fold',fold)#2.0


lflist = [math.floor(i) for i in np.linspace(100,1,11)]
good_mol = int(min_last*lflist[n_it-1])
print('lf',lflist[n_it-1])
print('good_mol', good_mol)

cf = [sorted(scores_val)[good_mol]]
print('cf:',cf)
t_avail = len(scores_val[scores_val<cf[0]])
print('t_avail',t_avail)
#save log
df = pd.DataFrame({'n_it':n_it,'good_mol':good_mol,'cf':cf,'t_avail':t_avail},index=[0])
if n_it==1:
    df.to_csv(dd_project_file + '/cut_off_num.csv',mode='a',index=None)
else:
    df.to_csv(dd_project_file + '/cut_off_num.csv', mode='a', index=None,header=None)
print('save log ok')


all_hyperparas = []

for o in oss:
    for batch in bs:
        for nu in num_units:
            for do in dropout:
                for lr in learn_rate:
                    for ba in bin_array:
                        for w in wt:
                            for c in cf:
                                all_hyperparas.append([o,batch,nu,do,lr,ba,w,c])

print('len(all_hyperparas)',len(all_hyperparas))
print(all_hyperparas)


ct=1
for i in range(len(all_hyperparas)):
    with open(file_path+'/'+protein+'/iteration_'+str(n_it)+'/simple_job/simple_job_'+str(ct)+'.sh','w') as ref:
        ref.write('#!/bin/bash\n')
        ref.write('\n')
        ref.write('cd '+pd_folder_path+'\n')
        o,batch,nu,do,lr,ba,w,c = all_hyperparas[i]
        ref.write('/public/software/.local/easybuild/software/Anaconda3/2020.02/envs/rdkit/bin/python '+'8.2progressive_docking.py'+' '+'-num_units'+' '+str(nu)+' '
                  +'-dropout'+' '+str(do)+' '+'-learn_rate'+' '+str(lr)+' '+'-bin_array'+' '+str(ba)+' '+'-wt'+' '+str(w)+' '+'-cf'+' '+str(c)+' '
                  +'-n_it'+' '+str(n_it)+' '+'-t_mol'+' '+str(t_mol)+' '+'-os'+' '+str(o)+' '+'-bs'+' '+str(batch)+' '+'-protein'+' '+protein+' '
                  +'-file_path'+' '+file_path+' '+'-run_time'+' '+ str(time)+' '+'-vl'+' '+str(vlen)+'\n')
    ct+=1


