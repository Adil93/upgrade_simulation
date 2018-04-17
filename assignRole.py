import sys
import time as systime
import traceback
import os

def print_help():
    print("The command to assign roles to users : \n <wlst path> <weblogic user> <weblogic passwd> <weblogic url> <user list> ")

if len(sys.argv) == 5:
    w_user = sys.argv[1]
    w_pass = sys.argv[2]
    w_url = sys.argv[3]
    user_list = sys.argv[4]
    
    currentTime = systime.strftime('%Y%m%d%H%M%S', systime.gmtime())
    try:
        user=user_list.split(',')
        connect(w_user, w_pass, w_url)
        for usr in user:
			grantAppRole(appStripe="crm", appRoleName="ORA_CRM_EXTN_ROLE", principalClass="weblogic.security.principal.WLSUserImpl", principalName=usr)	
        print("\n successfully assigned role ORA_CRM_EXTN_ROLE to the users!")
    except:
        traceback.print_exc(file=sys.stdout)
else:
    print_help()
