import glob
import multiprocessing
import os
import time
from contextlib import closing
from multiprocessing import Pool

# import gzip
import numpy as np
from config import args

fp = args.file_path
t_pos = args.t_pos
t_no = args.t_no#分割成几份
download_directory = args.download_directory#未分割前路径
zinc_directory = args.zinc_directory
data_directory = args.data_directory
node_num = args.node_num
name = 'smile_all_'


def zid_molecules(f_name):
    ct=0
    with open(f_name,'r') as ref:
        for line in ref:
            ct+=1
    return f_name,ct

def delete_all(files):
    os.remove(files)

def concat_morgan_files(file_data):
    file_no = file_data[0]
    files = file_data[1:]
    ref1 = open(os.path.join(zinc_directory,name+str(file_no)+'.txt'),'w')
    for f in files:
        with open(f,'r') as ref:
            for line in ref:
                ref1.write(line)
        # os.remove(f)
    ref1.close()


def get_ct(to_list):
    return np.array([to_list[i][0] for i in range(len(to_list))])

def concat_for_equal(list_files,to_list):
    for i in range(len(list_files)):
        to_list[0].append(list_files[-1-i][-1])
        to_list[0][0] = to_list[0][0] + list_files[-1-i][0]
        ct = get_ct(to_list)
        to_list = [to_list[i] for i in ct.argsort()]
    
if __name__=='__main__':
    print('multiprocessing.cpu_count()',multiprocessing.cpu_count())
    start=time.time()
    try:
        os.mkdir(zinc_directory)
    except:
        pass

    files = []
    for f in glob.glob(download_directory+"/*_smiles.txt"):
        files.append(f)
    with closing(Pool(np.min([multiprocessing.cpu_count(),len(files),t_pos]))) as pool:
        molecule_ct = pool.map(zid_molecules,files)
    print('zid_molecules time.time()-t',time.time()-start)
    ct=[]
    for i in range(len(molecule_ct)):
        ct.append(molecule_ct[i][1])
    print('start np.sum(ct)',np.sum(ct))
    file_ct_list=[]
    for i in range(len(molecule_ct)):
        file_ct_list.append([molecule_ct[i][1],molecule_ct[i][0]])

    file_ct_list = [file_ct_list[i] for i in np.array(ct).argsort()]
    
    to_list = file_ct_list[-t_no:]
    list_files = file_ct_list[:-t_no]

    concat_for_equal(list_files,to_list)

    ct=0
    for i in range(len(to_list)):
        ct+=to_list[i][0]

    print('to_list ct',ct)
    
    files = {}
    for i in range(len(to_list)):
        for j in range(1,len(to_list[i])):
            files[to_list[i][j]] = 1

    print('len(files)',len(files))

    for i in range(len(to_list)):
        to_list[i][0] = i+1
        
    t=time.time()
    with closing(Pool(np.min([multiprocessing.cpu_count()*node_num,len(to_list),t_pos]))) as pool:
        pool.map(concat_morgan_files,to_list)
    print('concat_morgan_files time.time()-t',time.time()-t)
    
    files_morgan = []
    for f in glob.glob(zinc_directory+'/smile_all_*.txt'):
        files_morgan.append(f)

    with closing(Pool(t_no)) as pool:
        molecule_ct = pool.map(zid_molecules,files_morgan)
    
    ct=[]
    for i in range(len(molecule_ct)):
        ct.append(molecule_ct[i][1])
    print('finally np.sum(ct)',np.sum(ct))
    print('all run time', time.time() - start)




