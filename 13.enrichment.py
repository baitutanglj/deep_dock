import glob
import os
import re
import time

import numpy as np
import pandas as pd
from config import args
from keras.models import model_from_json

protein = args.protein_name
file_path = args.file_path
data_directory = args.data_directory
dd_project_file = args.dd_project_file
a2ar_directory = args.a2ar_directory
n_it = args.n_iteration
ef_num = args.ef_num


# dir name
it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
it_dir_old = os.path.join(file_path, protein, 'iteration_' + str(n_it-1))
mor_dir = os.path.join(it_dir, 'morgan')


#get ef_update_morgan
morgan = pd.read_csv(mor_dir+'/ef.txt', sep=' ', header=None)
morgan.columns = ['zinc_id','morgan']

#将2个文件合并成一个用于预测
active_EF= pd.read_csv(a2ar_directory + '/ef_a2ar.csv',sep=' ',header=None)
print('len(actives_EF)',len(active_EF))
active_EF.columns = ['zinc_id','morgan']
outfile = active_EF.append(morgan)
print('len(outfile)',len(outfile))
pd.DataFrame(outfile).to_csv(dd_project_file + '/iteration_' + str(n_it) +'/preEF.txt',sep=' ', index=False, header=None)

#读取模型
fname = dd_project_file + '/iteration_' + str(n_it) +'/preEF.txt'
model_path = dd_project_file + '/iteration_' + str(n_it) +'/best_models/'

# thresholds
thresholds = pd.read_csv(model_path + 'thresholds.txt', header=None)
thresholds.columns = ['model_no', 'thresh', 'cutoff']
# thresh = thresholds[thresholds.model_no ==5].thresh.iloc[0]
thresh = thresholds['thresh']


# load model & weight
# import re
# re.findall(r'\d+',glob.glob(model_path + 'model_*.json')[0])[-1]
with open(glob.glob(model_path + 'model_*.json')[0], 'r') as ref:
    model = model_from_json(ref.read())
model.load_weights(glob.glob(model_path + 'model_*_weights.h5')[0])

# main
def prediction_morgan(fname, model,factor):
    with open(fname, "r") as ref:
        lines_tmp = [line for line in ref]
        t = time.time()
        per_time = len(lines_tmp)
        n_features = 1024
        zinc_id = []
        X_set = np.zeros([per_time, n_features])
        no = 0
        for line in lines_tmp:
            tmp = re.split(' |,', line)
            on_bit_vector = tmp[1:]
            zinc_id.append(tmp[0])

            for elem in on_bit_vector:
                X_set[no, int(elem)] = 1
            no = no + 1

            if no == per_time:
                X_set = X_set[:no, :]
                pred = model.predict(X_set)

        pred = pred.flatten()
        # pred = pred.tolist()

    with open(dd_project_file + '/iteration_' + str(n_it) +'pred_results.txt','w') as w:
        d = dict(zip(zinc_id, pred))
        L = sorted(d.items(), key=lambda i: i[1], reverse=True)
        L_dict = dict(L)
        print('len(L_dict)',len(L_dict))
        w.write('\n'.join('%s %s' % x for x in L))
    #w.close()
        
        L_dict_new = {}
        for i,(k,v) in enumerate(L_dict.items()):
            L_dict_new[k]=v
            if i == int(len(L_dict)*factor):
                break
            #return L_dict_new
            
        w = open(dd_project_file + '/iteration_' + str(n_it) +'/best_model_stats.txt', "a")#不覆盖之前的内容
        true_all=0
        for id in L_dict_new.keys():

            if "GVK" in id:
                true_all += 1
            #print(L_dict_new.keys())
    # EF1%
        print('true_all:',true_all)
        EF= (true_all * 1.0) / (int(len(L_dict)*factor) * (len(active_EF) / (ef_num+len(active_EF))))
        print('EF: %.2f equal: %.3f,true_all equal: %d ' % (factor,EF, true_all))
    
    #return EF
        w.write('EF'+ str(factor) + 'equal:' + str(EF)+','+'true_all equal:'+str(true_all))
        w.write('\n')
        w.close()


prediction_morgan(fname, model, 0.01)
prediction_morgan(fname, model, 0.1)
