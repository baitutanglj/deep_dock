# deep_dock
The code was built based on [D2](https://github.com/vibudh2209/D2). Thanks a lot for their code sharing!
# run step
0.2smile_simplification.py:切分data为32份
| script | function | parameter |
| 0.2smile_simplification.py | 切分data为32份 |-tp：进程数

| Line number | script | function | parameter
|:---|:---|:---|:---|
| 1 | 0.2smile_simplification.py | 切分data为32份 | -tp：进程数，-fn：下载下来zinc路径， zd：切分后保存的路径            
| 2 | 0.3Morgan_fing.py | 利用smiles得到morgan | -tp：进程数，-zd：smiles路径，-dd：morgan路径
| 3 | 1.count_lines.py | 统计每次迭代抽剩的data数量和当前迭代要sample的数量 | -n_it：第n次迭代， -s:sample_num
| 4 | 2.sampling.py | sample id，即XXX_set | -n_it：第n次迭代， -s:sample_num
| 5 | 3.sanity_check.py | 去掉与之前n_it重合的，去掉与tr，v之间重合的| -n_it：第n次迭代
| 6 | 4.Extracting_smiles.py | 找出n_it的tr，v, tsample出来的smiles| -n_it：第n次迭代
| 7 | 4.2add_a2ar_smi.py | 加入a2ar的smiles |
| 8 | 5.docking_run.py | 用4sample的smiles去docking得到labels | -n_it：第n次迭代， -ds：分成多少个smiles为一个文件 
| 9 | submitjobs.sh、submit.sh | 提交docking | submitjobs.sh里的-N可改 
| 10 | 6.Extracting_labels.py | 去掉docking为空的 | -n_it：第n次迭代
| 11 | 7.Extracting_morgan.py | 取出morgan | -n_it：第n次迭代
| 12 | 7.2add_a2ar_mor.py | 加入a2ar的morgan | 
| 13 | 8.1simple_job_models_noslurm.py | 生成12组超参数的.sh文件 | -n_it：第n次迭代， -vl
| 14 | 8.2progressive_docking.py | 定义model | 
| 15 | 9.run_all_bash_in_a_dic.sh | 训练12个sh | 
| 16 | 10.hyperparameter_result_evaluation.py | 用n_it=1d的v和t选best model | 
| 17 | 11.1simple_job_predictions_noslurm.py | 生成预测剩下的32个morgan.txt | -n_it：第n次迭代，-chs 
| 18 | 11.2Prediction_morgan_1024.py | 预测脚本 | 
| 19 | 12.run_all_prediction.sh | 运行步骤11的64个sh | 

