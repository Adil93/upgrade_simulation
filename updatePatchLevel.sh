#!/bin/sh
csm_location=$1
patch_level=""
# DIR=$(dirname "${csm_location}")
# if [ -d "$DIR/temp" ]; then
#     rm -r -f $DIR/temp
# fi
# mkdir $DIR/temp
# fname=$(basename $csm_location)
# unzip $csm_location -d $DIR/temp
# rm $DIR/$fname
# file_location=$DIR/temp/CSCheckSum.properties
# sed -i "/patchLevel/c $patch_level" $file_location
# cd $DIR/temp/ && zip -r $fname *
# mv $DIR/temp/*.jar $DIR/
# rm -r -f $DIR/temp


#!/bin/bash

function usage
{
    echo "usage: ./updatePAtchLevel.sh [archivefile]"
    echo "  [archivefile]     input CSM archive/jar file including its full path"
    echo "Example:      ./RemoveSOA /tmp/csm/CS_DEV2_0421_V1_5547943012639744.jar"
    exit 1
}

if [ "$#" -ne 1 ]; then
   usage
fi
if [ ! -f "$1" ]; then
   echo "$1. Invalid file name or path."
   exit 1
fi
cp "$1" "$1.old"
chmod +w "$1"

unzip -p "$1" CSCheckSum.properties > CSCheckSum.properties
if [ -s CSCheckSum.properties ]; then
   sed -i "/patchLevel/c $patch_level" CSCheckSum.properties
   zip -g "$1" CSCheckSum.properties
fi
rm -f CSCheckSum.properties

exit 0
