#!/bin/bash

CURDIR=`pwd`

echo "JOBID=$SLURM_JOB_ID"

export INPUT=$1

mkdir -p /dev/shm/dd/$1/$SLURM_JOB_ID/out
mkdir -p /dev/shm/dd/$1/$SLURM_JOB_ID/lib

cp $INPUT /dev/shm/dd/$1/$SLURM_JOB_ID

cd /dev/shm/dd/$1/$SLURM_JOB_ID

echo "input=$INPUT"

cat $INPUT | while read i;
do
echo "i=$i"
filename=`echo "$i"|cut -d ' ' -f 1`
echo "$filename"
smi=`echo "$i"|cut -d ' ' -f 2`
echo "$smi"
paths=`echo "$i"|cut -d ' ' -f 3`
echo "$paths"

pTarFileDir=`echo "$paths"|cut -d '/' -f 1`
echo "$pTarFileDir"
pTarFileName=`echo "$paths"|cut -d '/' -f 2`
echo "$pTarFileName"
tarFileName=`echo "$paths"|cut -d '/' -f 3`
echo "$tarFileName"

unzipedPTarFile_Dir=`echo "$pTarFileName"|cut -d '.' -f 1`
echo "$unzipedPTarFile_Dir"

if test -f "/dev/shm/dd/$1/$SLURM_JOB_ID/lib/$unzipedPTarFile_Dir"; then
    echo "$FILE exists."
else
        rm -rf /dev/shm/dd/$1/$SLURM_JOB_ID/lib/*
        tar xvf /public/software/.local/easybuild/software/virtualflow/libs/enamine/ligand-library/$pTarFileDir/$pTarFileName -C /dev/shm/dd/$1/$SLURM_JOB_ID/lib/
fi

cd /dev/shm/dd/$1/$SLURM_JOB_ID/lib/$unzipedPTarFile_Dir
tar xvf /dev/shm/dd/$1/$SLURM_JOB_ID/lib/$unzipedPTarFile_Dir/${tarFileName}.tar.gz ${tarFileName}/${filename}.pdbqt 

cd /dev/shm/dd/$1/$SLURM_JOB_ID

newname=${filename}

/public/software/.local/easybuild/software/virtualflow/vfvs/tools/bin/qvina02 --cpu 2 --config /home/cloudam/test/4UG2/4UG2.conf --ligand /dev/shm/dd/$1/$SLURM_JOB_ID/lib/$unzipedPTarFile_Dir/${tarFileName}/${newname}.pdbqt --out ./out/${newname}.out --log ./out/${newname}.log


scoring=`cat ./out/${newname}.log | grep " 1 " |awk '{print $2}'`
echo "$scoring,${newname}" >> ./out/$INPUT.csv


done

cd ./out

tar -cvf $1.tar.gz  *
mv $1.tar.gz $CURDIR/

cat ./$INPUT.csv >> $2
