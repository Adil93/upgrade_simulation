import os,glob,traceback
import sys
import os.path
from os import listdir
import logging
from datetime import datetime
def print_help():
	print("The command to run the script is : \n python postCsmImport.py <rootPath> <weblogic user> <weblogic password>")
	print("\nThe command to run the script for resuming from a point is : \n python postCsmImport.py <rootPath> <weblogic user> <weblogic password> <mode Resume> <Resume point>")
	print("\nPossible Resume Point values : \"executeADFMbean\" , \"executeCRMMbean\" , \"takeMdsBackup postUpgrade\" , \"executeSqls\" , \"executeATKMigration\" , \"takeMdsBackup preNonAru\"")
	print("NOTE : Resume point values should be given in double quotes itself")

def readPropertyFile(propertyFile):
    propFile= file(propertyFile, "rU" )
    configMap= dict()
    for propLine in propFile:
        propDef= propLine.strip()
        if len(propDef) == 0:
            continue
        if propDef[0] in ( '!', '#' ):
            continue
        punctuation= [ propDef.find(c) for c in ':= ' ] + [ len(propDef) ]
        found= min( [ pos for pos in punctuation if pos != -1 ] )
        name= propDef[:found].rstrip()
        value= propDef[found:].lstrip(":= ").rstrip()
        configMap[name]= value
    propFile.close()
    return configMap

def getExecutionStatus(logFilePath,logType):
    logfile = open(logFilePath,'r')
    completeStatus = "FAILED"
    
    if logType == "adfMbean":
        for lines in logfile:
            if 'ERROR' in lines or 'Failed' in lines:
                completeStatus = "FAILED"
                break
            if 'completed ok' in lines:
                completeStatus = "SUCCESS"
                break
    elif logType == "crmMbean" or logType == "sql": 
        completeStatus = "SUCCESS" 
        for lines in logfile:
            if 'ERROR' in lines or 'Failed' in lines:
                completeStatus = "FAILED"
                break  
    elif logType == "atkMigration":
        for lines in logfile:
            if 'ERROR' in lines or 'Failed' in lines:
                completeStatus = "FAILED"
                break
            if 'ALL: Migration completed successfully' in lines:
                completeStatus = "SUCCESS"
                break

    print(completeStatus)        
    return completeStatus

def executeADFMbean():
    if (os.path.isfile(adfupgradescript)):
            os.system("chmod u+x "+ adfupgradescript)
            print("\nExecuting ADF Mbean :")
            print("\n"+wlstPath+" "+adfupgradescript+" "+w_user+" "+w_pass+" "+weblogic_url+" oracle.apps.fnd.applcore.customization.SiteCC > "+adfMbeanCosole)
            adfMbeanCosole = os.path.join(mbeanLogPath,"adfMbeanCosole.out")
            os.system(wlstPath+" "+adfupgradescript+" "+w_user+" "+w_pass+" "+weblogic_url+" oracle.apps.fnd.applcore.customization.SiteCC > "+ adfMbeanCosole )
            adfMbeanstatus = getExecutionStatus(adfMbeanCosole,"adfMbean")
            if adfMbeanstatus == "SUCCESS" :
                print("ADF Mbean Executed Successfully")
            else:
                print("ADF Mbean Execution failed")
                exit(1)                    
    else:
            print("\nExecutable file not found : " + adfupgradescript)
            exit(1)

def executeCRMMbean():
    if (os.path.isfile(crmMbeantemplate)):
            os.system("chmod u+x "+ crmMbeantemplate)
            print("\nExecuting CRM Mbean :")
            print("\n"+wlstPath+" "+crmMbeantemplate+" "+w_user+" "+w_pass+" "+weblogic_url+ " > " +crmMbeanCosole)
            crmMbeanCosole = os.path.join(mbeanLogPath,"crmMbeanCosole.out")
            os.system(wlstPath+" "+crmMbeantemplate+" "+w_user+" "+w_pass+" "+weblogic_url+ " > " +crmMbeanCosole )
            crmMbeanstatus = getExecutionStatus(crmMbeanCosole,"crmMbean")

            if crmMbeanstatus == "SUCCESS" :
                print("CRM Mbean Executed Successfully")
            else:
                print("CRM Mbean Execution failed")
                exit(1)                  
    else:
            print("\nExecutable file not found : " + crmMbeantemplate)
            exit(1) 

def takeMdsBackup(mds_prefix):
    print("\nTaking "+ mds_prefix+" MDS back up : ")
    print("\n"+wlstPath+" "+rootPath+"/scripts/mdsBackup.py "+w_user+" "+w_pass+" "+weblogic_url+" "+mds_path+" "+mds_prefix)
    os.system(wlstPath+" "+rootPath+"/scripts/mdsBackup.py "+w_user+" "+w_pass+" "+weblogic_url+" "+mds_path+" "+mds_prefix)

def executeSqls():
    print("\nExecuting sqls before NonARU :")
    os.system("scp -r sqls/* "+db_host+":"+sqlScriptsLocInDbHost)
    os.system("ssh "+db_host+" \"bash -s\" < ./executeSqls.sh "+sqlScriptsLocInDbHost+" >> ../logs/sql.log")
    sqlStatus = getExecutionStatus("../logs/sql.log","sql")
    if sqlStatus == "SUCCESS":
        print("\nSqls Executed successfully")
    else:
        print("\nSql execution failed")
        exit(1)

def executeATKMigration():
    if os.path.isfile(atk_migration_script):  
        print("\nExecuting ATK Migration script ")
        
        f= open(os.path.join(rootPath,"pwd.txt"),"w+")
        f.write(fusion_mds_pass)
        os.system("chmod 744 "+os.path.join(rootPath,"pwd.txt"))
    
        print("\n"+atk_migration_script+" "+database_connect_string+"  fusion_mds "+atk_migration_log+" < "+os.path.join(rootPath,"pwd.txt"))
        os.system(atk_migration_script+" "+database_connect_string+"  fusion_mds "+atk_migration_log+" < "+os.path.join(rootPath,"pwd.txt"))
        atkLogFile = [filename for filename in os.listdir('.') if filename.startswith("AtkMigration")][0]
        atkMigrationsStatus = getExecutionStatus(atkLogFile,"atkMigration")
        if atkMigrationsStatus == "SUCCESS":
            print("ATK Migration executed successfully")
            os.system("rm /u01/APPLTOP/pwd.txt")
        else:
            print("ATK Migration execution failed")    
            exit(1)
    else:
        print("\nExecutable file not found : " + atk_migration_script)
        exit(1)     

def essSubmitRequest():
    print("\nSubmitting ESS request")
    print("\n"+"/u01/APPLTOP/fusionapps/atgpf/common/bin/wlst.sh "+rootPath+"/scripts/essSubmitRequest.py"+" "+"FUSION_APPS_CRM_SOA_APPID"+" "+FUSION_APPS_CRM_SOA_APPID_pass+" "+weblogic_url)
    os.system("/u01/APPLTOP/fusionapps/atgpf/common/bin/wlst.sh "+rootPath+"/scripts/essSubmitRequest.py"+" "+"FUSION_APPS_CRM_SOA_APPID"+" "+FUSION_APPS_CRM_SOA_APPID_pass+" "+weblogic_url)
    print("\nSubmitted Successfully")

def executeApplyDefferedTask():
    if os.path.isfile("/u01/APPLTOP/fusionapps/applications/lcm/ad/bin/applydeferredtasks.sh"):
        os.system("/u01/APPLTOP/fusionapps/applications/lcm/ad/bin/applydeferredtasks.sh")
        print("Executed ApplyDefferedTask.sh")
    else:
        print("File /u01/APPLTOP/fusionapps/applications/lcm/ad/bin/applydeferredtasks.sh does not exists : ignoring the step")

if len(sys.argv) == 4 or len(sys.argv) == 6:
    rootPath = sys.argv[1]
    w_user = sys.argv[2]
    w_pass = sys.argv[3]
    mode = None
    resumePoint = None
    
    # if not os.path.exists(rootPath):
    #     print("Root Path : "+rootPath+" does not exist")
    #     exit(1)
    
    startTime = datetime.now()
    #Read configurations from property file
    configMap=readPropertyFile("../config.properties")
    
    #need to add null checks for each values taken from properties file and give a pop up like the value cannot be empty
    db_host = configMap["db_host"]
    db_port = configMap["db_port"]
    wlstPath = configMap["wlstPath"]
    w_host = configMap["fa_host"]
    w_port = configMap["fa_port"]
    atk_migration_script = configMap["atk_migration_script"]
    JAVA_HOME = configMap["JAVA_HOME"]
    fusion_mds_pass = configMap["fusion_mds_pass"]
    FUSION_APPS_CRM_SOA_APPID_pass = configMap["FUSION_APPS_CRM_SOA_APPID_pass"]
    oracle_sid = configMap["oracle_sid"]

    logPath = os.path.join(rootPath,'logs')
    mds_path = os.path.join(rootPath,'mds_dumps')
    adf_crm_mbean_scriptpath = os.path.join(rootPath,'ADFandCRMMbean')
    atk_migration_log = os.path.join(rootPath,'ATK_Migration_log')
    mbeanLogPath = os.path.join(adf_crm_mbean_scriptpath,'logs')

    weblogic_url= "t3://"+w_host+":"+w_port
    database_connect_string = "jdbc:oracle:thin:@"+db_host+":"+db_port+"/"+oracle_sid

    # The location in the db host to copy the sqls, So a change is required from post and pre as of now the generic sqls folder    
    sqlScriptsLocInDbHost="/u01/app/oracle/temp_sqls/sqls"

    # if "FUSION_APPS_CRM_SOA_APPID_passsd" not in configMap:
    #     print("hhh")

    adfupgradescript=os.path.join(adf_crm_mbean_scriptpath,"adfupgradescript.py")
    crmMbeantemplate=os.path.join(adf_crm_mbean_scriptpath,"wlstUpgradeCustomMetadata.template")
    print("\nRoot Working Dir: "+rootPath)

    #need to give checking in mode value , resume , execute and all 
    try:
        executionList = ["executeADFMbean","executeCRMMbean","takeMdsBackup postUpgrade","executeSqls","executeATKMigration","executeApplyDefferedTask","takeMdsBackup preNonAru"]
        start = 0
        if(len(sys.argv) == 6 ):
            mode = sys.argv[4]
            resumePoint = sys.argv[5]
            if resumePoint is not None and resumePoint in executionList:
                start = executionList.index(resumePoint)
            else:
                print("\nInvalid Resume point input")
                print("\nPossible Resume Point values : \"executeADFMbean\" , \"executeCRMMbean\" , \"takeMdsBackup postUpgrade\" , \"executeSqls\" , \"executeATKMigration\" , \"executeApplyDefferedTask\",  \"takeMdsBackup preNonAru\"")
                print("NOTE : Resume point values should be given in double quotes itself")
                exit(1)
            for i in range(start,len(executionList)):
                if " " in executionList[i]:
                    arguments=executionList[i].split()
                    eval(arguments[0]+"("+"\""+arguments[1]+"\""+")")
                else:
                    eval(executionList[i]+"()")
        
    
        # for count, executable in enumerate(executionList):
        #     if " " in executable:
        #         arguments=executable.split()

        if(len(sys.argv) == 4 ):
            executeADFMbean()
            executeCRMMbean()
            takeMdsBackup("postUpgrade")
            executeSqls()
            executeATKMigration()
            executeApplyDefferedTask()
            takeMdsBackup("preNonARU")
        
        print("Time taken for execution : "+str(datetime.now() - startTime))
    except:
        traceback.print_exc(file=sys.stdout)
else:
    print_help()   