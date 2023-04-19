import glob
import os

from config import args

n_it = args.n_iteration
protein = args.protein_name
file_path = args.file_path
data_directory = args.data_directory
pd_folder_path = args.pd_folder_path
chunk_size = args.chunk_size

it_dir = os.path.join(file_path, protein, 'iteration_' + str(n_it))
mor_dir = os.path.join(it_dir, 'morgan')
updated_dir = os.path.join(it_dir, 'updated')


try:
    os.mkdir(it_dir+'/simple_job_predictions')
except:
    pass

for f in glob.glob(it_dir+'/simple_job_predictions/*'):
    os.remove(f)



morgan_files = []
for i,f in enumerate(glob.glob(data_directory+'/smile_all_*.txt')):
    morgan_files.append(f)

id_file = []
for i,f in enumerate(glob.glob(updated_dir+'/smile_all_*.txt')):
    id_file.append(f)

ct = 1
for m,i in zip(morgan_files,id_file):
    with open(it_dir + '/simple_job_predictions/simple_job_'+str(ct)+'.sh','w') as ref:
        ref.write('#!/bin/bash\n')
        #ref.write('#SBATCH --ntasks=1\n')
        #ref.write('#SBATCH --nodes=1\n')
        #ref.write('#SBATCH --gres=gpu:1\n')
        #ref.write('#SBATCH --cpus-per-task=1\n')
        #ref.write('#SBATCH --job-name=phase_5\n')
        #ref.write('#SBATCH --mem=0               # memory per node\n')
        #ref.write('#SBATCH --time='+time+'            # time (DD-HH:MM)\n')
        ref.write('\n')
        ref.write('cd '+pd_folder_path+'\n')
        #ref.write('source '+tf_venv_path+'/bin/activate\n')
        ref.write('/public/software/.local/easybuild/software/Anaconda3/2020.02/envs/rdkit/bin/python '+'11.2Prediction_morgan_1024.py'+' '\
                  +'-mname'+' '+m.split('/')[-1]+' '+'-id'+' ' +i.split('/')[-1]+' '\
                  +'-protein'+' '+protein+' '+'-n_it'+' '+str(n_it)+' '+'-file_path'+' '+file_path+' '\
                  +'-dd'+' '+data_directory+' '+'-chs'+' '+str(chunk_size)+'\n')
    ct+=1

print('ct',ct)