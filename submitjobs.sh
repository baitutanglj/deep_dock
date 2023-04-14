#!/bin/bash

#CSVFILEPATH=/home/cloudam/dd-project/iteration_1.csv

module add Anaconda3/2020.02
source activate
conda activate rdkit


file_path=/home/cloudam
#file_path=/home/linjie/projects/D2/
n_it=$1
split_num=$2

it_path=$file_path/dd-project/iteration_$n_it
smi_path=$it_path/smile
echo $it_path
echo $smi_path
cp $file_path/D2/pd_python/submit.sh  $smi_path/
#cp $file_path/pd_python/submit.sh  $smi_path/
cd $smi_path
echo  `pwd`

#chmod 777 ./submit.sh


sort  -d  -t ' ' -k 3 train_smiles_final_updated.smi > train_smiles_final_updated.sorted.smi
sort  -d  -t ' ' -k 3 test_smiles_final_updated.smi > test_smiles_final_updated.sorted.smi
sort  -d  -t ' ' -k 3 valid_smiles_final_updated.smi > valid_smiles_final_updated.sorted.smi

split -l $split_num train_smiles_final_updated.sorted.smi -d -a 4 Train_
echo "r_i_docking_score, ZINC_ID" >> $it_path/training_labels.txt
for i in `ls |grep Train_`;
do
  sbatch -N 1 -n 1 submit.sh $i $it_path/training_labels.txt
done

split -l $split_num valid_smiles_final_updated.sorted.smi -d -a 4 Valid_
echo "r_i_docking_score, ZINC_ID" >> $it_path/validation_labels.txt
for i in `ls |grep Valid_`;
do
  sbatch -N 1 -n 1 submit.sh $i $it_path/validation_labels.txt
done

split -l $split_num test_smiles_final_updated.sorted.smi -d -a 4 Test_
echo "r_i_docking_score, ZINC_ID" >> $it_path/testing_labels.txt
for i in `ls |grep Test_`;
do
  sbatch -N 1 -n 1 submit.sh $i $it_path/testing_labels.txt
done


