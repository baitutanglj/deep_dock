import os
import time

from config import args

dd_project_file = args.dd_project_file
n_it = args.n_iteration
it_dir = os.path.join(dd_project_file, 'iteration_' + str(n_it))

def extracting_score(label_name,set_name):
    labels = {}
    with open(it_dir+label_name) as ref:
        ref.readline()
        for line in ref:
            if line.strip().split(',')[0] == '':
                continue
            else:
                tmpp = line.strip().split(',')[-1]
                labels[tmpp] = line.strip().split(',')[0]
    os.remove(it_dir+label_name)
    print('len(labels)',len(labels))
    with open(it_dir + set_name, 'w') as ref:
        for keys in labels.keys():
            ref.write(keys + '\n')

    ref1 = open(it_dir+label_name,'a')
    ref1.write('r_i_docking_score,ZINC_ID\n')
    for k,v in labels.items():
        ref1.write(str(v)+','+k)
        ref1.write('\n')
    ref1.close()



if __name__=='__main__':
    start = time.time()
    label_names = ['/training_labels.txt', '/validation_labels.txt', '/testing_labels.txt']
    set_names = ['/train_set.txt', '/valid_set.txt', '/test_set.txt']
    for l, s in zip(label_names, set_names):
        print(l, s)
        extracting_score(l, s)

    print('all_time:',time.time()-start)


