#!/bin/bash

file_path=/home/cloudam/projects
#file_path=/home/linjie/projects/D2/
n_it=$1
it_path=$file_path/dd-project/iteration_$n_it/

cd $it_path/simple_job_predictions/
#for i in {1..64};do
#	bash "simple_job_$i.sh" &
#done
#wait
#echo "END"
for i in {1..64}
do
  sbatch -N 1 -n 1 simple_job_$i.sh
done