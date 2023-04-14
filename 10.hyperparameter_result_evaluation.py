import glob
import os
import re as re_split
from shutil import copy2

import numpy as np
import pandas as pd
from config import args
from keras.models import model_from_json
from sklearn.metrics import auc, r2_score
from sklearn.metrics import precision_recall_curve, roc_curve, precision_score, recall_score

print('import bao ok')


n_it = args.n_iteration
time = args.time
protein = args.protein_name
file_path = args.file_path
dd_project_file = args.dd_project_file
data_directory = args.data_directory
sample_num = args.sample_num
split_ratio = args.split_ratio
# vlen = int(sample_num * split_ratio)#valid_len
vlen = args.valid_len

mdd = os.path.join(dd_project_file, 'iteration_' + str(n_it),'morgan')#n_it_morgan_directory
it_dir = os.path.join(dd_project_file, 'iteration_' + str(n_it))
print('set args ok')


db_len = pd.read_csv(data_directory + '/Mol_ct_file.csv',header=None)[[0]].sum()[0]
t_mol = db_len / vlen

hyperparameters = pd.read_csv(it_dir + '/hyperparameter_morgan_with_freq_v3.csv',header=None)

hyperparameters.columns = ['Model_no', 'Over_sampling', 'Batch_size', 'Learning_rate', 'N_layers', 'N_units', 'dropout',
                           'weight', 'cutoff', 'ROC_AUC', 'Pr_0_9', 'tot_left_0_9_mil', 'auc_te', 'pr_te', 're_te',
                           'tot_left_0_9_mil_te', 'tot_positives']

hyperparameters.tot_left_0_9_mil = hyperparameters.tot_left_0_9_mil / vlen
hyperparameters.tot_left_0_9_mil_te = hyperparameters.tot_left_0_9_mil_te / vlen

hyperparameters['re_vl/re_pr'] = 0.9 / hyperparameters.re_te

tmp = hyperparameters.groupby('cutoff')
print('set hyperparameters ok')
cf_values = {}

for mini_df in tmp:
    print(mini_df[0])
    print(mini_df[1]['re_vl/re_pr'].mean())
    print(mini_df[1]['re_vl/re_pr'].std())
    cf_values[mini_df[0]] = mini_df[1]['re_vl/re_pr'].std()

print(cf_values)
model_to_use_with_cf = []
ind_pr = []
count = 0
for cf in cf_values:
    count += 1
    print(count)
    if cf_values[cf] < 0.01:
        tmp = hyperparameters[hyperparameters.cutoff == cf]
        thr = 0.9
        while 1 == 1:
            if len(tmp[tmp.re_te >= thr]) >= 3:
                tmp = tmp[tmp.re_te >= thr]
                break
            else:
                thr = thr - 0.01
                break
        # tmp = tmp[tmp.re_te>=0.895]
        # if len(tmp)
        tmp = tmp.sort_values('pr_te')[::-1]
        try:
            model_to_use_with_cf.append([cf, tmp.Model_no.iloc[0]])
            ind_pr.append([cf, tmp.pr_te.iloc[0]])
        except:
            pass
    else:
        tmp = hyperparameters[hyperparameters.cutoff == cf]
        thr = 0.9
        while 1 == 1:
            if len(tmp[tmp.re_te >= thr]) >= 3:
                tmp = tmp[tmp.re_te >= thr]
                break
            else:
                thr = thr - 0.01
                break
        # tmp = tmp[tmp.re_te>=0.895]
        tmp = tmp.sort_values('pr_te')[::-1]
        try:
            model_to_use_with_cf.append([cf, tmp.Model_no.iloc[:3].values])
            ind_pr.append([cf, tmp.pr_te.iloc[:3].values])
        except:
            pass

# v_temp = []
# for i in range(len(model_to_use_with_cf)):
#    cf = model_to_use_with_cf[i][0]
#    tmp = hyperparameters[hyperparameters.cutoff==cf]
#    t_pos = tmp.tot_positives.unique()
#    if t_pos>150:
#        v_temp.append(model_to_use_with_cf[i])

# model_to_use_with_cf = v_temp

print(model_to_use_with_cf)
print(ind_pr)

all_model_files = {}
for f in glob.glob(it_dir + '/all_models/*'):
    all_model_files[f] = 1

for f in glob.glob(it_dir + '/all_models/*'):
    try:
        mn = int(f.split('/')[-1].split('_')[1])
    except:
        mn = int(f.split('/')[-1].split('_')[1].split('.')[0])
    for i in range(len(model_to_use_with_cf)):
        try:
            if mn in model_to_use_with_cf[i][-1]:
                all_model_files.pop(f)
        except:
            if mn == model_to_use_with_cf[i][-1]:
                all_model_files.pop(f)

for f in all_model_files.keys():
    os.remove(f)


def get_all_x_data(fname, y):
    train_set = np.zeros([1000000, 1024], dtype='float16')
    train_id = []
    with open(fname, 'r') as ref:
        no = 0
        for line in ref:
            # tmp = line.rstrip().split(',')
            tmp = re_split.split(' |,', line)
            train_id.append(tmp[0])
            on_bit_vector = tmp[1:]
            for elem in on_bit_vector:
                train_set[no, int(elem)] = 1
            no += 1
        train_set = train_set[:no, :]
    train_pd = pd.DataFrame(data=train_set)
    train_pd['ZINC_ID'] = train_id
    if len(y.columns) != 2:
        y.reset_index(level=0, inplace=True)
    else:
        print('already 2 columns: ', fname)
    score_col = y.columns.difference(['ZINC_ID'])[0]
    train_data = pd.merge(y, train_pd, how='inner', on=['ZINC_ID'])
    X_train = train_data[train_data.columns.difference(['ZINC_ID', score_col])].values
    y_train = train_data[[score_col]].values
    return X_train, y_train


try:
    valid_pd = pd.read_csv(dd_project_file + '/iteration_1/morgan/valid_morgan_1024_updated.csv', header=None,
                           sep=' ',usecols=[0])
except:
    valid_pd = pd.read_csv(dd_project_file + '/iteration_1/morgan/valid_morgan_1024_updated.csv', header=None,
                           sep=' ',usecols=[0], engine='python')
    try:
        if 'ZINC' in valid_pd.index[0]:
            valid_pd = pd.DataFrame(data=valid_pd.index)
    except:
        pass
valid_pd.columns = ['ZINC_ID']
valid_label = pd.read_csv(dd_project_file + '/iteration_1/validation_labels.txt', sep=',', header=0)
valid_label = pd.DataFrame({'r_i_docking_score': valid_label.iloc[:, 0], 'ZINC_ID': valid_label.iloc[:, 1]})#4899
validation_data = pd.merge(valid_label, valid_pd, how='inner', on=['ZINC_ID'])
validation_data.set_index('ZINC_ID', inplace=True)
y_valid = validation_data

try:
    test_pd = pd.read_csv(dd_project_file + '/iteration_1/morgan/test_morgan_1024_updated.csv', header=None,
                          sep=' ',usecols=[0])
except:
    test_pd = pd.read_csv(dd_project_file + '/iteration_1/morgan/test_morgan_1024_updated.csv', header=None,
                          sep=' ',usecols=[0], engine='python')
    try:
        if 'ZINC' in test_pd.index[0]:
            test_pd = pd.DataFrame(data=test_pd.index)
    except:
        pass
test_pd.columns = ['ZINC_ID']
test_label = pd.read_csv(dd_project_file + '/iteration_1/testing_labels.txt', sep=',', header=0)
test_label = pd.DataFrame({'r_i_docking_score': test_label.iloc[:, 0], 'ZINC_ID': test_label.iloc[:, 1]})
testing_data = pd.merge(test_label, test_pd, how='inner', on=['ZINC_ID'])
testing_data.set_index('ZINC_ID', inplace=True)
y_test = testing_data

try:
    train_pd = pd.read_csv(dd_project_file + '/iteration_1/morgan/train_morgan_1024_updated.csv', header=None,
                           sep=' ',usecols=[0])
except:
    train_pd = pd.read_csv(dd_project_file + '/iteration_1/morgan/train_morgan_1024_updated.csv', header=None,
                           sep=' ',usecols=[0], engine='python')
    try:
        if 'ZINC' in train_pd.index[0]:
            train_pd = pd.DataFrame(data=train_pd.index)
    except:
        pass
train_pd.columns = ['ZINC_ID']
train_label = pd.read_csv(dd_project_file + '/iteration_1/training_labels.txt', sep=',', header=0)
train_label = pd.DataFrame({'r_i_docking_score': train_label.iloc[:, 0], 'ZINC_ID': train_label.iloc[:, 1]})
training_data = pd.merge(train_label, train_pd, how='inner', on=['ZINC_ID'])
training_data.set_index('ZINC_ID', inplace=True)
y_train = training_data

X_valid, y_valid = get_all_x_data(dd_project_file+ '/iteration_1/morgan/valid_morgan_1024_updated.csv',
                                  y_valid)

X_test, y_test = get_all_x_data(dd_project_file + '/iteration_1/morgan/test_morgan_1024_updated.csv', y_test)

X_train, y_train = get_all_x_data(dd_project_file + '/iteration_1/morgan/train_morgan_1024_updated.csv',
                                  y_train)


# valid_label = pd.read_csv(file_path+'/'+protein+'/iteration_'+str(1)+'/validation_labels.txt')#4899
db_len = pd.read_csv(data_directory+'/Mol_ct_file.csv',header=None)[[0]].sum()[0]
t_mol = db_len / vlen
fold = db_len/(vlen*100)
total_mols = t_mol

is_v2 = [False] * len(model_to_use_with_cf)
for i in range(len(model_to_use_with_cf)):
    cf = model_to_use_with_cf[i][0]
    if np.sum(y_valid < cf) <= 10000:
        is_v2[i] = True

for i in range(len(model_to_use_with_cf)):
    if is_v2[i] == True:
        try:
            model_to_use_with_cf[i][1] = model_to_use_with_cf[i][1][0]
        except:
            pass

if n_it == 1:
    is_v2 = [False] * len(model_to_use_with_cf)

cf_with_left = {}
thresholds = {}
all_sc = {}
for i in range(len(model_to_use_with_cf)):
    try:
        t_models = len(model_to_use_with_cf[i][-1])
    except:
        t_models = 1
    cf = model_to_use_with_cf[i][0]
    path_to_model = it_dir + '/all_models/'
    if t_models == 1:
        print('its a single model')
        model_to_use = model_to_use_with_cf[i][-1]
        with open(path_to_model + '/model_' + str(model_to_use) + '.json', 'r') as ref:
            Progressive_docking = model_from_json(ref.read())
        Progressive_docking.load_weights(path_to_model + '/model_' + str(model_to_use) + '_weights.h5')
        if is_v2[i]:
            print('using train as validaition')
            prediction_valid = Progressive_docking.predict(X_valid)
            # print('prediction_valid', prediction_valid)
            precision_vl, recall_vl, thresholds_vl = precision_recall_curve(y_valid < cf, prediction_valid)
            fpr_vl, tpr_vl, thresh_vl = roc_curve(y_valid < cf, prediction_valid)
            r2 = r2_score(valid_label['r_i_docking_score'],prediction_valid)
            print('r2',r2)

        else:
            print('using valid as validation')
            prediction_valid = Progressive_docking.predict(X_valid)
            # print('prediction_valid', prediction_valid)
            precision_vl, recall_vl, thresholds_vl = precision_recall_curve(y_valid < cf, prediction_valid)
            fpr_vl, tpr_vl, thresh_vl = roc_curve(y_valid < cf, prediction_valid)
            r2 = r2_score(valid_label['r_i_docking_score'],prediction_valid)
            print('r2',r2)


        pr_vl = precision_vl[np.where(recall_vl > 0.90)[0][-1]]
        tr = thresholds_vl[np.where(recall_vl > 0.90)[0][-1]]
        prediction_test = Progressive_docking.predict(X_test)
        precision_te, recall_te, thresholds_te = precision_recall_curve(y_test < cf, prediction_test)
        fpr_te, tpr_te, thresh_te = roc_curve(y_test < cf, prediction_test)
        auc_te = auc(fpr_te, tpr_te)
        pr_te = precision_te[np.where(thresholds_te > tr)[0][0]]
        re_te = recall_te[np.where(thresholds_te > tr)[0][0]]
        pos_ct_orig = np.sum(y_test < cf)
        t_train_mol = len(y_test)
        print('cf, re_te, pr_te, auc_te, pos_ct_orig / t_train_mol',cf, re_te, pr_te, auc_te, pos_ct_orig / t_train_mol)
        total_left_te = re_te * pos_ct_orig / pr_te * total_mols * vlen / t_train_mol
        print('total_left_te',total_left_te)
        all_sc[cf] = [cf, re_te, pr_te, auc_te, total_left_te]
        cf_with_left[cf] = total_left_te
        thresholds[cf] = tr
    else:
        print('its an ensemble')
        model_to_use = model_to_use_with_cf[i][-1]
        models = []
        for mn in model_to_use:
            with open(path_to_model + '/model_' + str(mn) + '.json', 'r') as ref:
                models.append(model_from_json(ref.read()))
            models[-1].load_weights(path_to_model + '/model_' + str(mn) + '_weights.h5')
        prediction_valid = []
        scc = []
        for Progressive_docking in models:
            if is_v2[i]:
                print('using train as validation')
                prediction_valid.append(Progressive_docking.predict(X_valid))
                precision_vl_tmp, recall_vl_tmp, thresholds_vl_tmp = precision_recall_curve(y_valid < cf,
                                                                                            prediction_valid[-1])
            else:
                print('using valid as validation')
                prediction_valid.append(Progressive_docking.predict(X_valid))
                precision_vl_tmp, recall_vl_tmp, thresholds_vl_tmp = precision_recall_curve(y_valid < cf,
                                                                                            prediction_valid[-1])
            scc.append([precision_vl_tmp, recall_vl_tmp, thresholds_vl_tmp])
        tr = []
        for precision_vl_tmp, recall_vl_tmp, thresholds_vl_tmp in scc:
            tr.append(thresholds_vl_tmp[np.where(recall_vl_tmp > 0.90)[0][-1]])
        thresholds[cf] = tr
        '''
        avg_pred = np.zeros([len(y_valid),])
        for i in range(len(prediction_valid)):
            avg_pred += (prediction_valid[i]>=tr[i]).reshape(-1,)
        avg_pred = avg_pred>=1
        pr_vl_avg = precision_score(y_valid<cf,avg_pred)
        re_vl_avg = recall_score(y_valid<cf,avg_pred)
        pos_ct_orig = np.sum(y_valid<cf)
        t_train_mol = len(y_valid)
        total_left_vl = re_vl_avg*pos_ct_orig/pr_vl_avg*total_mols*vlen/t_train_mol
        '''
        prediction_test = []
        scc_test = []
        for Progressive_docking in models:
            prediction_test.append(Progressive_docking.predict(X_test))
            precision_te_tmp, recall_te_tmp, thresholds_te_tmp = precision_recall_curve(y_test < cf,
                                                                                        prediction_test[-1])
            scc_test.append([precision_te_tmp, recall_te_tmp, thresholds_te_tmp])
        avg_pred = np.zeros([len(y_test), ])
        for i in range(len(prediction_test)):
            avg_pred += (prediction_test[i] >= tr[i]).reshape(-1, )
        avg_pred = avg_pred >= 2
        fpr_te_avg, tpr_te_avg, thresh_te_avg = roc_curve(y_test < cf, avg_pred)
        auc_te_avg = auc(fpr_te_avg, tpr_te_avg)
        pr_te_avg = precision_score(y_test < cf, avg_pred)
        re_te_avg = recall_score(y_test < cf, avg_pred)
        pos_ct_orig = np.sum(y_test < cf)
        t_train_mol = len(y_test)
        print(cf, re_te_avg, pr_te_avg, auc_te_avg, pos_ct_orig / t_train_mol)
        total_left_te = re_te_avg * pos_ct_orig / pr_te_avg * total_mols * vlen / t_train_mol
        all_sc[cf] = [cf, re_te_avg, pr_te_avg, auc_te_avg, total_left_te]
        cf_with_left[cf] = total_left_te

print('cf_with_left',cf_with_left)

min_left_cf = total_mols * vlen
cf_to_use = 0
for keys in cf_with_left:
    if cf_with_left[keys] < min_left_cf:
        min_left_cf = cf_with_left[keys]
        cf_to_use = keys

print('cf_to_use',cf_to_use)
print('min_left_cf',min_left_cf)

with open(it_dir + '/best_model_stats.txt', 'w') as ref:
    ref.write('model_cutoff,model_precision,model_recall,model_auc,total_pred_left\n')
    cf, re, pr, auc, tot_le = all_sc[cf_to_use]
    ref.write(str(cf) + ',' + str(pr) + ',' + str(re) + ',' + str(auc) + ',' + str(tot_le))

try:
    os.mkdir(it_dir + '/best_models')
except:
    pass
for i in range(len(model_to_use_with_cf)):
    if model_to_use_with_cf[i][0] == cf_to_use:
        try:
            copy2(path_to_model + '/model_' + str(model_to_use_with_cf[i][-1]) + '.json',
                  it_dir + '/best_models/')
            copy2(path_to_model + '/model_' + str(model_to_use_with_cf[i][-1]) + '_weights.h5',
                  it_dir + '/best_models/')
            with open(it_dir + '/best_models/thresholds.txt',
                      'w') as ref:
                ref.write(str(model_to_use_with_cf[i][-1]) + ',' + str(thresholds[cf_to_use]) + ',' + str(cf_to_use))
        except:
            for count, mod_no in enumerate(model_to_use_with_cf[i][-1]):
                with open(it_dir + '/best_models/thresholds.txt',
                          'a') as ref:
                    ref.write(str(mod_no) + ',' + str(thresholds[cf_to_use][count]) + ',' + str(cf_to_use) + '\n')
                copy2(path_to_model + '/model_' + str(mod_no) + '.json',
                      it_dir + '/best_models/')
                copy2(path_to_model + '/model_' + str(mod_no) + '_weights.h5',
                      it_dir + '/best_models/')

