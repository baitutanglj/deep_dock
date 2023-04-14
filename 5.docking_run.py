import os

from config import args

protein = args.protein_name
file_path = args.file_path
n_it = args.n_iteration
ds = args.docking_split_num

os.system('chmod 777' + ' * ' + file_path + '/pd_python/submitjobs_1.sh')
os.system(file_path + '/pd_python/submitjobs_1.sh' +' '+ str(n_it) + ' ' + str(ds))

#os.system('chmod 777' + ' * ' +file_path + '/' + protein + '/iteration_' + str(n_it) + '/smile/' + 'submit.sh')
# os.system('chmod 777'+' * ' +file_path + '/' + protein + '/iteration_' + str(n_it) + '/smile/' + 'submitjobs_1.sh')
# os.system(file_path + '/' + protein + '/iteration_' + str(n_it) + '/smile/' + 'submitjobs_1.sh ' + file_path + ' ' + protein + ' ' + str(n_it))
