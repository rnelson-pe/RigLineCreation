

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


cwd = os.getcwd()

dataPath = cwd + r'\DATA'
if not os.path.isdir(dataPath):
    os.makedirs(dataPath)

logPath = cwd + r'\LOG'
if not os.path.isdir(logPath):
    os.makedirs(logPath)

x = 1
dt = str(datetime.datetime.today().strftime('%Y%m%d'))
logFile = r'{0}\{1}_{2}.txt'.format(logPath,'RigLineCreation_LOG',dt)
while os.path.isfile(logFile):
    logFile = r'{0}\{1}_{2}_{3}.txt'.format(logPath,'RigLineCreation_LOG',dt,str(x))
    x+=1

log = open(logFile,'w')
log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' RigLineCreation.py\n')
log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Executed By: '+os.environ.get("USERNAME")+'\n')
log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Date: '+str(datetime.datetime.today())+'\n\n')

err = False
comp = False
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
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' FileGeodatabase {0} Created.\n'.format(fgdb))
        
        ## Create ParlseyStage Data Connection
        PEStageConnName = r'ParsleyStage.sde'
        PEStageConnPath = r'{0}\{1}'.format(dataPath,PEStageConnName)
        if not os.path.isfile(PEStageConnPath):
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Connection {0} not found.\n'.format(PEStageConnPath))
            ##CreateDatabaseConnection_management (out_folder_path, out_name, database_platform, instance, {account_authentication}, {username}, {password}, {save_user_pass}, {database}, {schema}, {version_type}, {version}, {date})
            arcpy.CreateDatabaseConnection_management(dataPath,PEStageConnName,'SQL_SERVER','cubeprd-01','OPERATING_SYSTEM_AUTH','#','#','DO_NOT_SAVE_USERNAME','ParsleyStage')
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Connection {0} created.\n'.format(PEStageConnPath))
        else:
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Connection {0} exists.\n'.format(PEStageConnPath))

        ## Test for GIS pegistest Data Connection
        GISpegistest = r'GISpegistest.sde'
        GISpegistestPath = r'{0}\{1}'.format(dataPath,GISpegistest)
        if not os.path.isfile(GISpegistestPath):
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Error: Connection not found.  Exiting process.\n')
            err=True
        else:
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Connection {0} exists.\n'.format(GISpegistestPath))

        ## Test for STAGE pegistest Data Connection
        STAGEpegistest = r'STAGEpegistest.sde'
        STAGEpegistestPath = r'{0}\{1}'.format(dataPath,STAGEpegistest)
        if not os.path.isfile(STAGEpegistestPath):
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Error: Connection not found.  Exiting process.\n')
            err=True
        else:
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Connection {0} exists.\n'.format(STAGEpegistestPath))


        #Stage RigActivityPlans
        arcpy.env.workspace = STAGEpegistestPath
        
        #Tables
        infc = 'ParsleyStage.Epex.RigActivityPlans'
        outfc ='pegistest.STAGE.EPEX_RigActivityPlans'
        
        #Truncate
        #TruncateTable_management (in_table)
        arcpy.TruncateTable_management(outfc)
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Truncated.\n'.format(outfc))
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Truncated.\n'.format(outfc)
        
        #Append
        infc = 'ParsleyStage.Epex.RigActivityPlans'
        infcPath = '{0}\{1}'.format(PEStageConnPath,infc)
        #Append_management (inputs, target, {schema_type}, {field_mapping}, {subtype})
        arcpy.Append_management (infcPath, outfc)
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Appended to {1}.\n'.format(infc,outfc))
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Appended to {1}.\n'.format(infc,outfc)

        #Process


        arcpy.env.workspace = GISpegistestPath
        
        in1 = '{0}\{1}'.format(GISpegistestPath,outfc)
        in2 = '{0}\{1}'.format(GISpegistestPath,'pegistest.GIS.INDUSTRY_WELLS')
        RigSched = 'RigSchedule'
##        keyFields = 'pegistest.GIS.INDUSTRY_WELLS.uwi' + \
##                    ';pegistest.STAGE.EPEX_RigActivityPlans.Id '
        
        keyFields = 'uwi' + \
                    ';Id '
        
##        inFields = 'pegistest.GIS.INDUSTRY_WELLS.uwi' + \
##                ';pegistest.GIS.INDUSTRY_WELLS.Shape' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.Id' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.RigScheduleName' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.SubSiteName' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.EntityId' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.RigId' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.StartDate' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.EndDate' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.ActivityType' + \
##                ';pegistest.STAGE.EPEX_RigActivityPlans.SegmentType'


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
        arcpy.MakeQueryTable_management ('{0};{1}'.format(in1,in2), RigSched, "USE_KEY_FIELDS", keyFields, inFields,'pegistest.STAGE.EPEX_RigActivityPlans.EntityId = pegistest.GIS.INDUSTRY_WELLS.EPEX_ID AND pegistest.STAGE.EPEX_RigActivityPlans.EndDate >getdate()')
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Make Query Table Management Complete to {0}.\n'.format('RigSched'))
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Make Query Table Management Complete to {0}.\n'.format('RigSched')
        
        #TEST OUTPUT
        #FeatureClassToFeatureClass_conversion (in_features, out_path, out_name, {where_clause}, {field_mapping}, {config_keyword})
        #arcpy.FeatureClassToFeatureClass_conversion ('Test1', fgdbPath, 'Test')


        #Point to Line
        #PointsToLine_management (Input_Features, Output_Feature_Class, {Line_Field}, {Sort_Field}, {Close_Line})
        arcpy.PointsToLine_management (RigSched, 'in_memory\\tempriglines', 'RigId', 'StartDate')
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Points to Line Complete.\n')
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Points to Line Complete.\n'

        #one time
        #arcpy.FeatureClassToFeatureClass_conversion ('in_memory\\tempriglines',GISpegistestPath,'EPEX_RigLines')

        infc = 'in_memory\\tempriglines'
        outfc ='pegistest.GIS.EPEX_RigLines'
        #Truncate
        #TruncateTable_management (in_table)
        arcpy.TruncateTable_management(outfc)
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Truncated.\n'.format(outfc))
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Truncated.\n'.format(outfc)

        #Append
        #Append_management (inputs, target, {schema_type}, {field_mapping}, {subtype})
        arcpy.Append_management (infc, outfc)
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Appended to {1}.\n'.format(infc,outfc))
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Appended to {1}.\n'.format(infc,outfc)

    
        #Lines

        #Truncate

        #Load

        #arcpy.env.workspace = GISConnPath
        #TableToTable_conversion (in_rows, out_path, out_name, {where_clause}, {field_mapping}, {config_keyword})
        #arcpy.TableToTable_conversion('pegistst.GIS.INDUSTRY_WELLS',dataPath + '\\' + fgdb,'INDUSTRY_WELLS')

##        infield= 'pegistest.GIS.INDUSTRY_WELLS.uwi'+\
##                ';pegistest.GIS.INDUSTRY_WELLS.Shape'+\
##                ';EpexTest.Id'+\
##                ';EpexTest.RigScheduleName'+\
##                ';EpexTest.SubSiteName'+\
##                ';EpexTest.EntityId'+\
##                ';EpexTest.RigId'+\
##                ';EpexTest.StartDate'+\
##                ';EpexTest.EndDate'+\
##                ';EpexTest.ActivityType'+\
##                ';EpexTest.SegmentType'
##
##        #MakeQueryTable_management (in_table, out_table, in_key_field_option, {in_key_field}, {in_field}, {where_clause})
##        arcpy.MakeQueryTable_management (['EpexTest',GISConnPath + '\\pegistest.GIS.INDUSTRY_WELLS'], 'RigSchedule', "USE_KEY_FIELDS", "pegisprod.GIS.INDUSTRY_WELLS.uwi;EpexTest.Id",infield, 'EpexTest.EntityId = pegisprod.GIS.INDUSTRY_WELLS.EPEX_ID')
##
##        arcpy.MakeQueryTable_management("
##                                        'Database Connections\\GIS NAME - Production Server.sde\\pegisprod.GIS.INDUSTRY_WELLS'
##                                        ;'Database Connections\\GIS NAME - Production Server.sde\\pegisprod.GIS.TEST_EPEX_RigActivityPlans'"
##                                        , RigSchedule
##                                        , "USE_KEY_FIELDS"
##                                        , "pegisprod.GIS.INDUSTRY_WELLS.uwi;pegisprod.GIS.TEST_EPEX_RigActivityPlans.Id"
##                                        , CHECK_UWI___Shape_from_INDUSTRY_WELLS__ALL_from_RigActivityPlans
##                                        , "")



    
        
        arcpy.env.workspace = dataPath
        for i in arcpy.ListWorkspaces("*", "FileGDB"):
            arcpy.Delete_management(i)
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Deleted.\n'.format(i))
            print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Deleted.\n'.format(i)

        comp=True
    except Exception, e:
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Error: ' + str(e) + '\n'
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Error: ' + str(e) + '\n')
        comp = True


#clean up
    try:
        arcpy.env.workspace = dataPath
        for i in arcpy.ListWorkspaces("*", "FileGDB"):
            arcpy.Delete_management(i)
            log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Deleted.\n'.format(i))
            print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' {0} Deleted.\n'.format(i)

    except Exception, e:
        print str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Error: ' + str(e) + '\n'
        log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Error: ' + str(e) + '\n')


log.write(str(datetime.datetime.today().strftime('%H:%M:%S')) + ' Script complete.\n')
log.close()
