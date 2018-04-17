import sys
import os

def print_help():
    print("The command to run the script is : \n <wlst path : /u01/APPLTOP/fusionapps/atgpf/common/bin/wlst.sh > <path to essSubmitRequest.py> <weblogic user : FUSION_APPS_CRM_SOA_APPID> <FUSION_APPS_CRM_SOA_APPID passwd> <weblogic url>")

if len(sys.argv) == 4:
    w_user = sys.argv[1]
    w_pass = sys.argv[2]
    w_url = sys.argv[3]
    try:
        connect(w_user, w_pass, w_url)
        essSubmitRequest("CrmEss","/oracle/apps/ess/marketing/commonMarketing/mktImport/Job_Generation",reqParams= {'applicationName':'Extensibility'})

    except:
        traceback.print_exc(file=sys.stdout)

else:
    print_help()