import glob
import os
import time

from config import args

protein = args.protein_name
file_path = args.file_path
n_it = args.n_iteration
# dir name
it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
it_dir_old = os.path.join(file_path, protein, 'iteration_' + str(n_it-1))
zinc_dir = os.path.join(it_dir, 'smile')
mor_dir = os.path.join(it_dir, 'morgan')


old_dict = {}
# for i in range(1,n_it):
#     with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(i)+'/training_labels*')[-1]) as ref:
#         ref.readline()
#         for line in ref:
#             tmpp = line.strip().split(',')[-1]
#             old_dict[tmpp] = 1
#     with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(i)+'/validation_labels*')[-1]) as ref:
#         ref.readline()
#         for line in ref:
#             tmpp = line.strip().split(',')[-1]
#             old_dict[tmpp] = 1
#     with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(i)+'/testing_labels*')[-1]) as ref:
#         ref.readline()
#         for line in ref:
#             tmpp = line.strip().split(',')[-1]
#             old_dict[tmpp] = 1
#####
for i in range(1,n_it):
    with open(glob.glob(it_dir+'/train_set*')[-1]) as ref:
        for line in ref:
            tmpp = line.strip().split(',')[0]
            old_dict[tmpp] = 1
    with open(glob.glob(it_dir+'/valid_set*')[-1]) as ref:
        for line in ref:
            tmpp = line.strip().split(',')[0]
            old_dict[tmpp] = 1
    with open(glob.glob(it_dir+'/test_set*')[-1]) as ref:
        for line in ref:
            tmpp = line.strip().split(',')[0]
            old_dict[tmpp] = 1
    # print(time.time()-t)

######
t=time.time()
start = time.time()
new_train = {}
new_valid = {}
new_test = {}
with open(glob.glob(it_dir+'/train_set*')[-1]) as ref:
    for line in ref:
        tmpp = line.strip().split(',')[0]
        new_train[tmpp] = 1
with open(glob.glob(it_dir+'/valid_set*')[-1]) as ref:
    for line in ref:
        tmpp = line.strip().split(',')[0]
        new_valid[tmpp] = 1
with open(glob.glob(it_dir+'/test_set*')[-1]) as ref:
    for line in ref:
        tmpp = line.strip().split(',')[0]
        new_test[tmpp] = 1
print(time.time()-t)

t=time.time()
for keys in new_train.keys():
    if keys in new_valid.keys():
        new_valid.pop(keys)
    if keys in new_test.keys():
        new_test.pop(keys)
for keys in new_valid.keys():
    if keys in new_test.keys():
        new_test.pop(keys)
print(time.time()-t)

for keys in old_dict.keys():
    if keys in new_train.keys():
        new_train.pop(keys)
    if keys in new_valid.keys():
        new_valid.pop(keys)
    if keys in new_test.keys():
        new_test.pop(keys)
        
with open(it_dir+'/train_set.txt','w') as ref:
    for keys in new_train.keys():
        ref.write(keys+'\n')
with open(it_dir+'/valid_set.txt','w') as ref:
    for keys in new_valid.keys():
        ref.write(keys+'\n')
with open(it_dir+'/test_set.txt','w') as ref:
    for keys in new_test.keys():
        ref.write(keys+'\n')
print('all_time:',time.time()-start)

# file_path = '/home/linjie/projects/D2'
# protein = 'dd-project'
# with open(glob.glob(file_path+'/'+protein+'/iteration_'+str(1)+'/train_set*')[-1]) as ref:
#     for line in ref:
#         tmpp = line.strip().split(',')[0]
