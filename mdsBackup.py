import sys
import time as systime
import traceback
import os

def print_help():
    print("The command to run the script is : \n <wlst path> <path to mdsBackup.py> <weblogic user> <weblogic passwd> <weblogic url> <export mds path> <mds suffix name>")

if len(sys.argv) == 6:
    w_user = sys.argv[1]
    w_pass = sys.argv[2]
    w_url = sys.argv[3]
    mds_path = sys.argv[4]
    mds_prefix = sys.argv[5]

    currentTime = systime.strftime('%Y%m%d%H%M%S', systime.gmtime())
    try:
        mds_prefix = mds_prefix+"_"+str(currentTime)
        connect(w_user, w_pass, w_url)
        if os.path.exists(mds_path):
            print(mds_path+" Directory already exists")
            print("\n\nExporting MDS to" + mds_path)
        else:
            os.makedirs(mds_path)
            print(mds_path + " does not exist")
            print("\nCreated Directory "+mds_path)
        mds_file_name = "MDS_Dump_"+ mds_prefix + ".zip"
        exportMetadata(application='ORA_CRM_UIAPP',server='UIServer_1',toLocation=mds_path+"/"+mds_file_name,docs='/**')
        if os.stat(os.path.join(mds_path,mds_file_name)).st_size == 0 :
            print("\n Export failed")
            exit(1)
        print("\nMDS successfully exported to the path : "+mds_path + "\nName : "+mds_file_name)
        createMetadataLabel('ORA_CRM_UIAPP','UIServer_1',"MDS_"+mds_prefix)
        print("\nNew label created mds_prefix : MDS_"+mds_prefix)
    except:
        traceback.print_exc(file=sys.stdout)
else:
    print_help()
