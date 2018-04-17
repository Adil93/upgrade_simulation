#!/bin/bash

function usage
{
    echo "usage: ./RemoveSOA [archivefile]"
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
zip -d "$1" "SOA/*"

if [ "$?" -eq 0 ]; then
   echo "Sucessfully deleted SOA directory form the archive: $1."
else 
   echo "Failed to delete SOA directory from the archive: $1."
fi

unzip -l "$1"
unzip -p "$1" CSCheckSum.properties > CSCheckSum.properties
if [ -s CSCheckSum.properties ]; then
   sed -i 's/\<SOA\>\,//g' CSCheckSum.properties
   sed -i '/^SOA.*/d' CSCheckSum.properties
   zip -g "$1" CSCheckSum.properties
fi
rm -f CSCheckSum.properties

exit 0

