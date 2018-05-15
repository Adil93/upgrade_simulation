import os,glob,traceback
import sys
import os.path
from os import listdir
import logging
import subprocess
from datetime import datetime



def print_help():
    print("The command to run the script is : \n python csmImportWrapper.py <mode : (post/pre)> <rootPath> <weblogic user> <weblogic password>")
    print("\nThe command to run the script for resuming from a point for post import is : \n python csmImportWrapper.py post <rootPath> <weblogic user> <weblogic password> resume <Resume point>")
    print("\nThe command to execute a specific task : \n python csmImportWrapper.py <mode : (post/pre)> <rootPath> <weblogic user> <weblogic password> execute <executionPoint>")
    print("\nPossible Resume_Point/Execution_Point values : \"executeADFMbean\" , \"executeCRMMbean\" , \"takeMdsBackup postUpgrade\" , \"executeSqls\" , \"executeATKMigration\" ,\"executeApplyDefferedTask\", \"takeMdsBackup preMDSScript\",\"executeMDSScripts\",\"takeMdsBackup postMDSScript\", \"essSubmitRequest\"")
    print("NOTE : Resume_Point/Execution_Point values should be given in double quotes itself")

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

def validateConfigProperties(configMap):
    for key, value in configMap.iteritems():
        if value == None or value == "":
            print("The value of key "+key+" cannot be empty in the config.properties")
            logger.info("The value of key "+key+" cannot be empty in the config.properties")
            exit(0)
        else:
            pass

def getExecutionStatus(logFilePath,logType):
    logfile = open(logFilePath,'r')
    completeStatus = "FAILED"
    
    if logType == "adfMbean":
        for lines in logfile:
            if 'completed ok' in lines:
                completeStatus = "SUCCESS"
                break
    elif logType == "crmMbean": 
        for lines in logfile:
            if 'Upgrading custom metadata for application' in lines:
                completeStatus = "SUCCESS"
                break
    elif logType == "sql":
        for lines in logfile:
            if 'procedure successfully completed' in lines or 'Commit complete' in lines:
                completeStatus = "SUCCESS"

    elif logType == "atkMigration":
        for lines in logfile:
            if 'ALL: Migration completed successfully' in lines:
                completeStatus = "SUCCESS"
                break
    elif logType == "roleCreation":
        for lines in logfile:
            if 'SUCCESS' in lines:
                completeStatus= "SUCCESS"
                break
    elif logType == "ess":
        for lines in logfile:
             if 'Successfully submitted job request' in lines:
                completeStatus= "SUCCESS"
                break

    print(completeStatus)        
    return completeStatus

def executeADFMbean():
    if (os.path.isfile(adfupgradescript)):
            os.system("chmod u+x "+ adfupgradescript)
            print("\nExecuting ADF Mbean :")
            logger.info("Executing ADF Mbean :")
            adfMbeanCosole = os.path.join(mbeanLogPath,"adfMbeanCosole.out")
            print("\n"+wlstPath+" "+adfupgradescript+" "+w_user+" "+"****"+" "+weblogic_url+" oracle.apps.fnd.applcore.customization.SiteCC > "+adfMbeanCosole)
            logger.info(wlstPath+" "+adfupgradescript+" "+w_user+" "+"****"+" "+weblogic_url+" oracle.apps.fnd.applcore.customization.SiteCC > "+adfMbeanCosole)
            os.system(wlstPath+" "+adfupgradescript+" "+w_user+" "+w_pass+" "+weblogic_url+" oracle.apps.fnd.applcore.customization.SiteCC > "+ adfMbeanCosole )
            adfMbeanstatus = getExecutionStatus(adfMbeanCosole,"adfMbean")
            print("\n See the log "+str(adfMbeanCosole)+" for more details")
            logger.info("See the log "+str(adfMbeanCosole)+" for more details")
            if adfMbeanstatus == "SUCCESS" :
                print("ADF Mbean Executed Successfully.")
                logger.info("ADF Mbean Executed Successfully.")
            else:
                print("ADF Mbean Execution failed")
                logger.info("ADF Mbean Execution failed")
                exit(1)                    
    else:
            print("\nExecutable file not found : " + adfupgradescript)
            logger.info("Executable file not found : " + adfupgradescript)
            exit(1)

def executeCRMMbean():
    if (os.path.isfile(crmMbeantemplate)):
            os.system("chmod u+x "+ crmMbeantemplate)
            print("\nExecuting CRM Mbean :")
            logger.info("Executing CRM Mbean :")
            crmMbeanCosole = os.path.join(mbeanLogPath,"crmMbeanCosole.out")
            # os.system("sed -i 's#\[%3\]#"+weblogic_url+"#g' "+crmMbeantemplate)
            print("\n"+wlstPath+" "+crmMbeantemplate+" "+w_user+" "+"****"+" "+weblogic_url+ " > " +crmMbeanCosole)
            logger.info(wlstPath+" "+crmMbeantemplate+" "+w_user+" "+"****"+" "+weblogic_url+ " > " +crmMbeanCosole)
            os.system(wlstPath+" "+crmMbeantemplate+" "+w_user+" "+w_pass+" "+weblogic_url+ " > " +crmMbeanCosole)

            # os.system("sed -i 's#"+weblogic_url+"#\[%3\]#g' "+crmMbeantemplate)
            crmMbeanstatus = getExecutionStatus(crmMbeanCosole,"crmMbean")

            print("\n See the log "+str(crmMbeanCosole)+" for more details")
            logger.info("See the log "+str(crmMbeanCosole)+" for more details")
            if crmMbeanstatus == "SUCCESS" :
                print("CRM Mbean Executed Successfully")
                logger.info("CRM Mbean Executed Successfully")
            else:
                print("CRM Mbean Execution failed")
                logger.info("CRM Mbean Execution failed")
                exit(1)                  
    else:
            print("\nExecutable file not found : " + crmMbeantemplate)
            logger.info("Executable file not found : " + crmMbeantemplate)
            exit(1)

def takeMdsBackup(mds_prefix):
    print("\nTaking "+ mds_prefix+" MDS back up : ")
    logger.info("Taking "+ mds_prefix+" MDS back up : ")
    print("\n"+wlstPath+" "+rootPath+"/scripts/mdsBackup.py "+w_user+" "+"****"+" "+weblogic_url+" "+mds_path+" "+mds_prefix)
    logger.info(wlstPath+" "+rootPath+"/scripts/mdsBackup.py "+w_user+" "+"****"+" "+weblogic_url+" "+mds_path+" "+mds_prefix)
    os.system(wlstPath+" "+rootPath+"/scripts/mdsBackup.py "+w_user+" "+w_pass+" "+weblogic_url+" "+mds_path+" "+mds_prefix)
    filePresent=None
    for f in os.listdir(mds_path):
        if(f.startswith("MDS_Dump_"+mds_prefix)):
            filePresent=True
    if filePresent:    
        print("MDS backup Succeeded")
    else:
        print("MDS backup failed")
        exit(1)
    
def executeSqls():
    print("\nExecuting sqls "+ mode +" import :")
    logger.info("Executing sqls "+ mode +" import :")
    os.system("ssh -o \"StrictHostKeyChecking no\" "+db_host+" "+"\"mkdir -p " + sqlScriptsLocInDbHost+"\"")
    if disableBI.lower() == "false" and mode=="pre":
        os.system("rsync -avz --exclude 'disableBI.sql' "+"sqls/"+mode+"Import/* "+db_host+":"+sqlScriptsLocInDbHost)
    else:
        os.system("rsync -avz "+"sqls/"+mode+"Import/* "+db_host+":"+sqlScriptsLocInDbHost)

    os.system("ssh -o \"StrictHostKeyChecking no\" "+db_host+" \"bash -s\" < ./executeSqls.sh "+sqlScriptsLocInDbHost+" "+db_host+" "+db_port+" "+oracle_sid+" "+oracle_home+" >> ../logs/"+mode+"_sql.log")
    sqlStatus = getExecutionStatus("../logs/"+mode+"_sql.log","sql")
    print("\n See the log "+"../logs/"+mode+"_sql.log"+" for more details")
    logger.info("See the log "+"../logs/"+mode+"_sql.log"+" for more details")
    if sqlStatus == "SUCCESS":
        print("\nSqls Executed successfully")
        logger.info("Sqls Executed successfully")
    else:
        print("\nSql execution failed")
        logger.info("Sql execution failed")
        exit(1)

def executeATKMigration():
    if os.path.isfile(atk_migration_script):  
        print("\nExecuting ATK Migration script ")
        logger.info("Executing ATK Migration script ")
        with open('pwd.txt','w') as f:
                f.write(fusion_mds_pass)

        print("\n"+atk_migration_script+" "+database_connect_string+" fusion_mds "+"/u01/APPLTOP"+" "+atk_migration_log+" "+JAVA_HOME+" < pwd.txt")
        logger.info(atk_migration_script+" "+database_connect_string+" fusion_mds "+"/u01/APPLTOP"+" "+atk_migration_log+" "+JAVA_HOME+" < pwd.txt")
        os.system(atk_migration_script+" "+database_connect_string+" fusion_mds "+"/u01/APPLTOP"+" "+atk_migration_log+" "+JAVA_HOME+" < pwd.txt")
        #need to check
        atkLogFile = [filename for filename in os.listdir(atk_migration_log) if filename.startswith("AtkMigration")][0]
        if atkLogFile == "":
             atkMigrationsStatus="FAILED"
             print("ATK Migration execution failed")
             logger.info("ATK Migration execution failed")    
             exit(1)
        
        atkLogFile=os.path.join(atk_migration_log,atkLogFile)
        atkMigrationsStatus = getExecutionStatus(atkLogFile,"atkMigration")
        print("\n See the log "+str(atkLogFile)+" for more details")
        logger.info("See the log "+str(atkLogFile)+" for more details")
        if atkMigrationsStatus == "SUCCESS":
            print("ATK Migration executed successfully")
            logger.info("ATK Migration executed successfully")
            # os.system("rm /u01/APPLTOP/pwd.txt")
        else:
            print("ATK Migration execution failed")
            logger.info("ATK Migration execution failed")    
            exit(1)
    else:
        print("\nExecutable file not found : " + atk_migration_script)
        logger.info("Executable file not found : " + atk_migration_script)
        exit(1)     

def executeMDSScripts(*args):
    serverName="UIServer_1"
    application="ORA_CRM_UIAPP"
    release="latest"
    exportMDS="afternonaru"
    mdsLogPath=os.path.join(logPath,"mdsScriptLogs")
    upgradeWrapperFile=os.path.join(mdsScriptPath,"upgradeWrapper.py")
    if not os.path.isdir(mdsLogPath):
        os.makedirs(mdsLogPath)
    print("Executing MDS scripts\n")
    if os.path.isfile(upgradeWrapperFile):
        if args:
            executable_file=os.path.join(mdsScriptPath,"latest/"+args[0])
            if os.path.isfile(executable_file):
                print("python "+upgradeWrapperFile+" "+wlstPath+" "+mdsScriptPath+" "+w_host+" "+w_port+" "+w_user+" "+"****"+" "+serverName+" "+application+" "+release+" exportMDS="+exportMDS +" "+executable_file+">"+mdsLogPath+"/mdsScripts.log")
                logger.info("python "+upgradeWrapperFile+" "+wlstPath+" "+mdsScriptPath+" "+w_host+" "+w_port+" "+w_user+" "+"****"+" "+serverName+" "+application+" "+release+" exportMDS="+exportMDS +" "+executable_file+">"+mdsLogPath+"/mdsScripts.log")
                os.system("python "+upgradeWrapperFile+" "+wlstPath+" "+mdsScriptPath+" "+w_host+" "+w_port+" "+w_user+" "+w_pass+" "+serverName+" "+application+" "+release+" exportMDS="+exportMDS +" "+executable_file+">"+mdsLogPath+"/mdsScripts.log")
            else:
                print(executable_file +"not found")
                logPath.info(executable_file +"not found")
        else:
            print("python "+upgradeWrapperFile+" "+wlstPath+" "+mdsScriptPath+" "+w_host+" "+w_port+" "+w_user+" "+"****"+" "+serverName+" "+application+" "+release+" exportMDS="+exportMDS +">"+mdsLogPath+"/mdsScripts.log")
            logger.info("python "+upgradeWrapperFile+" "+wlstPath+" "+mdsScriptPath+" "+w_host+" "+w_port+" "+w_user+" "+"****"+" "+serverName+" "+application+" "+release+" exportMDS="+exportMDS +">"+mdsLogPath+"/mdsScripts.log")
            os.system("python "+upgradeWrapperFile+" "+wlstPath+" "+mdsScriptPath+" "+w_host+" "+w_port+" "+w_user+" "+w_pass+" "+serverName+" "+application+" "+release+" exportMDS="+exportMDS +">"+mdsLogPath+"/mdsScripts.log")
    else:
        print(upgradeWrapperFile + " not found")
        logger.info(upgradeWrapperFile + " not found")
        exit(1)

def essSubmitRequest():
    print("\nSubmitting ESS request")
    print("\n"+"/u01/APPLTOP/fusionapps/atgpf/common/bin/wlst.sh"+" "+rootPath+"/scripts/essSubmitRequest.py"+" "+"FUSION_APPS_CRM_SOA_APPID"+" "+"\""+FUSION_APPS_CRM_SOA_APPID_pass+"\""+" "+ess_weblogic_url)
    logger.info("/u01/APPLTOP/fusionapps/atgpf/common/bin/wlst.sh"+" "+rootPath+"/scripts/essSubmitRequest.py"+" "+"FUSION_APPS_CRM_SOA_APPID"+" "+"\""+FUSION_APPS_CRM_SOA_APPID_pass+"\""+" "+ess_weblogic_url)
    os.system("/u01/APPLTOP/fusionapps/atgpf/common/bin/wlst.sh"+" "+rootPath+"/scripts/essSubmitRequest.py"+" "+"FUSION_APPS_CRM_SOA_APPID"+" "+"\""+FUSION_APPS_CRM_SOA_APPID_pass+"\""+" "+ess_weblogic_url+" > "+logPath+"/essRequest.out")
    submissionStatus=getExecutionStatus(logPath+"/essRequest.out","ess")
    if submissionStatus == "SUCCESS":
        print("\nEss Submitted Successfully")    
        logger.info("Ess Submitted Successfully\n")
    else:
        print("ESS Submission failed , Please check "+logPath+"/essRequest.out")
        exit(1)

def executeApplyDefferedTask():
    if os.path.isfile("/u01/APPLTOP/fusionapps/applications/lcm/ad/bin/applydeferredtasks.sh"):
        os.system("/u01/APPLTOP/fusionapps/applications/lcm/ad/bin/applydeferredtasks.sh")
        print("Executed ApplyDefferedTask.sh")
        logger.info("Executed ApplyDefferedTask.sh")
    else:
        print("File /u01/APPLTOP/fusionapps/applications/lcm/ad/bin/applydeferredtasks.sh does not exists : ignoring the step")
        logger.info("File /u01/APPLTOP/fusionapps/applications/lcm/ad/bin/applydeferredtasks.sh does not exists : ignoring the step")

def updatePatchLevel():
    subprocess.call(['./updatePatchLevel.sh',str(csm_path)])
    logger.info("Updated Patch level to "+patchLevel)

def removeSOA():
    subprocess.call(['./removeSOA.sh',str(csm_path)])
    logger.info("Removed SOA from the CSM archive")

def preUpgradeMdsBackup():
	# subprocess.call(['preimportMdsDump.sh',str(csm_path),str(mds_path)])
    if os.path.isfile(str(csm_path)):
        print("Taking the PreImportMds Back up")
        print("./preimportMdsDump.sh"+" "+str(csm_path)+" "+str(mds_path)+" "+"preImportMdsDump")
        os.system("./preimportMdsDump.sh"+" "+str(csm_path)+" "+str(mds_path)+" "+" preImportMdsDump")
        if(os.path.isfile(mds_path+"/preImportMdsDump.zip")):
            print("Took the back up in "+mds_path)
            logger.info("Took the back up in "+mds_path)
        else:
            logger.info("Pre Upgrade MDS Backup creation failed")
            print("Pre Upgrade MDS Backup creation failed")
            exit(1)
    else:
        logger.info("Please specify correct path of the CSM jar in the config.properties")
        print("\nPlease specify correct path of the CSM jar in the config.properties")
        exit(1)
def createCustomRolesInCSM(csm_path):
    fa_host_name=w_host[0:w_host.find('.')]
    print("Creating Missing duty roles")
    logger.info("Creating Missing duty roles")
    os.system(JAVA_HOME+"/bin/java -jar customRole/CSMRoleExtractor.jar "+ csm_path+" customRole/customRole.temp")
    os.system("sed -i '0,/changeme/{s/changeme/"+w_user+"/}' "+"customRole/customRole.temp")
    os.system("sed -i '0,/changeme/{s/changeme/"+w_pass+"/}' "+"customRole/customRole.temp")
    os.system("sed -i '0,/changeme/{s/changeme/"+fa_host_name+"/}' "+"customRole/customRole.temp")
    os.system("sed -i '0,/adminport#/{s/adminport#/"+"11401"+"/}' "+"customRole/customRole.temp")
    print(wlstPath +" "+ "customRole/customRole.temp "+"> "+"customRole/roleCreation.out")
    logger.info(wlstPath +" "+ "customRole/customRole.temp "+"> "+"customRole/roleCreation.out")
    os.system(wlstPath +" "+ "customRole/customRole.temp" +"> "+"customRole/roleCreation.out")
    roleCreationStatus=getExecutionStatus("customRole/roleCreation.out","roleCreation")
    if roleCreationStatus =="SUCCESS":
        print("Successfully Created Missing roles")
    else:
        print("Required jars not pathed in env , should create missing roles via UI")
    
def assignORA_CRM_EXTN_ROLE():
    #Create the role first and then assign it to the users
    #call the python script for granting the role
    print("Custom role created")
    os.system(wlstPath+" "+rootPath+"/scripts/assignRole.py "+w_user+" "+w_pass+" "+weblogic_url+" "+users)

#Function to import the CSM File:
def importCSM(w_host,csmName,csm_path,username,password):
    encoded = base64.b64encode(username + ':' + password)
    print("Encoded", encoded)
    print(type(encoded))

    print(w_host)
    print(csmName)
    print("csm path", csm_path)
    url = "https://" + w_host + "/fscmUI/applcorerestservice/actions/importcustomization"
    print(url)

    payload1 = '{\"name\":\"importcustomization\",\"resources\":[{\"name\":'
    payload2 = '"' + csmName + '"'
    payload3 = ',\"type\":\"JAR\",\"location\":'
    payload4 = '"' + csm_path + '"'
    payload5 = '}],\"actionRequestProperties\":[{\"key\":\"FileLocation\",\"value\":'
    payload6 = '"' + csm_path + '"'
    payload7 = '}],\"provisioningProperties\":[{\"key\":\"dummy\",\"value\":\"dummy\"}]}'

    payload = payload1 + payload2 + payload3 + payload4 + payload5 + payload6 + payload7

    print(payload)

    headers = {
        'content-type': "application/json",
        # 'authorization': "Basic YXBwbGljYXRpb25faW1wbGVtZW50YXRpb25fY29uc3VsdGFudDpXZWxjb21lMQ==",
        'authorization': "Basic " + str(encoded),
        'cache-control': "no-cache",
        'postman-token': "911c6518-6416-d416-e5f9-6c5ed519187b"
    }
    print("HEADER: ", headers)
    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

#Logging framwork
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
if not os.path.isdir('../logs'):
    os.makedirs('../logs')
handler = logging.FileHandler('../logs/console_out.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

if len(sys.argv) == 5 or len(sys.argv) == 7:
    mode = sys.argv[1].lower()
    rootPath = sys.argv[2]
    w_user = sys.argv[3]
    w_pass = sys.argv[4]
    
    #optional
    resumePoint = None
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
    csm_path = configMap["csm_path"]
    patchLevel = configMap["patchLevel"]
    oracle_sid = configMap["oracle_sid"]
    removeSoa = configMap["removeSOA"]
    disableBI = configMap["disableBI"]
    execMDSScripts=configMap["executeMDSScripts"]
    users=configMap["users"]
    createCustomRole=configMap["createCustomRole"]
    essSoaServerPort=configMap["ess_soa_server_port"]
    oracle_home=configMap["oracle_home"]

    #CSM Import Variables Start
    csm_path = configMap["csm_path"]
    username = configMap["username"]
    password = configMap["password"]
    csmName = os.path.basename(csm_path)
    #CSM Import Variables End
    
    #Ensure required values are filled up in config.properties file
    validateConfigProperties(configMap)

    logPath = os.path.join(rootPath,'logs')
    if not os.path.isdir(logPath):
        os.makedirs(logPath)
    mds_path = os.path.join(rootPath,'mds_dumps')
    if not os.path.isdir(mds_path):
        os.makedirs(mds_path)
    adf_crm_mbean_scriptpath = os.path.join(rootPath,'ADFandCRMMbean')
    atk_migration_log = os.path.join(rootPath,'ATK_Migration_log')
    if not os.path.isdir(atk_migration_log):
        os.makedirs(atk_migration_log)
    mbeanLogPath = os.path.join(adf_crm_mbean_scriptpath,'logs')
    if not os.path.isdir(mbeanLogPath):
        os.makedirs(mbeanLogPath)
    if not os.path.isdir(JAVA_HOME):
        JAVA_HOME=os.environ["JAVA_HOME"]

    weblogic_url= "t3://"+w_host+":"+w_port
    ess_weblogic_url = "t3://"+w_host+":"+essSoaServerPort
    database_connect_string = "jdbc:oracle:thin:@"+db_host+":"+db_port+"/"+oracle_sid

    adfupgradescript=os.path.join(adf_crm_mbean_scriptpath,"adfupgradescript.py")
    crmMbeantemplate=os.path.join(adf_crm_mbean_scriptpath,"wlstUpgradeCustomMetadata.template")
    mdsScriptPath=os.path.join(rootPath,"scripts/mdsScripts")
    sqlScriptsLocInDbHost="~/temp_sqls/"+mode+"sqls"

    #check mode given is valid or not
    if mode not in ["post","pre"]:
        print("invalid mode specified")
        print_help
        exit(0)
    
    # check whether root path given exists or not
    if os.path.isdir(rootPath):
        print("\nRoot Working Dir: "+rootPath)
    else:
        print("Invalid Root Path specified")
        exit(0)

    #need to check whether credentials are right or not

    #Authentication validation to be done

    try:
        # Execution begins
        print "Execution of "+mode+" Import Begins\n"
        logger.info("Execution of "+mode+" Import Begins\n")
        logger.info("log file location : "+rootPath+"/logs/console_out.log")

        #Pre Import 
        if mode == "pre":
            if(len(sys.argv) == 5):
                # Take the Pre Upgrade MDS backup from the CSM archive
                preUpgradeMdsBackup()
                
                # Update the patchLevel
                updatePatchLevel()

                # Remove SOA references from the csm
                if removeSoa.lower() == "true":
                    removeSOA()                

                #Create the roles in the CSM into target

                #Executing Pre Import sqls : Disblin BI , Removing HRT_POTENTAIL_MEMBER reference from database
                # if disable BI is false should remove the corresponding sql
                executeSqls()
                if createCustomRole=="true":
                    createCustomRolesInCSM(csm_path)
                else:
                    print("NEED TO MANUALLY CREATE ROLES via UI")
                
                print("\nPre Import Succeeded. Continue with Importing CSM jar via UI")
            else:
                #need to add in readme there is no resume point for pre import
                print("\nNo Resume Point Argument expected for Pre import\n")
                print_help()
                exit(0)
        # CSM import 


        # succes : .....
        #Post Import
        if mode == "post":            
            try:
                executionList = ["executeADFMbean","executeCRMMbean","takeMdsBackup postUpgrade","executeSqls","executeATKMigration","executeApplyDefferedTask","takeMdsBackup preMDScript","executeMDSScripts","takeMdsBackup postMDSScript","assignORA_CRM_EXTN_ROLE","essSubmitRequest"]
                if execMDSScripts.lower() == "false":
                    executionList.remove("executeMDSScripts")
                    executionList.remove("takeMdsBackup postMDSScript")
                    print("Make the value of executeMDSScripts to true in config.properties and copy neccessary MDS scripts to "+mdsScriptPath+" corresponding to the branch and execute again to execute MDS scripts , other wise please continue")
                #Resuming from a particualr point in post import
                if(len(sys.argv) == 7 ):
                    execution_type = sys.argv[5]
                    resumePoint=sys.argv[6]
                    if execution_type == "resume":
                        if resumePoint is not None and resumePoint in executionList:
                            start = executionList.index(resumePoint)
                        else:
                            print_help()
                            exit(1)
                        logger.info("Resuming from "+resumePoint+"\n")
                        for i in range(start,len(executionList)):
                            if " " in executionList[i]:
                                arguments=executionList[i].split()
                                eval(arguments[0]+"("+"\""+arguments[1]+"\""+")")
                            else:
                                eval(executionList[i]+"()")
                    elif execution_type == "execute":
                        if " " in resumePoint:
                            arguments=resumePoint.split()
                            eval(arguments[0]+"("+"\""+arguments[1]+"\""+")")
                        else:
                            eval(resumePoint+"()")
                    else:
                        print("Invalid Execution type , Possible values : \"resume\",\"execute\"")
                
                #Normal flow of Execution starts from here for post import           
                if(len(sys.argv) == 5):
                    executeADFMbean()
                    executeCRMMbean()
                    takeMdsBackup("postUpgrade")
                    executeSqls()
                    executeATKMigration()
                    executeApplyDefferedTask()
                    takeMdsBackup("preMDSScript")
                    if execMDSScripts.lower() == "true":
                        executeMDSScripts()
                        takeMdsBackup("postMDSScript")
                    #Assign the Customobject role to the users listed in the config.properties
                    assignORA_CRM_EXTN_ROLE()
                    essSubmitRequest()
                print("\nPost Import Succeeded.")
                logger.info("Post Import Succeeded.")         
            except:
                traceback.print_exc(file=sys.stdout)


            print("Time taken for execution : "+str(datetime.now() - startTime))
    except:
        traceback.print_exc(file=sys.stdout)

else:
    print_help() 