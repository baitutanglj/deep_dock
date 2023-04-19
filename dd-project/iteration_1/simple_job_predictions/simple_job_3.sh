#!/bin/bash

cd /home/linjie/projects/D2/pd_python
/public/software/.local/easybuild/software/Anaconda3/2020.02/envs/rdkit/bin/python 11.2Prediction_morgan_1024.py -mname AB_smiles.txt -id AB_smiles.txt -protein dd-project -n_it 1 -file_path /home/linjie/projects/D2 -dd /home/linjie/projects/D2/zinc1/morgan/morgan -chs 1000000
