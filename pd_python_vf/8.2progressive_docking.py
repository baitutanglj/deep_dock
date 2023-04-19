import argparse
import glob
import os
import random
import re
import time

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.callbacks import EarlyStopping
from keras.layers import Input, Dense, Activation, Dropout
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from sklearn.metrics import auc
from sklearn.metrics import precision_recall_curve, roc_curve

# from config_my import args

parser = argparse.ArgumentParser()
parser.add_argument('-num_units', '--nu', required=True)
parser.add_argument('-dropout', '--df', required=True)
parser.add_argument('-learn_rate', '--lr', required=True)
parser.add_argument('-bin_array', '--ba', required=True)
parser.add_argument('-wt', '--wt', required=True)
parser.add_argument('-cf', '--cf', required=True)
parser.add_argument('-n_it', '--n_it', required=True)
parser.add_argument('-t_mol', '--t_mol', required=True)
parser.add_argument('-bs', '--bs', required=True)
parser.add_argument('-os', '--os', required=True)
parser.add_argument('-protein', '--protein', required=True)
parser.add_argument('-file_path', '--file_path', required=True)
parser.add_argument('-run_time', '--run_time', required=True)
parser.add_argument('-vl','--valid_len',type=int,default=10000)
io_args = parser.parse_args()

nu = int(io_args.nu)
df = float(io_args.df)
lr = float(io_args.lr)
ba = int(io_args.ba)
wt = float(io_args.wt)
cf = float(io_args.cf)
n_it = int(io_args.n_it)
bs = int(io_args.bs)
oss = int(io_args.os)
t_mol = float(io_args.t_mol)
protein = io_args.protein
file_path = io_args.file_path
run_time = int(io_args.run_time)
vlen = io_args.valid_len
print(nu, df, lr, ba, wt, cf, bs, oss, protein, file_path, run_time)

# n_it = args.n_iteration
# # n_it = 2
# run_time = args.time
# protein = args.protein_name
# file_path = args.file_path
# data_directory = args.data_directory
# pd_folder_path = args.pd_folder_path
# dd_project_file = args.dd_project_file
# min_last = args.min_mols_last
# t_mol=200.0
# nu = 1000
# df = 0.7
# lr = 0.0001
# ba = 2
# wt  = 2
# cf = -11.0
# oss = 10
# bs = 256

prefix = ['_morgan_1024_updated.csv']
total_mols = t_mol  # 200
print('t_mol',t_mol)

try:
    os.mkdir(file_path + '/' + protein + '/iteration_' + str(n_it) + '/all_models')
except:
    pass

is_v2 = False

##get label####
train_data = pd.read_csv(
    file_path + '/' + protein + '/iteration_' + str(1) + '/training_labels.txt',
    sep=',',header=0)
test_data = pd.read_csv(
    file_path + '/' + protein + '/iteration_' + str(1) + '/testing_labels.txt',
    sep=',',header=0)
validation_data = pd.read_csv(
    file_path + '/' + protein + '/iteration_' + str(1) + '/validation_labels.txt',
    sep=',',header=0)


if n_it != 1:
    for i in range(2, n_it + 1):
        for f in glob.glob(os.path.join(file_path, protein, 'iteration_' + str(i), '*_labels.txt')):
            tmp_label = pd.read_csv(f, sep=',', header=0)
            train_data = pd.concat([train_data, tmp_label])
print('get label ok')

train_data.set_index('ZINC_ID', inplace=True)
validation_data.set_index('ZINC_ID', inplace=True)
test_data.set_index('ZINC_ID', inplace=True)
print('train_data.shape, validation_data.shape, test_data.shape',
      train_data.shape, validation_data.shape, test_data.shape)
y_train = train_data < cf
y_valid = validation_data < cf
y_test = test_data < cf
print('y_train.sum()',y_train.sum())
print('y_valid.sum()',y_valid.sum())
print('y_test.sum()',y_test.sum())

t_train_mol = len(y_train)
pos_ct_orig = y_train.r_i_docking_score.sum()


y_pos = y_train[y_train.r_i_docking_score == 1]
y_neg = y_train[y_train.r_i_docking_score == 0]

pos_ct = y_pos.shape[0]
neg_ct = y_neg.shape[0]


print('pos_ct, pos_ct_orig, neg_ct',pos_ct, pos_ct_orig, neg_ct)

sample_size = np.min([neg_ct, 125000, pos_ct * oss])

print('sample_size',sample_size)

Oversampled_zid = {}
Oversampled_zid_y = {}
for i in range(sample_size):
    idx = random.randint(0, pos_ct - 1)
    idx_neg = random.randint(0, neg_ct - 1)
    try:
        Oversampled_zid[y_pos.index[idx]] += 1
    except:
        Oversampled_zid[y_pos.index[idx]] = 1
        Oversampled_zid_y[y_pos.index[idx]] = 1
    try:
        Oversampled_zid[y_neg.index[idx_neg]] += 1
    except:
        Oversampled_zid[y_neg.index[idx_neg]] = 1
        Oversampled_zid_y[y_neg.index[idx_neg]] = 0
y_pos = []
y_neg = []


def get_x_data(Oversampled_zid, fname):
    with open(fname, 'r') as ref:
        no = 0
        for line in ref:
            # tmp = line.rstrip().split(',')
            tmp = re.split(' |,', line)
            if tmp[0] in Oversampled_zid.keys():
                if type(Oversampled_zid[tmp[0]]) != np.ndarray:
                    train_set = np.zeros([1, 1024])
                    on_bit_vector = tmp[1:]
                    for elem in on_bit_vector:
                        train_set[0, int(elem)] = 1
                    Oversampled_zid[tmp[0]] = np.repeat(train_set, Oversampled_zid[tmp[0]], axis=0)
                else:
                    continue
    return  Oversampled_zid


def get_all_x_data(fname, y):
    train_set = np.zeros([1000000, 1024], dtype='float16')
    train_id = []
    with open(fname, 'r') as ref:
        no = 0
        for line in ref:
            # tmp = line.rstrip().split(' ')
            tmp = re.split(' |,',line)
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
    score_col = y.columns.difference(['ZINC_ID'])[0]#'r_i_docking_score'

    train_data = pd.merge(y, train_pd, how='inner', on=['ZINC_ID'])#0      GVK124471544              False  0.0  ...   0.0   0.0      GVK124471544
    X_train = train_data[train_data.columns.difference(['ZINC_ID', score_col])].values#[0.0, 1.0, 0.0, ..., 0.0, 0.0, 'GVK124471544'],
    y_train = train_data[[score_col]].values#array([[False],[False],....,[False]])
    return X_train, y_train


print('len(Oversampled_zid)',len(Oversampled_zid))#6132

X_valid, y_valid = get_all_x_data(file_path + '/' + protein + '/iteration_' + str(1) +
                                  '/morgan/valid_morgan_1024_updated.csv', y_valid)
X_test, y_test = get_all_x_data(file_path + '/' + protein + '/iteration_' + str(1) +
                                '/morgan/test_morgan_1024_updated.csv', y_test)
Oversampled_zid_2 = get_x_data(Oversampled_zid, file_path + '/' + protein + '/iteration_' + str(1) +
                                '/morgan/train_morgan_1024_updated.csv')
if n_it != 1:
    for i in (2,n_it+1):
        for f in glob.glob(os.path.join(file_path, protein, 'iteration_' + str(i),
                                        'morgan','*_morgan_1024_updated.csv')):
            Oversampled_zid_2.update(get_x_data(Oversampled_zid,f))

ct = 0
Oversampled_X_train = np.zeros([sample_size * 2, 1024])
Oversampled_y_train = np.zeros([sample_size * 2, 1])
for keys in Oversampled_zid_2.keys():
    tt = len(Oversampled_zid_2[keys])
    Oversampled_X_train[ct:ct + tt] = Oversampled_zid_2[keys]
    Oversampled_y_train[ct:ct + tt] = Oversampled_zid_y[keys]
    ct += tt

try:
    print(Oversampled_X_train.shape, Oversampled_y_train.shape, X_valid.shape, y_valid.shape, X_test.shape,
          y_test.shape)
except:
    print(Oversampled_X_train.shape, Oversampled_y_train.shape, X_valid.shape, y_valid.shape)

from keras.callbacks import Callback


class TimedStopping(Callback):
    '''Stop training when enough time has passed.
    # Arguments
        seconds: maximum time before stopping.
        verbose: verbosity mode.
    '''

    def __init__(self, seconds=None, verbose=1):
        super(Callback, self).__init__()

        self.start_time = 0
        self.seconds = seconds * 3600
        self.verbose = verbose

    def on_train_begin(self, logs={}):
        self.start_time = time.time()

    def on_epoch_end(self, epoch, logs={}):
        print('epoch done')
        if time.time() - self.start_time > self.seconds:
            self.model.stop_training = True
            if self.verbose:
                print('Stopping after %s seconds.' % self.seconds)


def Progressive_Docking(input_shape, num_units=32, bin_array=[0, 1, 0], dropoutfreq=0.8):
    X_input = Input(input_shape)
    X = X_input
    for j, i in enumerate(bin_array):
        if i == 0:
            X = Dense(num_units, name="Hidden_Layer_%i" % (j + 1))(X)
            X = BatchNormalization()(X)
            X = Activation('relu')(X)
        else:
            X = Dropout(dropoutfreq)(X)
    X = Dense(1, activation='sigmoid', name="Output_Layer")(X)
    model = Model(inputs=X_input, outputs=X, name='Progressive_Docking')
    return model


progressive_docking = Progressive_Docking(Oversampled_X_train.shape[1:], num_units=nu, bin_array=ba * [0, 1],
                                          dropoutfreq=df)
#Oversampled_X_train.shape[1:]#(1024,)
adam_opt = tf.train.AdamOptimizer(learning_rate=lr, epsilon=1e-06)
progressive_docking.compile(optimizer=adam_opt, loss='binary_crossentropy', metrics=['accuracy'])

es = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=0, mode='auto')
es1 = TimedStopping(seconds=run_time)
cw = {0: wt, 1: 1}

progressive_docking.fit(Oversampled_X_train, Oversampled_y_train, epochs=500, batch_size=bs, shuffle=True,
                        class_weight=cw, verbose=1, validation_data=[X_valid, y_valid], callbacks=[es, es1])



print('using valid as validation')
prediction_valid = progressive_docking.predict(X_valid)
print('prediction_valid', prediction_valid)
precision_vl, recall_vl, thresholds_vl = precision_recall_curve(y_valid, prediction_valid)
fpr_vl, tpr_vl, thresh_vl = roc_curve(y_valid, prediction_valid)
auc_vl = auc(fpr_vl, tpr_vl)
pr_vl = precision_vl[np.where(recall_vl > 0.9)[0][-1]]
pos_ct_orig = np.sum(y_valid)
print('validation  pos_ct_orig',pos_ct_orig)
Total_left = 0.9 * pos_ct_orig / pr_vl * total_mols * vlen / len(y_valid)
print('validation Total_left',Total_left)
tr = thresholds_vl[np.where(recall_vl > 0.90)[0][-1]]
print('tr',tr)
try:
    with open(file_path + '/' + protein + '/iteration_' + str(n_it) + '/model_no.txt', 'r') as ref:
        mn = int(ref.readline().rstrip()) + 1
    with open(file_path + '/' + protein + '/iteration_' + str(n_it) + '/model_no.txt', 'w') as ref:
        ref.write(str(mn))
except:
    mn = 1
    with open(file_path + '/' + protein + '/iteration_' + str(n_it) + '/model_no.txt', 'w') as ref:
        ref.write(str(mn))

with open(file_path + '/' + protein + '/iteration_' + str(n_it) + '/all_models/model_' + str(mn) + '.json', 'w') as ref:
    ref.write(progressive_docking.to_json())
progressive_docking.save_weights(
    file_path + '/' + protein + '/iteration_' + str(n_it) + '/all_models/model_' + str(mn) + '_weights.h5')

prediction_test = progressive_docking.predict(X_test)
precision_te, recall_te, thresholds_te = precision_recall_curve(y_test, prediction_test)
fpr_te, tpr_te, thresh_te = roc_curve(y_test, prediction_test)
auc_te = auc(fpr_te, tpr_te)
pr_te = precision_te[np.where(thresholds_te > tr)[0][0]]
re_te = recall_te[np.where(thresholds_te > tr)[0][0]]
pos_ct_orig = np.sum(y_test)#36
Total_left_te = re_te * pos_ct_orig / pr_te * total_mols * vlen / len(y_test)
print('auc_te',auc_te)
print('pr_te',pr_te)
print('re_te',re_te)
print('pos_ct_orig',pos_ct_orig)
print('Total_left_te',Total_left_te)

with open(file_path + '/' + protein + '/iteration_' + str(n_it) + '/hyperparameter_morgan_with_freq_v3.csv',
          'a') as ref:
    ref.write(str(mn) + ',' + str(oss) + ',' + str(bs) + ',' + str(lr) + ',' + str(ba) + ',' + str(nu) + ',' + str(
        df) + ',' + str(wt) + ',' + str(cf) + ',' + str(auc_vl) + ',' + str(pr_vl) + ',' + str(Total_left) + ',' + str(
        auc_te) + ',' + str(pr_te) + ',' + str(re_te) + ',' + str(Total_left_te) + ',' + str(pos_ct_orig) + '\n')

print('y_train.sum()',y_train.sum())#39
print('y_valid.sum()',y_valid.sum())#43
print('y_test.sum()',y_test.sum())#36
print('sample_size',sample_size)