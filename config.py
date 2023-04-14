import argparse

parser = argparse.ArgumentParser()
#get_data.py
parser.add_argument('-db','--database_dir',type=str,default='/public/software/.local/easybuild/software/virtualflow/libs/enamine/ligand-library')##原始数据库路径
parser.add_argument('-downd','--download_directory',type=str,default='/home/cloudam/projects/download')#下载smiles的保存路径
parser.add_argument('-downmor','--downmor_directory',type=str,default='/home/cloudam/projects/download_morgan')#下载morgan的保存路径
parser.add_argument('-invdir','--invalid_directory',type=str,default='/home/cloudam/projects/invalid')#下载无效smiles的保存路径
#0.2smile_simplification.py
parser.add_argument('-tp','--t_pos',type=int,default=64)#进程数
parser.add_argument('-tn','--t_no',type=int,default=64)#将所有smile切分为几份
###smile_simplification.py
parser.add_argument('-nn','--node_num',type=int,default=2)#节点数
####
parser.add_argument('-fp','--file_path',type=str,default='/home/cloudam/projects')#projects路径
parser.add_argument('-pt','--protein_name',type=str,default='dd-project')#所有迭代结果总目录
parser.add_argument('-ddpf','--dd_project_file',type=str,default='/home/cloudam/projects/dd-project')#所有迭代结果总目录的路径
parser.add_argument('-dd','--data_directory',type=str,default='/home/cloudam/projects/morgan')#morgan路径
parser.add_argument('-zd','--zinc_directory',type=str,default='/home/cloudam/projects/zinc')#切分好后smiles路径
parser.add_argument('-ad','--a2ar_directory',type=str,default='/home/cloudam/projects/a2ar')
parser.add_argument('-n_it','--n_iteration',type=int,default=1)#第几次迭代1-9
#home/cloudam/zinc/zinc1/morgan/morgan或home/cloudam/dd-project/iteration_it-1/morgan_1024_predictions
parser.add_argument('-t_pos','--tot_process',type=int,default=64)#进程数
parser.add_argument('-s','--sample_num',type=int,default=1500000)#每次迭代sample的总数
parser.add_argument('-r','--split_ratio',type=float,default=1/3)#sample的总数分为train,valid,test,比例
parser.add_argument('-ar','--a2ar_ratio',type=float,default=0.6)#a2ar分为train,ef,比例
parser.add_argument('-ds','--docking_split_num',type=int,default=10000)#在docking时每份数据多少条
#sample_job_models_noslurm.py
parser.add_argument('-time','--time',type=int,default=1)#设定训练时长
parser.add_argument('-pdfp','--pd_folder_path',type=str,default='/home/cloudam/projects/pd_python')#代码路径
parser.add_argument('-min_last','--min_mols_last',type=int,default=0.5)
parser.add_argument('-vl','--valid_len',type=str,default=500000)#valid多少条
#simple_job_predictions_noslurm.py
parser.add_argument('-chs','--chunk_size',type=int,default=1000000)#预测时每次预测多少条
#13.enrichment.py
parser.add_argument('-ef','--ef_num',type=int,default=5000)#每次迭代用于计算ef的数据量

args, unparsed = parser.parse_known_args()
# args = parser.parse_args()

