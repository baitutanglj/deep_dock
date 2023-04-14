import os

from config import args

protein = args.protein_name
file_path = args.file_path
n_it = args.n_iteration
ds = args.docking_split_num###每个任务docking几条数据
sample_num = args.sample_num###每个迭代sample的数据量
vlen = args.valid_len###n_it=1的valid数据量
chunk_size = args.chunk_size
r = args.a2ar_ratio#a2ar切分比例
python_path = '/public/software/.local/easybuild/software/Anaconda3/2020.02/envs/rdkit/bin/python'

run1 = [python_path, '1.count_lines.py', '-n_it', str(n_it), '-s', str(sample_num)]
run2 = [python_path, '2.sampling.py', '-n_it', str(n_it), '-s', str(sample_num)]
run3 = [python_path, '3.sanity_check.py', '-n_it', str(n_it)]
run4 = [python_path, '4.Extracting_smiles.py', '-n_it', str(n_it)]
run4_2 = [python_path, '4.2add_a2ar_smi.py', '-r', str(r)]
run5 = [python_path,'5.docking_run.py', '-n_it', str(n_it)]
run6 = [python_path,'6.Extracting_labels.py', '-n_it', str(n_it)]
run7 = [python_path,'7.Extracting_morgan.py', '-n_it', str(n_it)]
run7_2 = [python_path, '7.2add_a2ar_mor.py', '-r', str(r)]
run8 = [python_path,'8.1simple_job_models_noslurm.py', '-n_it', str(n_it), '-vl', str(vlen)]
run9 = ['bash','9.run_all_bash_in_a_dic.sh', str(n_it)]
run10 = [python_path, '10.hyperparameter_result_evaluation.py', '-n_it', str(n_it), '-vl', str(vlen)]
run11 = [python_path, '11.1simple_job_predictions_noslurm.py', '-n_it', str(n_it),'-chs', str(chunk_size)]
run12 = ['bash', '12.run_all_prediction.sh', str(n_it)]
run13 = [python_path,'13.enrichment.py', '-n_it', str(n_it)]

if n_it == 1:
    runlist = [run1, run2, run3, run4, run4_2, run5, run6, run7,run7_2, run8, run9, run10, run11, run12, run13]
else:
    runlist = [run1,run2,run3,run4,run5,run6,run7,run8,run9,run10,run11,run12,run13]
for i in runlist:
    i = ' '.join(i)
    print(i)
    os.system(i)







############
# os.chdir('/home/linjie/projects/D2/pd_python_path_my')
# lst = os.listdir(os.getcwd())
# for c in lst:
#     if os.path.isfile(c) and c.endswith('.py') and c.find("run_all") == -1 \
#             and c.find("config_my") == -1:  # 去掉run_all.py文件
#         print(c)
#         os.system("python_path ./%s -n_it %s" % (c,3))