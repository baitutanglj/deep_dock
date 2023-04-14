import glob
import os
import time
from contextlib import closing
from multiprocessing import Pool

import numpy as np
from config import args

protein = args.protein_name
file_path = args.file_path
n_it =  args.n_iteration
data_directory = args.data_directory
tot_process = args.tot_process

##dir name
it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
it_dir_old = os.path.join(file_path, protein, 'iteration_' + str(n_it-1))
mor_dir = os.path.join(it_dir, 'morgan')

def extract_morgan(file_name):
    train= {}
    test = {}
    valid = {}
    ef = {}
    with open(it_dir+"/train_set.txt",'r') as ref:
        for line in ref:
            train[line.rstrip()] = 0
    with open(it_dir+"/valid_set.txt",'r') as ref:
        for line in ref:
            valid[line.rstrip()] = 0
    with open(it_dir+"/test_set.txt",'r') as ref:
        for line in ref:
            test[line.rstrip()] = 0
    with open(it_dir+"/ef_set.txt",'r') as ref:
        for line in ref:
            ef[line.rstrip()] = 0
    #for file_name in file_names:
    ref1 = open(mor_dir+'/train_'+file_name.split('/')[-1],'a')
    ref2 = open(mor_dir+'/valid_'+file_name.split('/')[-1],'a')
    ref3 = open(mor_dir+'/test_'+file_name.split('/')[-1],'a')
    ref4 = open(mor_dir+'/ef_'+file_name.split('/')[-1],'a')
    with open(file_name,'r') as ref:
        flag=0
        for line in ref:
            tmpp = line.strip().split(' ')[0]
            if tmpp in train.keys():
                train[tmpp]+=1
                fn = 1
                if train[tmpp]==1: flag=1
            elif tmpp in valid.keys():
                valid[tmpp]+=1
                fn = 2
                if valid[tmpp]==1: flag=1
            elif tmpp in test.keys():
                test[tmpp]+=1
                fn = 3
                if test[tmpp]==1: flag=1
            elif tmpp in ef.keys():
                ef[tmpp] += 1
                fn = 4
                if ef[tmpp] == 1: flag = 1
            if flag==1:
                if fn==1:
                    ref1.write(line)
                if fn==2:
                    ref2.write(line)
                if fn==3:
                    ref3.write(line)
                if fn==4:
                    ref4.write(line)
            flag = 0


def alternate_concat(files):
    to_return = []
    with open(files,'r') as ref:
        for line in ref:
            to_return.append(line)
    return to_return
        
def delete_all(files):
    os.remove(files)
            
def morgan_duplicacy(f_name):
    flag=0
    mol_list = {}
    # print(f_name)#test_morgan_1024.csv
    # print(f_name[:-4])#test_morgan_1024
    ref1 = open(f_name[:-4]+'_updated.csv','a')
    with open(f_name,'r') as ref:
        for line in ref:
            tmpp = line.strip().split(' ')[0]
            if tmpp not in mol_list:
                mol_list[tmpp] = 1
                flag=1
            if flag==1:
                ref1.write(line)
                flag = 0
    os.remove(f_name)
    
    
            
if __name__=='__main__':
    start = time.time()
    try:
        os.mkdir(mor_dir)
    except:
        pass
    for f in glob.glob(mor_dir+'/*'):
        os.remove(f)
    files = []
    for f in glob.glob(data_directory+"/smile_all_*.txt"):
        files.append(f)
    
    t=time.time()
    with closing(Pool(np.min([tot_process,len(files)]))) as pool:
        pool.map(extract_morgan,files)
    print(time.time()-t)
    
    all_to_delete = []
    for type_to in ['train','valid','test','ef']:
        t=time.time()
        files = []
        for f in glob.glob(os.path.join(mor_dir,type_to+'*')):
            files.append(f)
            all_to_delete.append(f)
        print('len(files):',len(files))
        if len(files)==0:
            print("Error in address above")
            break
        with closing(Pool(np.min([tot_process,len(files)]))) as pool:
            to_print = pool.map(alternate_concat,files)
        with open(os.path.join(mor_dir, type_to + '_morgan_1024.csv'), 'w') as ref:
            for file_data in to_print:
                for line in file_data:
                    ref.write(line)
        to_print = []
        print(type_to,time.time()-t)

    f_names = []
    for f in glob.glob(file_path+'/'+protein+'/iteration_'+str(n_it)+'/morgan/*morgan*'):
        f_names.append(f)

    t=time.time()
    with closing(Pool(np.min([tot_process,len(f_names)]))) as pool:
        pool.map(morgan_duplicacy,f_names)
    print(time.time()-t)
        
    with closing(Pool(np.min([tot_process,len(all_to_delete)]))) as pool:
        pool.map(delete_all,all_to_delete)

    os.rename(mor_dir + '/ef_morgan_1024_updated.csv', mor_dir + '/ef.txt')
    print('all_time:',time.time()-start)
####################################
# morgan_directory = '/home/linjie/projects/D2/zinc1/morgan/morgan'
# file_path = '/home/linjie/projects/D2'
# protein = 'dd-project'
# data_directory = '/home/linjie/projects/D2/zinc1/morgan/morgan'
# n_it = 1
# tot_process = 32
# files = []
# for f in glob.glob(morgan_directory+"/*.txt"):
#     files.append(f)
#
# train= {}
# test = {}
# valid = {}
# with open(it_dir+"/train_set.txt",'r') as ref:
#     for line in ref:
#         train[line.rstrip()] = 0
# with open(it_dir+"/valid_set.txt",'r') as ref:
#     for line in ref:
#         valid[line.rstrip()] = 0
# with open(it_dir+"/test_set.txt",'r') as ref:
#     for line in ref:
#         test[line.rstrip()] = 0
# file_name = files[0]
# ref1 = open(mor_dir+'train_'+file_name.split('/')[-1],'w')
# ref2 = open(mor_dir+'valid_'+file_name.split('/')[-1],'w')
# ref3 = open(mor_dir+'test_'+file_name.split('/')[-1],'w')
# with open(file_name,'r') as ref:
#     flag=0
#     for line in ref:
#         tmpp = line.strip().split(',')[0]
#         if tmpp in train.keys():
#             train[tmpp]+=1
#             fn = 1
#             if train[tmpp]==1: flag=1
#         elif tmpp in valid.keys():
#             valid[tmpp]+=1
#             fn = 2
#             if valid[tmpp]==1: flag=1
#         elif tmpp in test.keys():
#             test[tmpp]+=1
#             fn = 3
#             if test[tmpp]==1: flag=1
#         if flag==1:
#             if fn==1:
#                 ref1.write(line)
#             if fn==2:
#                 ref2.write(line)
#             if fn==3:
#                 ref3.write(line)
#         flag = 0
# ####
# def alternate_concat(files):
#     to_return = []
#     with open(files, 'r') as ref:
#         for line in ref:
#             to_return.append(line)
#     return to_return
# files = ['/home/linjie/projects/D2/dd-project/iteration_1/morgan/train_morgan_1024_updated.csv',
#          '/home/linjie/projects/D2/dd-project/iteration_1/morgan/valid_smile_all_1.txt',
#          '/home/linjie/projects/D2/dd-project/iteration_1/morgan/test_smile_all_1.txt']
# #
# #
# to_print = alternate_concat(files[0])
# ['ZINC000004328962,33,41,64,70,80,114,128,147,167,175,184,191,271,356,366,367,389,392,393,456,475,531,557,561,625,650,659,662,667,695,698,726,792,807,843,849,852,875,884,893,901,980,993\n',
#  'ZINC000006022549,33,41,42,53,64,80,107,128,145,147,167,175,191,202,245,356,386,389,423,428,475,500,530,649,650,695,726,730,745,792,807,843,849,893,901,946,967,973,980,984,1017,1018\n',

# ####
# all_to_delete = []
# for type_to in ['train', 'valid', 'test']:
#     t = time.time()
#     files = []
#     for f in glob.glob(file_path + '/' + protein + '/iteration_' + str(n_it) + '/morgan/' + type_to + '*'):
#         files.append(f)
#         all_to_delete.append(f)
#     print(len(files))
#     if len(files) == 0:
#         print("Error in address above")
#         break
#     '''files
#     ['/home/linjie/projects/D2/dd-project/iteration_1/morgan/train_morgan_1024_updated.csv',
#     '/home/linjie/projects/D2/dd-project/iteration_1/morgan/valid_smile_all_1.txt',
#     '/home/linjie/projects/D2/dd-project/iteration_1/morgan/test_smile_all_1.txt']
#     '''
# with closing(Pool(np.min([tot_process, len(files)]))) as pool:
#     to_print = pool.map(alternate_concat, files)
#
# with open(file_path + '/' + protein + '/iteration_' + str(n_it) + '/morgan/' + train + '_morgan_1024.csv','w') as ref:
#     for file_data in to_print:
#         for line in file_data:
#             ref.write(line)
#     to_print = []
#     print(type_to, time.time() - t)
#
# f_names = []
# for f in glob.glob(file_path + '/' + protein + '/iteration_' + str(n_it) + '/morgan/*morgan*'):
#     f_names.append(f)
#
# t = time.time()
# with closing(Pool(np.min([tot_process, len(f_names)]))) as pool:
#     pool.map(morgan_duplicacy, f_names)
# print(time.time() - t)
#
# with closing(Pool(np.min([tot_process, len(all_to_delete)]))) as pool:
#     pool.map(delete_all, all_to_delete)