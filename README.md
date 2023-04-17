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
