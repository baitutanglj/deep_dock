# deep_dock
The code was built based on [D2](https://github.com/vibudh2209/D2). Thanks a lot for their code sharing!
#run step
0.2smile_simplification.py:切分data为32份
| script | function | parameter |
| 0.2smile_simplification.py | 切分data为32份 |-tp：进程数

| Line number | script | function | parameter
|:---|:---|:---|:---|
| 1 | 0.2smile_simplification.py | 切分data为32份 | -tp：进程数，-fn：下载下来zinc路径， zd：切分后保存的路径            
| 2 | 0.3Morgan_fing.py | 利用smiles得到morgan | -tp：进程数，-zd：smiles路径，-dd：morgan路径
| 3 | 1.count_lines.py | 利用smiles得到morgan | 
| 4 | 2.sampling.py | 利用smiles得到morgan | 
| 5 | 3.sanity_check.py | 利用smiles得到morgan | 
| 6 | 4.Extracting_smiles.py | 利用smiles得到morgan | 
| 7 | 4.2add_a2ar_smi.py | 利用smiles得到morgan | 
| 8 | 5.docking_run.py | 利用smiles得到morgan | 
| 9 | 6.Extracting_labels.py | 利用smiles得到morgan | 
| 10 | 7.Extracting_morgan.py | 利用smiles得到morgan | 
| 11 | 7.2add_a2ar_mor.py | 利用smiles得到morgan | 
| 12 | 8.1simple_job_models_noslurm.py | 利用smiles得到morgan | 
| 13 | 8.2progressive_docking.py | 利用smiles得到morgan | 
| 14 | 9.run_all_bash_in_a_dic.sh | 利用smiles得到morgan | 
| 15 | 10.hyperparameter_result_evaluation.py | 利用smiles得到morgan | 
| 16 | 11.1simple_job_predictions_noslurm.py | 利用smiles得到morgan | 
| 17 | 11.2Prediction_morgan_1024.py | 利用smiles得到morgan | 
| 18 | 12.run_all_prediction.sh | 利用smiles得到morgan | 
| 19 | 13.enrichment.py | 利用smiles得到morgan | 
