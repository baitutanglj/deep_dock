import glob
import multiprocessing
import os
import tarfile
import time
from contextlib import closing
from multiprocessing import Pool

import numpy as np
from config import args
from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem import AllChem

fp = args.file_path
fn = args.folder_name
t_pos = args.t_pos
data_dir = args.database_dir
download_directory = args.download_directory
zinc_directory = args.zinc_directory
data_directory = args.data_directory
invalid_directory = args.invalid_directory

##morgan fing args
nbits = 1024
radius = 2

def get_fnames(data_dir):
    fnames = glob.glob(os.path.join(data_dir, '*'))
    fnames = list(map(lambda n:n.rsplit('/',1)[-1],fnames))
    return fnames

def get_tar_names(fname):
    tar_names = glob.glob(os.path.join(data_dir,fname, '*.tar'))
    return tar_names

def get_content(tar_name):
    tmp_name = tar_name.split(data_dir+'/',1)[-1]
    fname = tmp_name.split('/')[0]
    print(tmp_name, 'start')

    smi = open(os.path.join(download_directory, fname+'_smiles.txt'), 'a')
    mor = open(os.path.join(data_directory, fname+'_smiles.txt'), 'a')
    invalid = open(os.path.join(invalid_directory, fname+'_smiles.txt'), 'a')
    try:
        tar = tarfile.open(tar_name)#打开tar文件
        gz_names = tar.getnames()
    except:
        pass
    else:
        for gz_name in gz_names:
            try:
                gz = tarfile.open(fileobj=tar.extractfile(gz_name))
                pdbqt_names = gz.getnames()
            except:
                pass
            for pdbqt_name in pdbqt_names:
                pdbqt_dict = {}
                try:
                    '''get every id(pdbqt_key) and smile'''
                    pdbqt = gz.extractfile(pdbqt_name).read().decode().splitlines()
                    pdbqt_key = pdbqt_name.split('/')[-1].split('.')[0]
                    pdbqt_dict[pdbqt_key] = pdbqt
                    smile = pdbqt_dict[pdbqt_key][2].split(': ')[-1]
                except:
                    # print('ERROR: Did not find %s in tar archive' % pdbqt_name)
                    continue

                try:
                    '''get morgan when the smile is valid'''
                    arg = np.zeros((1,))
                    mol = Chem.MolFromSmiles(smile)
                    DataStructs.ConvertToNumpyArray(
                            AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits), arg)
                except:
                    invalid.write(pdbqt_key + ' ' +
                                  smile + ' ' +
                                  tmp_name + '/'+
                                  pdbqt_names[0] + '\n')
                    continue

                else:
                    '''save valid smile and morgan'''
                    mor.write(pdbqt_key+' ')
                    mor.write((',').join([str(elem) for elem in np.where(arg == 1)[0]])+'\n')

                    smi.write(pdbqt_key+' '+
                              smile+' '+
                              tmp_name+'/'+
                              pdbqt_names[0]+'\n')

    # invalid.close()
    # mor.close()
    # smi.close()
    # gz.close()
    # tar.close()
    print(tmp_name,'ok')


if __name__ == '__main__':
    start = time.time()
    print('cpu_count()',multiprocessing.cpu_count())
    fnames = get_fnames(data_dir)

    with closing(Pool(multiprocessing.cpu_count())) as pool:
        tar_names = pool.map(get_tar_names, fnames)
    tar_names =sum(tar_names,[])

    print('len(fnames)',len(fnames))
    print('len(tar_names)', len(tar_names))
    with closing(Pool(multiprocessing.cpu_count())) as pool:
        pool.map(get_content, tar_names)
    print('len(fnames)',len(fnames))
    print('len(tar_names)', len(tar_names))
    print('all run time:',time.time()-start)



