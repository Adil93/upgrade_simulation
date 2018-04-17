#!/bin/bash

csm_patch=$1
mds_path=$2
mds_dump_name=$3
DIR=$(dirname "${csm_patch}")

mkdir $DIR/temp
unzip $csm_patch -d $DIR/temp
echo "unzipping  $DIR/temp/ADF/CS_ADF_*.jar"
unzip $DIR/temp/ADF/CS_ADF_*.jar -d $DIR/temp/ADF_temp


mv $DIR/temp/ADF_temp/CS_ADF_MDS*.jar $DIR/temp/ADF_temp/$mds_dump_name.zip
cp -r $DIR/temp/ADF_temp/$mds_dump_name.zip $mds_path
rm -r $DIR/temp