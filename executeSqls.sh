#!/bin/bash

export ORACLE_SID=$4
export ORACLE_HOME=/u01/app/oracle/product/12.1.0
sqlSCriptLocation=$1
DBUSER='fusion'
DBUSERPASSWORD='welcome1'
DB=$2:$3/$4

for entry in "$sqlSCriptLocation"/*
do
  echo "Executing $entry"
  ~/product/12.1.0/bin/sqlplus -S $DBUSER/$DBUSERPASSWORD @$entry
done

exit 0