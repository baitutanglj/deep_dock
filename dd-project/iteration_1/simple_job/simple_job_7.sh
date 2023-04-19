#!/bin/bash

cd /home/linjie/projects/D2/pd_python
/public/software/.local/easybuild/software/Anaconda3/2020.02/envs/rdkit/bin/python 8.2progressive_docking.py -num_units 1500 -dropout 0.7 -learn_rate 0.0001 -bin_array 3 -wt 2 -cf -11.2 -n_it 1 -t_mol 401.3399 -os 10 -bs 256 -protein dd-project -file_path /home/linjie/projects/D2 -run_time 1 -vl 10000
