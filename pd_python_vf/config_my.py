import argparse

parser = argparse.ArgumentParser()
#get_data.py
parser.add_argument('-db','--database_dir',type=str,default='/home/linjie/projects/D2-master/database')
parser.add_argument('-downd','--download_directory',type=str,default='/home/linjie/projects/D2-master/zinc1/download')
parser.add_argument('-downmor','--downmor_directory',type=str,default='/home/cloudam/projects/download_morgan')
parser.add_argument('-invdir','--invalid_directory',type=str,default='/home/linjie/projects/D2-master/zinc1/invalid')
#download_zinc_old
parser.add_argument('-up','--url_path',type=str,default='/home/linjie/projects/D2-master-master/ZINC-downloader-2D-txt.uri')
# parser.add_argument('-fp','--folder_path',type=str,default='/home/linjie/projects/D2-master')
parser.add_argument('-fn','--folder_name',type=str,default='download_zinc')
parser.add_argument('-tp','--t_pos',type=int,default=32)
parser.add_argument('-tn','--t_no',type=int,default=2)
###smile_simplification.py
parser.add_argument('-nn','--node_num',type=int,default=2)
####
parser.add_argument('-fp','--file_path',type=str,default='/home/linjie/projects/D2-master')#dd-project
parser.add_argument('-pt','--protein_name',type=str,default='dd-project')#/home/cloudam
parser.add_argument('-ddpf','--dd_project_file',type=str,default='/home/linjie/projects/D2-master/dd-project')
parser.add_argument('-dd','--data_directory',type=str,default='/home/linjie/projects/D2-master/zinc1/morgan/morgan')
parser.add_argument('-zd','--zinc_directory',type=str,default='/home/linjie/projects/D2-master/zinc1/zinc1')
parser.add_argument('-ad','--a2ar_directory',type=str,default='/home/linjie/projects/D2-master/zinc1/a2ar')
parser.add_argument('-ind','--index_directory',type=str,default='/home/linjie/projects/D2-master/zinc1/indexdir')
parser.add_argument('-n_it','--n_iteration',type=int,default=1)#1-9
#home/cloudam/zinc/zinc1/morgan/morgan或home/cloudam/dd-project/iteration_it-1/morgan_1024_predictions
parser.add_argument('-t_pos','--tot_process',type=int,default=28)
parser.add_argument('-s','--sample_num',type=int,default=30000)
parser.add_argument('-r','--split_ratio',type=float,default=1/3)
parser.add_argument('-ar','--a2ar_ratio',type=float,default=0.6)
parser.add_argument('-ds','--docking_split_num',type=int,default=1000)
#sample_job_models_noslurm.py
parser.add_argument('-time','--time',type=int,default=1)
parser.add_argument('-pdfp','--pd_folder_path',type=str,default='/home/linjie/projects/D2-master/pd_python')
parser.add_argument('-min_last','--min_mols_last',type=int,default=0.5)
parser.add_argument('-vl','--valid_len',type=int,default=10000)
#simple_job_predictions_noslurm.py
parser.add_argument('-chs','--chunk_size',type=int,default=1000000)
#13.enrichment.py
parser.add_argument('-ef','--ef_num',type=int,default=10000)

args, unparsed = parser.parse_known_args()
# args = parser.parse_args()