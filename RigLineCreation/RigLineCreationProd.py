

##############################################################
## Created By: Ryan Nelson
## Date: 05/30/2017
## Department: GIS
## Purpose: To populate rig line data for future movements
##############################################################


import os
import sys
import datetime
import arcpy

#Set Current Working Directory
cwd = r'C:\GIS\RigLineCreation'

#Create Data Path
dataPath = cwd + r'\DATA'
if not os.path.isdir(dataPath):
    os.makedirs(dataPath)

#Create Log Path
logPath = cwd + r'\LOG'
if not os.path.isdir(logPath):
    os.makedirs(logPath)

#Define Log File Name
x = 1
dt = str(datetime.datetime.today().strftime('%Y%m%d'))
logFile = r'{0}\{1}_{2}.txt'.format(logPath,'{0}_LOG'.format(str(os.path.basename(__file__).split('.')[0])),dt)
while os.path.isfile(logFile):
    logFile = r'{0}\{1}_{2}_{3}.txt'.format(logPath,'{0}_LOG'.format(str(os.path.basename(__file__).split('.')[0])),dt,str(x))
    x+=1

#Start Log
msg = ''
log = open(logFile,'w')

#Filename
msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' File:     {0}\n'.format(str(os.path.basename(__file__)))
log.write(msg)
print msg

#User Executed
msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Executed: '+os.environ.get("USERNAME")+'\n'
log.write(msg)
print msg

#Datetime
msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Date:     '+str(datetime.datetime.today())+'\n\n'
log.write(msg)
print msg

#Set Exits
err = False
comp = False

#Begin Process
while err==False and comp==False:   
    try:

        #CreateFileGDB_management (out_folder_path, out_name, {out_version})
        x=1
        fgdb = r'{0}_{1}.gdb'.format('FGDB_Scratch',dt)
        while arcpy.Exists(dataPath + '\\' + fgdb):
            fgdb = r'{0}_{1}_{2}.gdb'.format('FGDB_Scratch',dt,str(x))
            x+=1
        arcpy.CreateFileGDB_management(dataPath,fgdb)
        fgdbPath = '{0}\{1}'.format(dataPath,fgdb)
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' CREATE:   FileGeodatabase {0}.\n'.format(fgdb)
        log.write(msg)
        print msg
        
        ## Create ParlseyStage Data Connection
        PEStageConnName = r'ParsleyStage.sde'
        PEStageConnPath = r'{0}\{1}'.format(dataPath,PEStageConnName)
        if not os.path.isfile(PEStageConnPath):
            ##CreateDatabaseConnection_management (out_folder_path, out_name, database_platform, instance, {account_authentication}, {username}, {password}, {save_user_pass}, {database}, {schema}, {version_type}, {version}, {date})
            arcpy.CreateDatabaseConnection_management(dataPath,PEStageConnName,'SQL_SERVER','cubeprd-01','OPERATING_SYSTEM_AUTH','#','#','DO_NOT_SAVE_USERNAME','ParsleyStage')
            msg =str(datetime.datetime.today().strftime('%H:%M:%S')) + ' CREATE:    Connection {0} created.\n'.format(PEStageConnPath)
            log.write(msg)
            print msg
        else:
            msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' EXIST:    Connection {0} exists.\n'.format(PEStageConnPath)
            log.write(msg)
            print msg

        ## Test for GIS pegisprod Data Connection
        GISpegisprod = r'GISpegisprod.sde'
        GISpegisprodPath = r'{0}\{1}'.format(dataPath,GISpegisprod)
        if not os.path.isfile(GISpegisprodPath):
            msg = '\n' + str(datetime.datetime.today().strftime('%H:%M:%S')) + ' ERROR:    Connection {0} not found.  Exiting process.\n'.format(GISpegisprodPath)
            log.write(msg)
            print msg
            err=True
        else:
            msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' EXIST:    Connection {0} exists.\n'.format(GISpegisprodPath)
            log.write(msg)
            print msg

        ## Test for STAGE pegisprod Data Connection
        STAGEpegisprod = r'STAGEpegisprod.sde'
        STAGEpegisprodPath = r'{0}\{1}'.format(dataPath,STAGEpegisprod)
        if not os.path.isfile(STAGEpegisprodPath):
            msg = '\n' + str(datetime.datetime.today().strftime('%H:%M:%S')) + ' ERROR:    Connection {0} not found.  Exiting process.\n'.format(STAGEpegisprodPath)
            log.write(msg)
            print msg
            err=True
        else:
            msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' EXIST:    Connection {0} exists.\n'.format(STAGEpegisprodPath)
            log.write(msg)
            print msg

        #Stage RigActivityPlans
        arcpy.env.workspace = STAGEpegisprodPath
        
        #Tables
        infc = 'ParsleyStage.Epex.RigActivityPlans'
        outfc ='pegisprod.STAGE.EPEX_RigActivityPlans'
        
        #Truncate
        #TruncateTable_management (in_table)
        arcpy.TruncateTable_management(outfc)
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' TRUNCATE:     {0}.\n'.format(outfc)
        log.write(msg)
        print msg
        
        #Append
        infc = 'ParsleyStage.Epex.RigActivityPlans'
        infcPath = '{0}\{1}'.format(PEStageConnPath,infc)
        #Append_management (inputs, target, {schema_type}, {field_mapping}, {subtype})
        arcpy.Append_management (infcPath, outfc)
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' APPEND:   {0} to {1}.\n'.format(infc,outfc)
        log.write(msg)
        print msg

        #Switch Env
        arcpy.env.workspace = GISpegisprodPath

        #Variables
        in1 = '{0}\{1}'.format(GISpegisprodPath,outfc)
        in2 = '{0}\{1}'.format(GISpegisprodPath,'pegisprod.GIS.INDUSTRY_WELLS')
        RigSched = 'RigSchedule'
        
        keyFields = 'uwi' + \
                    ';Id '
        
        inFields = 'uwi' + \
                ';Shape' + \
                ';Id' + \
                ';RigScheduleName' + \
                ';SubSiteName' + \
                ';EntityId' + \
                ';RigId' + \
                ';StartDate' + \
                ';EndDate' + \
                ';ActivityType' + \
                ';SegmentType'
        
        #Make Query Table
        #MakeQueryTable_management (in_table, out_table, in_key_field_option, {in_key_field}, {in_field}, {where_clause})
        arcpy.MakeQueryTable_management ('{0};{1}'.format(in1,in2), RigSched, "USE_KEY_FIELDS", keyFields, inFields,'pegisprod.STAGE.EPEX_RigActivityPlans.EntityId = pegisprod.GIS.INDUSTRY_WELLS.EPEX_ID AND pegisprod.STAGE.EPEX_RigActivityPlans.EndDate >getdate()')
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' CREATE:   Make Query Table Management created {0}.\n'.format('RigSched')
        log.write(msg)
        print msg
        
        #Point to Line
        #PointsToLine_management (Input_Features, Output_Feature_Class, {Line_Field}, {Sort_Field}, {Close_Line})
        arcpy.PointsToLine_management (RigSched, 'in_memory\\tempriglines', 'RigId', 'StartDate')
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' CREATE:   Points to Line created tempriglines.\n'
        log.write(msg)
        print msg

        #Tables
        infc = 'in_memory\\tempriglines'
        outfc ='pegisprod.GIS.EPEX_RigLines'

        #Count Records before Truncation
        ct = arcpy.GetCount_management(outfc)
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' COUNT:   {0} record count = {1}.\n'.format(outfc,str(ct))
        log.write(msg)
        print msg

        #Truncate
        #TruncateTable_management (in_table)
        arcpy.TruncateTable_management(outfc)
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' TRUNCATE:     {0}.\n'.format(outfc)
        log.write(msg)
        print msg

        #Append
        #Append_management (inputs, target, {schema_type}, {field_mapping}, {subtype})
        arcpy.Append_management (infc, outfc)
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' APPEND:  {0} to {1}.\n'.format(infc,outfc)
        log.write(msg)
        print msg

        #Count Records after Append
        ct = arcpy.GetCount_management(outfc)
        msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' COUNT:   {0} record count = {1}.\n'.format(outfc,str(ct))
        log.write(msg)
        print msg
    
        #Cleanup Connections
        arcpy.env.workspace = dataPath
        for i in arcpy.ListWorkspaces("*", "FileGDB"):
            arcpy.Delete_management(i)
            msg = str(datetime.datetime.today().strftime('%H:%M:%S')) + ' DELETE:   {0}.\n'.format(i)
            log.write(msg)
            print msg

        #Complete
        comp=True
        
    except Exception, e:
        #Log Errors
        msg = '\n' + str(datetime.datetime.today().strftime('%H:%M:%S')) + ' ERROR:    ' + str(e) + '\n'
        log.write(msg)
        print msg

        #Complete
        err = True
        comp = True


#Script Complete
if err == True:
    msg = '\n' + str(datetime.datetime.today().strftime('%H:%M:%S')) + ' COMPLETE:     Script complete with ERRORS!\n'
else:
    msg = '\n' + str(datetime.datetime.today().strftime('%H:%M:%S')) + ' COMPLETE:     Script complete with success.\n'
log.write(msg)
print msg
log.close()
