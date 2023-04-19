#!/bin/bash

#file_path=/home/cloudam
file_path=/home/linjie/projects/D2/
n_it=$1
it_path=$file_path/dd-project/iteration_$n_it/

cd $it_path/simple_job/

for i in `seq 1 12`; do
  bash "simple_job_$i.sh" -H   || break # if needed 
done
